#!/usr/bin/python

import json
import whois
from ipwhois import IPWhois
from collections import OrderedDict



def getResult(domain):
    result = dict(whois.whois(domain))

    if 'status' in result.keys():
        del result['status']

    if 'creation_date' in result.keys():
        result['creation_date'] = result['creation_date'].strftime("%Y-%m-%d_%H:%M")

    if 'expiration_date' in result.keys():
        result['expiration_date'] = result['expiration_date'].strftime("%Y-%m-%d_%H:%M")

    if 'updated_date' in result.keys():
        result['updated_date'] = result['updated_date'].strftime("%Y-%m-%d_%H:%M")

    if 'emails' in result.keys():
        if type(result['emails']) == list:
            count = 1
            for k in result['emails']:
                result['emails-'+str(count)] = k
                count += 1
            result.pop('emails')

    if 'name_servers' in result.keys():
        if type(result['name_servers']) == list:
            count = 1
            for k in result['name_servers']:
                result['name_servers-'+str(count)] = k
                count += 1
            result.pop('name_servers')


    return OrderedDict(result)
