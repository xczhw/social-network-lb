#pragma once

#include <vector>
#include <mutex>
#include <condition_variable>
#include <cstdlib>
#include <deque>
#include <map>
#include <string>
#include <iostream>

#include "logger.h"
#include "sharedFolderUtils.h"
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
  std::map<std::string, std::deque<TClient *> *> _pool_map;
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

  for (int i = 0; i < min_pool_size; ++i) {
    TClient *client = new TClient(addr, port, _keep_alive);
    std::string ip = client->GetIp();
    if (_pool_map.find(ip) == _pool_map.end()) {
      _pool_map[ip] = new std::deque<TClient *>();
      std::cout << "<ClientPool> Create new pool for ip: " << ip << "\n";
    }
    _pool_map[ip]->push_back(client);
  }

  _curr_pool_size = min_pool_size;
}

template<class TClient>
ClientPool<TClient>::~ClientPool() {
    for (auto &kv : _pool_map) {
    while (!kv.second->empty()) {
      delete kv.second->front();
      kv.second->pop_front();
    }
    delete kv.second;
  }
}

// 从队列中取出并记录一个client的conn
template<class TClient>
TClient * ClientPool<TClient>::Pop() {
  TClient * client = nullptr;
  int64_t start = get_timestamp();
  std::cout << "Pop(): algorithm start = " << start << std::endl;
  std::string ip = _algorithm->execute();
  int64_t end = get_timestamp();
  std::cout << "Pop(): algorithm end = " << end << " ip: " << ip << std::endl;
  
  client = GetClientFromPool(ip);
  if (!client) // 如果取出失败,则创建一个新的client
  {
    std::cout << "Pop(): ProduceClient" << std::endl;
    client = ProduceClient(ip);
  }
  if (client) {
    // client->algorithm_time = algorithm_time;
    // client->pop_time = get_timestamp();
    try {
      client->Connect();
      std::cout << "Pop(): Connect Success" << std::endl;
    } catch (...) {
      LOG(error) << "Failed to connect " + _client_type;
      std::string ip = client->GetIp();
      if (_pool_map.find(ip) == _pool_map.end()) {
        _pool_map[ip] = new std::deque<TClient *>();
      }
      _pool_map[ip]->push_back(client);
      throw;
    }
  }
  write_send_to(_addr, ip);
  return client;
}

// 将client放回队列
template<class TClient>
void ClientPool<TClient>::Push(TClient *item) {
  // 如果是通过算法取出的client,则记录延时
  std::unique_lock<std::mutex> cv_lock(_mtx);
  std::string ip = item->GetIp();
  if (_pool_map.find(ip) == _pool_map.end()) {
    _pool_map[ip] = new std::deque<TClient *>();
  }
  _pool_map[ip]->push_back(item);
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
  if (_pool_map.find(ip) == _pool_map.end()) {
    _pool_map[ip] = new std::deque<TClient *>();
    std::cout << "<GetClientFromPool> Create new pool for ip: " << ip << "\n";
  }
  std::deque<TClient *> *_pool = _pool_map[ip];
  if (!_pool->empty()) { // 如果队列不为空,则取出一个client
    LOG(info) << "GetClientFromPool: " << _client_type << "pool_size = " << _pool->size() << " " << ip;
    client = _pool->front();
    _pool->pop_front();
  } else if (_curr_pool_size == _max_pool_size) { 
    // 如果队列为空,且当前连接数已经达到最大连接数,则等待
    auto wait_time = std::chrono::system_clock::now() +
        std::chrono::milliseconds(_timeout_ms);
    bool wait_success = _cv.wait_until(cv_lock, wait_time,
        [this, ip] { return _pool_map[ip]->size() > 0; });
    if (!wait_success) {
      LOG(warning) << "ClientPool pop timeout";
      cv_lock.unlock();
      return nullptr;
    }
    client = _pool->front();
    _pool->pop_front();
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
