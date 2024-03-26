#pragma once

#include <string>
#include <fstream>
#include <iostream>
#include <chrono>
#include <nlohmann/json.hpp>

#include "logger.h"
// Custom Epoch (January 1, 2018 Midnight GMT = 2018-01-01T00:00:00Z)
#define CUSTOM_EPOCH 1514764800000

namespace social_network{

using json = nlohmann::json;
using std::chrono::milliseconds;
using std::chrono::duration_cast;
using std::chrono::system_clock;


int load_config_file(const std::string &file_name, json *config_json) {
  std::ifstream json_file;
  json_file.open(file_name);
  if (json_file.is_open()) {
    json_file >> *config_json;
    json_file.close();
    return 0;
  }
  else {
    LOG(error) << "Cannot open service-config.json";
    return -1;
  }
};

int64_t get_timestamp() {
  return duration_cast<milliseconds>(
      system_clock::now().time_since_epoch()).count() - CUSTOM_EPOCH;
}

} //namespace social_network

