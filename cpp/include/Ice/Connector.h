// **********************************************************************
//
// Copyright (c) 2002
// MutableRealms, Inc.
// Huntsville, AL, USA
//
// All Rights Reserved
//
// **********************************************************************

#ifndef ICE_CONNECTOR_H
#define ICE_CONNECTOR_H

#include <Ice/ConnectorF.h>
#include <Ice/InstanceF.h>
#include <Ice/TransceiverF.h>
#include <Ice/Shared.h>

namespace _Ice
{

class EmitterFactoryI;

class ConnectorI : public Shared
{
public:
    
    Transceiver connect();
    
private:

    ConnectorI(const ConnectorI&);
    void operator=(const ConnectorI&);

    ConnectorI(Instance, const std::string&, int);
    virtual ~ConnectorI();
    void destroy();
    friend class EmitterFactoryI; // May create and destroy ConnectorIs

    Instance instance_;
    std::string host_;
    int port_;
};

}

#endif
