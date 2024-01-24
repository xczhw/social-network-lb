#ifndef ROUNDROBIN_H
#define ROUNDROBIN_H

#include <iostream>
#include "IAlgorithm.h"
#include "AlgoUtils.h"

class RoundRobin : public IAlgorithm
{
public:
    RoundRobin(std::string svc);
    void update() override;
    ~RoundRobin() = default;
    std::string execute() override
    {
        update();
        index = std::min(index, (int)ips.size() - 1);
        std::string ip = ips[index];
        std::cout << "RoundRobin execute " << ip << std::endl;
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

void RoundRobin::update()
{
    std::cout << "RoundRobin update" << std::endl;
    this->ips = get_ips(svc);
}



#endif //ROUNDROBIN_H