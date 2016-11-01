#!/usr/bin/env python


import hashlib, urllib, json, os
import urllib.request as urllib2
import requests

class vt:
    def __init__(self):
        self.api_key = '55ee5332492021897fbebb12f3768476374c9e84ef749ab19ce4865854d899fc'
        self.api_url = 'https://www.virustotal.com/vtapi/v2/'
        self._output = "json"
        self.errmsg = 'Something went wrong. Please try again later, or contact us.'

    # handles http error codes from vt
    def handleHTTPErros(self, code):
        if code == 404:
            print(self.errmsg + '\n[Error 404].')
            return 0
        elif code == 403:
            print('You do not have permissions to make that call.\nThat should not have happened, please contact us.\n[Error 403].')
            return 0
        elif code == 204:
            print('The quota limit has exceeded, please wait and try again soon.\nIf this problem continues, please contact us.\n[Error 204].')
            return 0
        else:
            print(self.errmsg + '\n[Error '+str(code)+']')
            return 0


    # Sending and scanning files
    def scanfile(self, file):
        url = self.api_url + "file/scan"
        files = {'file': open(file, 'rb')}
        headers = {"apikey": self.api_key}
        try:
            response = requests.post( url, files=files, data=headers )
            xjson = response.json()
            response_code = xjson ['response_code']
            verbose_msg = xjson ['verbose_msg']
            if response_code == 1:
                print(verbose_msg)
                return xjson
            else:
                print(verbose_msg)

        except urllib2.HTTPError as e:
            self.handleHTTPErros(e.code)
        except urllib2.URLError as e:
            print('URLError: ' + str(e.reason))
        except Exception:
            import traceback
            print('generic exception: ' + traceback.format_exc())

    # Sending and scanning URLs
    def scanurl(self, link):
        url = self.api_url + "url/scan"
        parameters = {"url": link, "apikey": self.api_key}
        data = urllib.parse.urlencode()(parameters)
        req = urllib2.Request(url, data)
        try:
            response = urllib2.urlopen(req)
            xjson = response.read()
            response_code = json.loads(xjson).get('response_code')
            verbose_msg = json.loads(xjson).get('verbose_msg')
            if response_code == 1:
                print(verbose_msg)
                return xjson
            else:
                print(verbose_msg)

        except urllib2.HTTPError as e:
            self.handleHTTPErros(e.code)
        except urllib2.URLError as e:
            print('URLError: ' + str(e.reason))
        except Exception:
            import traceback
            print('generic exception: ' + traceback.format_exc())


    # Retrieving file scan reports
    def getfile(self, file):
        if os.path.isfile(file):
            f = open(file, 'rb')
            file = hashlib.sha256(f.read()).hexdigest()
            f.close()
        url = self.api_url + "file/report"
        parameters = {"resource": file, "apikey": self.api_key}
        data = urllib.parse.urlencode(parameters)
        binary_data = data.encode('utf-8')
        req = requests.post(url, data=binary_data)
        try:
            response = req.json()
            response_code = response['response_code']
            verbose_msg = response['verbose_msg']
            if response_code == 1:
                return self.report(response)
            else:
                print(verbose_msg)

        except urllib2.HTTPError as e:
            self.handleHTTPErros(e.code)
        except urllib2.URLError as e:
            print('URLError: ' + str(e.reason))
        except Exception:
            import traceback
            print('generic exception: ' + traceback.format_exc())

    # Retrieving URL scan reports
    def geturl(self, resource):
        url = self.api_url + "url/report"
        parameters = {"resource": resource, "apikey": self.api_key}
        data = urllib.parse.urlencode(parameters)
        req = urllib2.Request(url, data)
        try:
            response = urllib2.urlopen(req)
            xjson = response.read()
            response_code = json.loads(xjson).get('response_code')
            verbose_msg = json.loads(xjson).get('verbose_msg')
            if response_code == 1:
                print(verbose_msg)
                return self.report(xjson)
            else:
                print(verbose_msg)

        except urllib2.HTTPError as e:
            self.handleHTTPErros(e.code)
        except urllib2.URLError as e:
            print('URLError: ' + str(e.reason))
        except Exception:
            import traceback
            print('generic exception: ' + traceback.format_exc())

    #Retrieving IP address reports
    def getip (self, ip):
        url = self.api_url + "ip-address/report"
        parameters = {"ip": ip, "apikey": self.api_key}
        try:
            response = urllib.request.urlopen()('%s?%s' % (url, urllib.parse.urlencode()(parameters))).read()
            xjson = json.loads(response)
            response_code = xjson['response_code']
            verbose_msg = xjson['verbose_msg']
            if response_code == 1:
                print(verbose_msg)
                return xjson
            else:
                print(verbose_msg)

        except urllib2.HTTPError as e:
            self.handleHTTPErros(e.code)
        except urllib2.URLError as e:
            print('URLError: ' + str(e.reason))
        except Exception:
            import traceback
            print('generic exception: ' + traceback.format_exc())

    # Retrieving domain reports
    def getdomain(self, domain):
        url = self.api_url + "domain/report"
        parameters = {"domain": domain, "apikey": self.api_key}
        try:
            response = urllib.request.urlopen()('%s?%s' % (url, urllib.parse.urlencode()(parameters))).read()
            xjson = json.loads(response)
            response_code = xjson['response_code']
            verbose_msg = xjson['verbose_msg']
            if response_code == 1:
                print(verbose_msg)
                return xjson
            else:
                print(verbose_msg)

        except urllib2.HTTPError as e:
            self.handleHTTPErros(e.code)
        except urllib2.URLError as e:
            print('URLError: ' + str(e.reason))
        except Exception:
            import traceback
            print('generic exception: ' + traceback.format_exc())



    #Rescanning already submitted files
    def rescan(self, resource):
        if os.path.isfile(resource):
            f = open(resource, 'rb')
            resource = hashlib.sha256(f.read()).hexdigest()
            f.close()
        url = self.api_url + "file/rescan"
        parameters = {"resource":  resource, "apikey": self.api_key }
        data = urllib.parse.urlencode()(parameters)
        req = urllib2.Request(url, data)
        try:
            response = urllib2.urlopen(req)
            xjson = response.read()
            response_code = json.loads(xjson).get('response_code')
            verbose_msg = json.loads(xjson).get('verbose_msg')
            if response_code == 1:
                print(verbose_msg)
                return xjson
            else:
                print(verbose_msg)

        except urllib2.HTTPError as e:
            self.handleHTTPErros(e.code)
        except urllib2.URLError as e:
            print('URLError: ' + str(e.reason))
        except Exception:
            import traceback
            print('generic exception: ' + traceback.format_exc())

    # internal - returns results accourding to output format (json, html or output)
    # available only for getfile and geturl
    def report(self, jsonx):
        if self._output == "json":
            return jsonx


    # set a new api-key
    def setkey(self, key):
        self.api_key = key



vt = vt()
result = vt.getfile('e6ff1bf0821f00384cdd25efb9b1cc09')
print(result)
