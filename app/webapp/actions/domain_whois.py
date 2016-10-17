#!/usr/bin/python

import json
import whois
from ipwhois import IPWhois


def getResult(domain):
    result = dict(whois.whois(domain))

    if 'status' in result.keys():
        del result['status']

    return result
