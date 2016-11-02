#!/usr/bin/env python


import hashlib, urllib, json, os
import urllib.request as urllib2
import requests

class vt:
    def __init__(self):
        self.api_key = '55ee5332492021897fbebb12f3768476374c9e84ef749ab19ce4865854d899fc'
        self.api_url = 'https://www.virustotal.com/vtapi/v2/'

    def handleHTTPErros(self, code):
        if code == 404:
            print('[Error 404]')
            return 0
        elif code == 403:
            print('Permissions error.\n[Error 403].')
            return 0
        elif code == 204:
            print('The quota limit has exceeded, please wait and try again soon.\n[Error 204].')
            return 0
        else:
            print('[Error '+str(code)+']')
            return 0


    def getResult(self, file):
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


def returnType():
    return ['hash']

#vt = vt()
#result = vt.getfile('e6ff1bf0821f00384cdd25efb9b1cc09')
#print(result)
