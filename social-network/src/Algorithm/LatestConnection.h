#ifndef LATESTCONNECTION_H
#define LATESTCONNECTION_H

#include <iostream>
#include <string>

#include "IAlgorithm.h"
#include "AlgoUtils.h"

class LatestConnection : public IAlgorithm
{
public:
    LatestConnection(std::string svc);
    ~LatestConnection() = default;
    std::string execute() override
    {
        std::cout << " execute" << std::endl;
        if (index == -1)
            index = rand() % ips->size();
        std::string ip = ips->at(index);
        return ip;
    }
private:
    int index = -1;
};

LatestConnection::LatestConnection(std::string svc)
{
    std::cout << "LatestConnection constructor" << std::endl;
    this->svc = svc;
    this->ips = get_ips(svc);
    this->index = 0;
}