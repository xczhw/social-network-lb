#ifndef ALGORITHMFACTORY_H
#define ALGORITHMFACTORY_H

#include <iostream>
#include <string>

#include "IAlgorithm.h"
#include "RoundRobin.h"
#include "Random.h"
#include "Pick2.h"

class AlgorithmFactory
{
public:
    AlgorithmFactory() = default;
    ~AlgorithmFactory() = default;
    static IAlgorithm* createAlgorithm(std::string algorithmType, std::string svc);
};

IAlgorithm* AlgorithmFactory::createAlgorithm(std::string algorithmType, std::string svc)
{
    // choose load balancing algorithm
    if (algorithmType == "round-robin")
    {
        return new RoundRobin(svc);
    }
    // else if (algorithmType == "least-connections")
    // {
    //     return new LeastConnections();
    // }
    else if (algorithmType == "random")
    {
        return new Random(svc);
    }
    // else if (algorithmType == "ip-hash")
    // {
    //     return new IpHash();
    // }
    else if (algorithmType == "pick2")
    {
        return new Pick2(svc);
    }
    else
    {
        return nullptr;
    }

}
    

#endif // ALGORITHMFACTORY_H