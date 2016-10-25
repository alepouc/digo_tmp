#!/usr/bin/python

import json
import whois
from ipwhois import IPWhois


def getResult(ip):
    output = {}
    obj = IPWhois(ip)
    result = obj.lookup_whois()
    for k, v in result.items():

        if "nets" not in k:
            output["0-"+k] = v

        if "nets" in k:
            if type(v) == list:
                count = 0
                for row in v:
                    count += 1
                    for k1, v1 in row.items():
                        output[str(count)+"-"+k1] = v1

    return output
