#!/usr/bin/evn python
# Create a network

import time
import os
import re
import sys

import libvirt
from libvirt import libvirtError

import sharedmod
from utils import xmlbuilder

required_params = ('networkname',
                   'bridgename',
                   'bridgeip',
                   'bridgenetmask',
                   'netstart',
                   'netend',
                   'netmode',)
optional_params = ()

def check_network_status(*args):
    """Check current network status, it will return True if
       current network is inactive, otherwise, return False
    """
    (networkname, conn, logger) = args

    net_list = conn.listNetworks()
    logger.debug("current active network list:")
    logger.debug(net_list)
    if networkname not in net_list:
        return True
    else:
        return False

def create(params):
    """Create a network from xml"""
    logger = params['logger']
    networkname = params['networkname']

    conn = sharedmod.libvirtobj['conn']

    if not check_network_status(networkname, conn, logger):
        logger.error("the %s network is running" % networkname)
        return 1

    xmlobj = xmlbuilder.XmlBuilder()
    netxml = xmlobj.build_network(params)
    logger.debug("%s network xml:\n%s" % (networkname, netxml))

    net_num1 = conn.numOfNetworks()
    logger.info("original network active number: %s" % net_num1)

    try:
        conn.networkCreateXML(netxml)
        net_num2 = conn.numOfNetworks()
        if  not check_network_status(networkname, conn, logger) and \
                net_num2 > net_num1:
            logger.info("current network active number: %s\n" % net_num2)
        else:
            logger.error("the %s network is inactive" % networkname)
            logger.error("fail to create network from :\n%s" % netxml)
            return 1
    except libvirtError, e:
        logger.error("API error message: %s, error code is %s" \
                     % (e.message, e.get_error_code()))
        logger.error("create a network from xml: \n%s" % netxml)
        return 1

    return 0
