#ifndef SOCIAL_NETWORK_IALGORITHM_H
#define SOCIAL_NETWORK_IALGORITHM_H

#include <iostream>
#include <vector>

// IAlgorithm.h
class IAlgorithm {
public:
    virtual ~IAlgorithm() {}
    virtual std::string execute() = 0;
    
protected:
    std::string svc;
    std::vector <std::string> ips;
};

#endif //SOCIAL_NETWORK_IALGORITHM_H
