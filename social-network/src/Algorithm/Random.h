#ifndef RANDOM_H
#define RANDOM_H

#include <iostream>
#include "IAlgorithm.h"
#include "AlgoUtils.h"

class Random : public IAlgorithm
{
public:
    Random(std::string svc);
    ~Random() = default;
    void update() override;
    std::string execute() override
    {
        int index = rand() % ips->size();
        std::string ip = ips->at(index);
        std::cout << "Random execute " << ip << std::endl;
        return ip;
    }
};

Random::Random(std::string svc)
{
    std::cout << "Random constructor" << std::endl;
    this->svc = svc;
    this->ips = get_ips(svc);
}

void Random::update()
{
    std::cout << "Random update" << std::endl;
    this->ips = get_ips(svc);
}

#endif //Random_H