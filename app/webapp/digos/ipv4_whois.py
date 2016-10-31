#!/usr/bin/python

import json
import whois
from ipwhois import IPWhois
from pprint import pprint
from collections import OrderedDict


def getResult(ip):
    output = OrderedDict()
    obj = IPWhois(ip)
    result = obj.lookup_whois()

    for k, v in result.items():

        if "nets" not in k:
            output[k] = v

    for k, v in result.items():

        if "nets" in k:
            if type(v) == list:
                count = 0
                for row in v:
                    count += 1
                    for k1, v1 in row.items():
                        output[k1+'-'+str(count)] = v1
    return output
