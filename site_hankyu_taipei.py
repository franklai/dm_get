import logging
import os
import re
import struct

import common

site_index = 'hankyu'
site_keyword = 'uni-hankyu.com.tw/taipei'
site_url = 'http://www.uni-hankyu.com.tw/taipei/'
test_url = 'http://www.uni-hankyu.com.tw/taipei/upload/dm/dm_no1.html'

def get_swf_link(url, html):
    pattern = u'SwfName=([a-z0-9]+/book.swf)'
    swfFile = common.get_first_match(pattern, html)

    pos = url.rfind('/')
    swfLink = url[:pos] + '/' + swfFile

    logging.debug('swf file name: %s' % (swfFile))
    logging.debug('swf link: %s' % (swfLink))

    return swfLink

def get_title(url):
    pos = url.rfind('/')

    title = 'uni-hankyu-' + url[pos + 1:] 

    logging.debug('title: %s' % (title))

    return title

def get_swf(swfLink):
    print('Start download dm swf, may take a little time.')
    bytes = common.get_content_by_url(swfLink)

    return bytes

def extract_swf_to_jpgs(title, swf):
    cwd = os.getcwdu()
    path_prefix = os.path.join(cwd, title)
    if not os.path.exists(path_prefix):
        # mkdir if directory not exists
        os.makedirs(path_prefix)

    # get decompressed swf content
    bytes = common.cws2fws(swf)

    print('Start extract jpeg from swf')

    # standard JFIF file start with FF D8 FF E0
    mark = struct.pack('BBBB', 0xFF, 0xD8, 0xFF, 0xE0)

    count = 1
    pos = bytes.find(mark)
    while pos > 0:
        lengthBytes = bytes[pos - 6: pos - 2]
        length = struct.unpack('<I', lengthBytes)[0]

        end = pos + length - 2

        filename = '%03d.jpg' % (count)

        path = os.path.join(path_prefix, filename)
        open(path, 'wb').write(bytes[pos: end])

        pos = bytes.find(mark, end)
        count += 1

def downloader(url):
    html = common.get_content_by_url(url)
    html = html.decode('big5')
    swfLink = get_swf_link(url, html)
    title = get_title(url)
    swf = get_swf(swfLink)

    extract_swf_to_jpgs(title, swf)

def main():
    downloader(test_url)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
