#!/usr/bin/python

import json
import whois
from ipwhois import IPWhois
from pprint import pprint
from collections import OrderedDict


def getWhoisResultForDomain(input):
    result = dict(whois.whois(input))

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


def getWhoisResultForIp(input):

    output = OrderedDict()
    obj = IPWhois(input)
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




def returnNecessaryInputSettings():
    return {
            'type':['domain', 'ipv4'],
            'need_api':'no',
            'need_username':'no',
            'need_password':'no'
            }


def returnType():
    return ['ipv4', 'domain']


def getResult(conf):

    print(conf)

    if conf['type'] == 'domain':
        result = getWhoisResultForDomain(conf['value'])

    if conf['type'] == 'ipv4':
        result = getWhoisResultForIp(conf['value'])

    return result
