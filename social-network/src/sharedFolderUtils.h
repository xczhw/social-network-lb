#pragma once

#include <iostream>
#include <vector>
#include <mutex>
#include <condition_variable>
#include <cstdlib>
#include <deque>
#include <chrono>
#include <map>
#include <fstream>
#include <string>

#include "utils.h"
#include "path_definitions.h"

namespace social_network {

using std::chrono::milliseconds;
using std::chrono::duration_cast;
using std::chrono::system_clock;

void safe_write(std::string filename, std::string content)
{
  // TODO: add lock
}

void create_if_not_exists(const std::string &folder_path) {
  if (access(folder_path.c_str(), F_OK) != -1) {
    return;
  }
  std::string command = "mkdir -p " + folder_path;
  int ret = system(command.c_str());
  if (ret != 0) {
    LOG(error) << "Failed to create folder " << folder_path;
  }
}

// 记录每次请求发送到哪个ip
void write_send_to(std::string svc, std::string send_to)
{
  social_network::create_if_not_exists(paths::LOGPATH + svc);
  LOG(info) << "write_send_to " << svc << " " << send_to;
  std::string filename = paths::LOGPATH + svc + "/send_to.txt";
  // add to filename
  std::ofstream outfile(filename, std::ios_base::app);
  // time, send_to
  outfile << get_timestamp() << " " << send_to << std::endl;
  outfile.close();
}

void write_send_to_log(std::string svc, std::string send_to_log)
{
  social_network::create_if_not_exists(paths::LOGPATH + svc);
  std::string filename = paths::LOGPATH + svc + "/send_to_log.txt";
  // add to filename
  std::ofstream outfile(filename, std::ios_base::app);
  // time, send_to
  outfile << get_timestamp() << " " << send_to_log << std::endl;
  outfile.close();
}

// 记录每次请求的延时
void write_latency(std::string svc, std::string ip, int64_t latency)
{
  social_network::create_if_not_exists(paths::LOGPATH + svc);
  std::string filename = paths::LOGPATH + svc + "/latency.txt";
  // add to filename
  std::ofstream outfile(filename, std::ios_base::app);
  // time, latency
  outfile << std::to_string(std::chrono::duration_cast<std::chrono::milliseconds>(
    std::chrono::system_clock::now().time_since_epoch()).count() - CUSTOM_EPOCH) << " " 
    << ip << " " << latency << std::endl;
  outfile.close();
}

void write_algorithm_latency(std::string svc, std::string ip, int64_t latency, int64_t algorithm_time)
{
  social_network::create_if_not_exists(paths::LOGPATH + svc);
  std::string filename = paths::LOGPATH + svc + "/algorithm_latency.txt";
  // add to filename
  std::ofstream outfile(filename, std::ios_base::app);
  // time, latency
  outfile << std::to_string(std::chrono::duration_cast<std::chrono::milliseconds>(
    std::chrono::system_clock::now().time_since_epoch()).count() - CUSTOM_EPOCH) << " " 
    << ip << " " << latency << " " << algorithm_time << algorithm_time / latency * 100 << '%' << std::endl;
  outfile.close();
}

void write_queue_size(std::string svc, std::map<std::string, int> &curr_pool_size_map, std::map<std::string, std::deque<std::string> *> &pool_map)
{
  social_network::create_if_not_exists(paths::LOGPATH + svc);
  std::string filename = paths::LOGPATH + svc + "/queue_size.txt";
  // add to filename
  std::ofstream outfile(filename, std::ios_base::app);
  // time, queue_size
  outfile << std::to_string(std::chrono::duration_cast<std::chrono::milliseconds>(
    std::chrono::system_clock::now().time_since_epoch()).count() - CUSTOM_EPOCH) << " ";
  for (auto &kv : curr_pool_size_map) {
    outfile << kv.first << " " << kv.second << " " << pool_map[kv.first]->size() << " ";
  }
  outfile << std::endl;
  outfile.close();

} 
}//namespace social_network