#pragma once

#include <iostream>
#include <sstream>
#include <map>
#include "IAlgorithm.h"
#include "AlgoUtils.h"

class Pick2 : public IAlgorithm
{
public:
    Pick2(std::string svc);
    ~Pick2() = default;
    void update() override;
    std::string execute() override;
private:
    std::map<std::string, std::string> *ip_to_status;
    void read_ip_status();
};

Pick2::Pick2(std::string svc)
{
    std::cout << "Pick2 constructor" << std::endl;
    this->svc = svc;
    this->ip_to_status = new std::map<std::string, std::string>();
    this->update();
}

void Pick2::update()
{
    std::cout << "Pick2 update" << std::endl;
    this->ips = get_ips(svc);
    for (auto ip : *ips)
        ip_to_status -> insert({ip, "0"});
    read_ip_status();
}


void Pick2::read_ip_status()
{
    std::ifstream infile("/share/data/" + svc + "/cpu_usage.txt");

    std::string line;
    while (std::getline(infile, line))
    {
        std::istringstream iss(line);
        std::string ip;
        int status;
        if (!(iss >> ip >> status)) { break; } // error
        ip_to_status -> at(ip) = std::to_string(status);
    }
}

std::string Pick2::execute()
{
    this->update();
    std::cout << "Pick2 execute" << std::endl;
    int idx1 = rand() % ips->size();
    int idx2 = rand() % ips->size();
    std::string ip1 = ips->at(idx1); 
    std::string ip2 = ips->at(idx2);
    double statu1 = std::stod(ip_to_status -> at(ip1)); 
    double statu2 = std::stod(ip_to_status -> at(ip2));
    std::string ip = statu1 < statu2 ? ip1 : ip2;
    
    std::stringstream ss;
    ss << ip1 << ": " << statu1 << " " << ip2 << ": " << statu2 << " chose " << ip;
    write_send_to_log(svc, ss.str());
    std::cout << "Pick2 execute " << ip << std::endl;
    
    return ip;
}
