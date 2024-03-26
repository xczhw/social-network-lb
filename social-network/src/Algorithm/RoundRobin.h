#pragma once

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
        // return svc;
        if (ips->empty())
            return svc;
        index = std::min(index, (int)ips->size() - 1);
        std::string ip = ips -> at(index);
        // LOG(info) << "RoundRobin execute " << ip << std::endl;
        index = (index + 1) % ips->size();

        std::stringstream ss;
        ss << "RoundRobin execute " << ip << " index: " << index << " ips size: " << ips->size();
        write_send_to_log(svc, ss.str());
        return ip;
    }
private:
    int index = 0;
};

RoundRobin::RoundRobin(std::string svc)
{
    // std::cout << "RoundRobin constructor" << std::endl;
    this->svc = svc;
    this->ips = get_ips(svc);
    this->index = 0;
}

void RoundRobin::update()
{
    // std::cout << "RoundRobin update" << std::endl;
    this->ips = get_ips(svc);
}
