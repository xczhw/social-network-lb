#ifndef ALGOUTILS_H
#define ALGOUTILS_H

#include <iostream>
#include <vector>

#include <fstream>

#include <unistd.h>

std::vector<std::string> safe_read(std::string file_name) {
    // open the file
    // while the file isnot exist, wait for 5 seconds and try again
    std::ifstream infile = std::ifstream(file_name);
    while (!infile) {
        std::cout << "Waiting for the " << file_name << " file" << std::endl;
        sleep(5);
        infile.open(file_name);
    }
    std::vector<std::string> lines;
    std::string line;
    while (infile >> line) {
        lines.push_back(line);
    }
    infile.close();
    return lines;
}

// TODO：改为检查文件 pod_ips.txt 的最后修改时间，并且仅当这个时间晚于上次更新的时间时，它才会读取文件（考虑是否有必要）
std::vector<std::string> get_ips(std::string svc) {
    std::vector<std::string> ips = safe_read("/share/data/" + svc + "/pod_ips.txt");
    return ips;
}


#endif // ALGOUTILS_H