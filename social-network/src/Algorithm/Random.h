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
    std::string execute() override
    {
        std::cout << "Random execute" << std::endl;
        int index = rand() % ips.size();
        return ips[index];
    }
};

Random::Random(std::string svc)
{
    std::cout << "Random constructor" << std::endl;
    this->svc = svc;
    this->ips = get_ips(svc);
}

#endif //Random_H