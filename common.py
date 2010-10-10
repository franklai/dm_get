import re
import urllib2
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

def cws2fws(bytes):
    if bytes[0:3] == 'CWS':
        compressedStr = bytes[8:]
        uncompressedStr = zlib.decompress(compressedStr)

        return 'FWS' + bytes[3:8] + uncompressedStr
    else:
        return bytes
    
