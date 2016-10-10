#!/usr/bin/python

from whois import *
import json

def getWhois(domain):
    whois_json = whois(domain)
    return jsonify(whois_json)




'''
whois_json['dnssec'] = w.dnssec
whois_json['name'] = w.name
whois_json['address'] = w.address
whois_json['org'] = w.org
whois_json['emails'] = w.emails
whois_json['country'] = w.country
whois_json['zipcode'] = w.zipcode
whois_json['state'] = w.state
whois_json['city'] = w.city
whois_json['referral_url'] = w.referral_url
whois_json['registrar'] = w.registrar
whois_json['creation_date'] = w.creation_date
whois_json['updated_date'] = w.updated_date
whois_json['expiration_date'] = w.expiration_date
'''
