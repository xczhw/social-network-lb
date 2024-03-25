#pragma once

#include <iostream>
#include <vector>
#include <fstream>
#include <sstream>

#include <fcntl.h>

#include <errno.h>
#include <unistd.h>

#include "../path_definitions.h"
#include "../utils.h"

std::vector<std::string>* safe_read(std::string file_name) {
    // 确保文件存在，没有则等待5秒钟
    while (access(file_name.c_str(), F_OK) == -1) {
        std::cout << "File " << file_name << " does not exist, waiting for 5 seconds" << std::endl;
        sleep(5);
    }

    int fd = open(file_name.c_str(), O_RDONLY);
    if (fd < 0) {
        std::cerr << "C++: Failed to open file" << std::endl;
        return new std::vector<std::string>();
    }

    // 准备共享锁结构
    struct flock fl;
    fl.l_type = F_RDLCK; // 请求一个共享锁
    fl.l_whence = SEEK_SET;
    fl.l_start = 0;  // 从文件开头开始
    fl.l_len = 0;    // 锁定整个文件

    while (true) {
        // 尝试获取共享锁
        if (fcntl(fd, F_SETLK, &fl) == -1) {
            if (errno == EACCES || errno == EAGAIN) {
                // 如果文件已被排他锁锁定，则输出信息并等待一秒
                // std::cerr << "C++: File is locked by another process (exclusive lock), retrying in 1 second..." << std::endl;
                sleep(1); // 等待一秒
            } else {
                // 如果是其他错误，则输出错误信息并退出
                // std::cerr << "C++: Failed to acquire shared lock due to an error" << std::endl;
                close(fd); // 关闭文件描述符
                return new std::vector<std::string>();
            }
        } else {
            // 成功获取共享锁
            // std::cout << "C++: Successfully acquired shared lock, file can now be safely read" << std::endl;
            break; // 跳出循环
        }
    }
    std::vector<std::string> *ips = new std::vector<std::string>();
    std::ifstream file(file_name);
    std::string ip;

    while (file >> ip) {
        ips->push_back(ip);
    }
    file.close();

    fl.l_type = F_UNLCK;
    fcntl(fd, F_SETLK, &fl);

    close(fd);

    return ips;
}

// TODO：改为检查文件 pod_ips.txt 的最后修改时间，并且仅当这个时间晚于上次更新的时间时，它才会读取文件（考虑是否有必要）
std::vector<std::string>* get_ips(std::string svc) {
    std::vector<std::string> *ips = safe_read("/share/data/" + svc + "/pod_ips.txt");
    return ips;
}

void write_send_to_log(std::string svc, std::string send_to_log)
{
  std::string filename = paths::LOGPATH + svc + "/send_to_log.txt";
  // add to filename
  std::ofstream outfile(filename, std::ios_base::app);
  // time, send_to
  outfile << get_timestamp() << " " << send_to_log << std::endl;
  outfile.close();
}
