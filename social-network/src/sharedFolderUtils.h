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

// Custom Epoch (January 1, 2018 Midnight GMT = 2018-01-01T00:00:00Z)
#define CUSTOM_EPOCH 1514764800000

namespace social_network {

using std::chrono::milliseconds;
using std::chrono::duration_cast;
using std::chrono::system_clock;

void safe_write(std::string filename, std::string content)
{
  // TODO: add lock
}

// 记录每次请求发送到哪个ip
void write_send_to(std::string svc, std::string send_to)
{
  std::string filename = "/share/data/" + svc + "/send_to.txt";
  // add to filename
  std::ofstream outfile(filename, std::ios_base::app);
  // time, send_to
  outfile << get_timestamp() << " " << send_to << std::endl;
  outfile.close();
}

// 记录每次请求的延时
void write_latency(std::string svc, std::string ip, int64_t latency)
{
  std::string filename = "/share/data/" + svc + "/latency.txt";
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
  std::string filename = "/share/data/" + svc + "/algorithm_latency.txt";
  // add to filename
  std::ofstream outfile(filename, std::ios_base::app);
  // time, latency
  outfile << std::to_string(std::chrono::duration_cast<std::chrono::milliseconds>(
    std::chrono::system_clock::now().time_since_epoch()).count() - CUSTOM_EPOCH) << " " 
    << ip << " " << latency << " " << algorithm_time << algorithm_time / latency * 100 << '%' << std::endl;
  outfile.close();
}

} //namespace social_network