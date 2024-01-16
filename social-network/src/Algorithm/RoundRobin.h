#ifndef ROUNDROBIN_H
#define ROUNDROBIN_H

#include <iostream>
#include "IAlgorithm.h"
#include "AlgoUtils.h"

class RoundRobin : public IAlgorithm
{
public:
    RoundRobin(std::string svc);
    ~RoundRobin() = default;
    std::string execute() override
    {
        std::cout << "RoundRobin execute" << std::endl;
        std::string ip = ips[index];
        index = (index + 1) % ips.size();
        return ip;
    }
private:
    int index = 0;
};

RoundRobin::RoundRobin(std::string svc)
{
    std::cout << "RoundRobin constructor" << std::endl;
    this->svc = svc;
    this->ips = get_ips(svc);
    this->index = 0;
}



#endif //ROUNDROBIN_H