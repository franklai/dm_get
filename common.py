import httplib
import re
from threading import Thread
import urllib
import urllib2
import urlparse

import zlib

def get_first_match(pattern, string):
    result = ''
    
    regex = re.compile(pattern).search(string)
    if regex:
        result = regex.group(1)

    return result

def get_content_by_url(url):
    f = urllib2.urlopen(url)
    html = f.read()

    return html

def is_url_ok(url):
    o = urlparse.urlparse(url)

    conn = httplib.HTTPConnection(o.netloc)
    conn.request('HEAD', o.path + o.params)
    resp = conn.getresponse()
    return resp.status == 200

def cws2fws(bytes):
    if bytes[0:3] == 'CWS':
        compressedStr = bytes[8:]
        uncompressedStr = zlib.decompress(compressedStr)

        return 'FWS' + bytes[3:8] + uncompressedStr
    else:
        return bytes
    
class DownloadFile(Thread):
    def __init__(self, url, path):
        Thread.__init__(self)
        self.url = url
        self.path = path

    def run(self):
        urllib.urlretrieve(self.url, self.path)

