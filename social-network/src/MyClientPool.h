#pragma once

#include <vector>
#include <mutex>
#include <condition_variable>
#include <cstdlib>
#include <deque>
#include <chrono>
#include <map>
#include <string>
#include <iostream>

#include "logger.h"
#include "sharedFolderUtils.h"
#include "Algorithm/AlgorithmFactory.h"
#include "Algorithm/IAlgorithm.h"

// Custom Epoch (January 1, 2018 Midnight GMT = 2018-01-01T00:00:00Z)
#define CUSTOM_EPOCH 1514764800000

namespace social_network {

using std::chrono::milliseconds;
using std::chrono::duration_cast;
using std::chrono::system_clock;

template<class TClient>
class ClientPool {
  class PoolItem {
   public:
    PoolItem(TClient *client) {
      _client = client;
      algorithm_time = -1;
      pop_time = -1;
    }
    TClient * GetClient() { return _client; }
    int64_t algorithm_time;
    int64_t pop_time;
   private:
    TClient * _client;
  };
public:
  ClientPool(const std::string &client_type, const std::string &addr,
      int port, int min_size, int max_size, int timeout_ms, int keep_alive=0);
  ~ClientPool();

  ClientPool(const ClientPool&) = delete;
  ClientPool& operator=(const ClientPool&) = delete;
  ClientPool(ClientPool&&) = default;
  ClientPool& operator=(ClientPool&&) = default;

  PoolItem * Pop();
  void Push(PoolItem *);
  void Remove(PoolItem *);

private:
  std::map<std::string, std::deque<PoolItem *> > _pool_map;
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

  PoolItem * GetClientFromPool(std::string ip);
  PoolItem * ProduceClient(std::string ip);

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
    _pool_map[ip] = std::deque<PoolItem *>();
  }

  // 创建最小连接数的连接,每个ip均匀分布
  while (conn_num < min_pool_size) {
    for (auto &ip : _ip_list) {
      TClient *client = new TClient(ip, port, _keep_alive);
      _pool_map[ip].push_back(new PoolItem(client));
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

// 从队列中取出并记录一个client的conn
template<class TClient>
typename ClientPool<TClient>::PoolItem * ClientPool<TClient>::Pop() {
  PoolItem * client = nullptr;
  time_t start = time(nullptr); // TODO: 是否合理?
  std::cout << "Pop(): algorithm start = " << start << std::endl;
  std::string ip = _algorithm->execute();
  time_t end = time(nullptr);
  std::cout << "Pop(): algorithm end = " << end << " ip: " << ip << std::endl;
  int64_t algorithm_time = end - start;
  client = GetClientFromPool(ip);
  if (!client) // 如果取出失败,则创建一个新的client
  {
    client = ProduceClient(ip);
    std::cout << "Pop(): ProduceClient" << std::endl;
  }
  if (client && client->GetClient()) {
    client->algorithm_time = algorithm_time;
    client->pop_time = duration_cast<milliseconds>(
        system_clock::now().time_since_epoch()).count() - CUSTOM_EPOCH;
    try {
      client->GetClient()->Connect();
      std::cout << "Pop(): Connect Success" << std::endl;
    } catch (...) {
      LOG(error) << "Failed to connect " + _client_type;

      _pool_map[client->GetClient()->GetIp()].push_back(client);
      throw;
    }
  }
  write_send_to(_addr, ip);
  return client;
}

// 将client放回队列
template<class TClient>
void ClientPool<TClient>::Push(typename ClientPool<TClient>::PoolItem *item) {
  // 如果是通过算法取出的client,则记录延时
  if (item->pop_time > 0) {
    int64_t now = duration_cast<milliseconds>(
        system_clock::now().time_since_epoch()).count() - CUSTOM_EPOCH;
    int64_t latency = now - item->pop_time;
    write_latency(_addr, item->GetClient()->GetIp(), latency);
    if (item->algorithm_time > 0) {
      write_algorithm_latency(_addr, item->GetClient()->GetIp(), latency, item->algorithm_time);
    }
    item->algorithm_time = item->pop_time = -1;
  }
  std::unique_lock<std::mutex> cv_lock(_mtx);
  _pool_map[item->GetClient()->GetIp()].push_back(item);
  cv_lock.unlock();
  _cv.notify_one();
}

// 从队列中删除一个client
template<class TClient>
void ClientPool<TClient>::Remove(typename ClientPool<TClient>::PoolItem *client) {
  std::unique_lock<std::mutex> lock(_mtx);
  delete client;
  client = nullptr;
  _curr_pool_size--;
  lock.unlock();
}

// 从队列中取出一个client
template<class TClient>
typename ClientPool<TClient>::PoolItem * ClientPool<TClient>::GetClientFromPool(std::string ip) {
  std::unique_lock<std::mutex> cv_lock(_mtx);
  PoolItem * client = nullptr;
  std::deque<PoolItem *> _pool = _pool_map[ip];
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
  if (client && !client->GetClient()->IsAlive()) {
    delete client;
    client = nullptr;
    _curr_pool_size--;
  }
  cv_lock.unlock();
  return client;
}

template<class TClient>
typename ClientPool<TClient>::PoolItem * ClientPool<TClient>::ProduceClient(std::string ip) {
  std::unique_lock<std::mutex> lock(_mtx);
  TClient * client = nullptr;
  if (_curr_pool_size < _max_pool_size) {
    try {
      client = new TClient(ip, _port, _keep_alive);
      _curr_pool_size++;
      LOG(warning) << "ClientPool size " << _curr_pool_size << " " << _client_type;
      lock.unlock();
      return new PoolItem(client);
    } catch (...) {
      lock.unlock();
      return nullptr;
    }
  }
}

} // namespace social_network
