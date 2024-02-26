#pragma once

#include <vector>
#include <mutex>
#include <condition_variable>
#include <cstdlib>
#include <deque>
#include <chrono>
#include <map>
#include <string>

#include "logger.h"
#include "Algorithm/AlgorithmFactory.h"
#include "Algorithm/IAlgorithm.h"


namespace social_network {

template<class TClient>
class ClientPool {
public:
  ClientPool(const std::string &client_type, const std::string &addr,
      int port, int min_size, int max_size, int timeout_ms, int keep_alive=0);
  ~ClientPool();

  ClientPool(const ClientPool&) = delete;
  ClientPool& operator=(const ClientPool&) = delete;
  ClientPool(ClientPool&&) = default;
  ClientPool& operator=(ClientPool&&) = default;

  TClient * Pop();
  void Push(TClient *);
  void Remove(TClient *);

private:
  std::map<std::string, std::deque<TClient *> > _pool_map;
  std::vector<std::string> _ip_list;
  std::string _addr;
  std::string _client_type;
  int _port;
  int _min_pool_size{};
  int _max_pool_size{};
  int _curr_pool_size{};
  int _timeout_ms;
  int _keep_alive;
  std::mutex _mtx;
  std::condition_variable _cv;
  IAlgorithm * _algorithm;

  TClient * GetClientFromPool(std::string ip);
  TClient * ProduceClient(std::string ip);

};

template<class TClient>
ClientPool<TClient>::ClientPool(const std::string &client_type,
    const std::string &addr, int port, int min_pool_size,
    int max_pool_size, int timeout_ms, int keep_alive) {
  _addr = addr;
  _port = port;
  _min_pool_size = min_pool_size;
  _max_pool_size = max_pool_size;
  _timeout_ms = timeout_ms;
  _keep_alive = keep_alive;
  _client_type = client_type;
  std::string algo = std::getenv("ALGORITHM");
  _algorithm = AlgorithmFactory::createAlgorithm(algo, addr);
  _ip_list = get_ips(addr);

  // 为每个ip创建一个队列
  int conn_num = 0;
  for (auto &ip : _ip_list) {
    _pool_map[ip] = std::deque<TClient *>();
  }

  // 创建最小连接数的连接,每个ip均匀分布
  while (conn_num < min_pool_size) {
    for (auto &ip : _ip_list) {
      TClient *client = new TClient(ip, port, _keep_alive);
      _pool_map[ip].push_back(client);
      conn_num++;
      if (conn_num >= min_pool_size)
        break;
    }
  }
  _curr_pool_size = conn_num;
}

template<class TClient>
ClientPool<TClient>::~ClientPool() {
  for (auto &kv : _pool_map) {
    while (!kv.second.empty()) {
      delete kv.second.front();
      kv.second.pop_front();
    }
  }
}

// 记录每次请求发送到哪个ip
void write_send_to(std::string svc, std::string send_to)
{
  std::string filename = "/share/data/" + svc + "/send_to.txt";
  // add to filename
  std::ofstream outfile(filename, std::ios_base::app);
  // time, send_to
  outfile << std::to_string(std::chrono::duration_cast<std::chrono::milliseconds>(
    std::chrono::system_clock::now().time_since_epoch()).count()) << " " 
    << send_to << std::endl;
  outfile.close();
}

// 从队列中取出一个client的conn
template<class TClient>
TClient * ClientPool<TClient>::Pop() {
  TClient * client = nullptr;
  std::string ip = _algorithm->execute();
  client = GetClientFromPool(ip);
  if (!client) // 如果取出失败,则创建一个新的client
    client = ProduceClient(ip);
  if (client) {
    try {
      client->Connect();
    } catch (...) {
      LOG(error) << "Failed to connect " + _client_type;

      _pool_map[client->GetIp()].push_back(client); // 改为ClientPool->Push
      throw;
    }
  }
  write_send_to(_addr, ip);
  return client;
}

// 将client放回队列
template<class TClient>
void ClientPool<TClient>::Push(TClient *client) {
  std::unique_lock<std::mutex> cv_lock(_mtx);
  _pool_map[client->GetIp()].push_back(client);
  cv_lock.unlock();
  _cv.notify_one();
}

// 从队列中删除一个client
template<class TClient>
void ClientPool<TClient>::Remove(TClient *client) {
  std::unique_lock<std::mutex> lock(_mtx);
  delete client;
  client = nullptr;
  _curr_pool_size--;
  lock.unlock();
}

// 从队列中取出一个client
template<class TClient>
TClient * ClientPool<TClient>::GetClientFromPool(std::string ip) {
  std::unique_lock<std::mutex> cv_lock(_mtx);
  TClient * client = nullptr;
  std::deque<TClient *> _pool = _pool_map[ip];
  if (!_pool.empty()) { // 如果队列不为空,则取出一个client
    client = _pool.front();
    _pool.pop_front();
  } else if (_curr_pool_size == _max_pool_size) { 
    // 如果队列为空,且当前连接数已经达到最大连接数,则等待
    auto wait_time = std::chrono::system_clock::now() +
        std::chrono::milliseconds(_timeout_ms);
    bool wait_success = _cv.wait_until(cv_lock, wait_time,
        [_pool] { return _pool.size() > 0; });
    if (!wait_success) {
      LOG(warning) << "ClientPool pop timeout";
      cv_lock.unlock();
      return nullptr;
    }
    client = _pool.front();
    _pool.pop_front();
  }
  if (client && !client->IsAlive()) {
    delete client;
    client = nullptr;
    _curr_pool_size--;
  }
  cv_lock.unlock();
  return client;
}

template<class TClient>
TClient * ClientPool<TClient>::ProduceClient(std::string ip) {
  std::unique_lock<std::mutex> lock(_mtx);
  TClient * client = nullptr;
  if (_curr_pool_size < _max_pool_size) {
    try {
      client = new TClient(ip, _port, _keep_alive);
      _curr_pool_size++;
      LOG(warning) << "ClientPool size " << _curr_pool_size << " " << _client_type;
      lock.unlock();
      return client;
    } catch (...) {
      lock.unlock();
      return nullptr;
    }
  }
}

} // namespace social_network
