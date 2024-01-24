#ifndef SOCIAL_NETWORK_MICROSERVICES_CLIENTPOOL_H
#define SOCIAL_NETWORK_MICROSERVICES_CLIENTPOOL_H

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
  _algorithm = AlgorithmFactory::GetAlgorithm(algo, addr);
  _ip_list = get_ips(addr);

  int conn_num = 0;
  for (auto &ip : _ip_list) {
    _pool_map[ip] = std::deque<TClient *>();
    _pools.push_back(_pool_map[ip]);
  }

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

template<class TClient>
TClient * ClientPool<TClient>::Pop() {
  TClient * client = nullptr;
  std::string ip = _algorithm->execute();
  client = GetClientFromPool(ip);
  if (!client)
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

template<class TClient>
void ClientPool<TClient>::Push(TClient *client) {
  std::unique_lock<std::mutex> cv_lock(_mtx);
  _pool_map[client->GetIp()].push_back(client);
  cv_lock.unlock();
  _cv.notify_one();
}

template<class TClient>
void ClientPool<TClient>::Remove(TClient *client) {
  std::unique_lock<std::mutex> lock(_mtx);
  delete client;
  client = nullptr;
  _curr_pool_size--;
  lock.unlock();
}

template<class TClient>
TClient * ClientPool<TClient>::GetClientFromPool(std::string ip) {
  std::unique_lock<std::mutex> cv_lock(_mtx);
  TClient * client = nullptr;
  std::deque<TClient *> _pool = _pool_map[ip];
  if (!_pool.empty()) {
    client = _pool.front();
    _pool.pop_front();
  } else if (_curr_pool_size == _max_pool_size) {
    auto wait_time = std::chrono::system_clock::now() +
        std::chrono::milliseconds(_timeout_ms);
    bool wait_success = _cv.wait_until(cv_lock, wait_time,
        [_pool] { return _pool.size() > 0; });
    if (!wait_success) {
      LOG(warning) << "ClientPool pop timeout";
      cv_lock.unlock();
      _pools.push_back(_pool);
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

#endif //SOCIAL_NETWORK_MICROSERVICES_CLIENTPOOL_H
