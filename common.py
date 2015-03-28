import httplib
import os
import re
from threading import Thread
import urllib
import urllib2
import urlparse

import zlib

def to_one_line(string):
    return re.sub('[\r\n]', '', string)

def get_first_match(pattern, string):
    result = ''
    
    regex = re.compile(pattern).search(string)
    if regex:
        result = regex.group(1)

    return result

def get_all_matched(pattern, string):
    return re.findall(pattern, string)

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

def download_jpgs(title, jpgs):
    cwd = os.getcwdu()

    # need to check title
    title = re.sub(r'([|/:\\])', '_', title)

    path_prefix = os.path.join(cwd, title)

    if not os.path.exists(path_prefix):
        # mkdir if directory not exists
        os.makedirs(path_prefix)

    length = len(jpgs)
    index = 0
    print('Start to downloading %s (total: %d)' % (title.encode('big5'), length))

    for jpg in jpgs:
        index += 1

        filename = jpg[jpg.rfind('/') + 1:]

        path = os.path.join(path_prefix, filename)

        if os.path.exists(path) and os.path.getsize(path) > 0:
            print('(%d/%d) skip %s, already exists' % (index, length, path,))
            continue

        task = DownloadFile(jpg, path)
        task.start()

        # wait until the thread finish
        task.join()

        print('finish(%d/%d): %s' % (index, length, jpg,))

