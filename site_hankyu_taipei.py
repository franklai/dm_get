import logging
import os
import re
import urlparse

import common

site_index = 'hankyu_taipei'
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
    dmMainUrl = 'http://www.uni-hankyu.com.tw/taipei/dm.asp'
    html = common.get_content_by_url(dmMainUrl)
    html = html.decode('utf-8')

    pattern = u'<title>([^<]+)</title>'
    department = common.get_first_match(pattern, html)

    pos = url.rfind('/')
    urlFile = url[pos + 1]

    urlPos = html.find(urlFile)
    titlePos = html.find('<strong>', urlPos)
    if titlePos > 0:
        endPos = html.find('</strong>', titlePos)
        matchedTitle = html[titlePos + len('<strong>'): endPos]

        title = '%s - %s' % (department, matchedTitle)
    else:
        title = '%s - %s' % (department, urlFile)

    logging.debug('title: %s' % (title.encode('big5')))

    return title

def get_swf(swfLink):
    print('Start download dm swf, may take a little time.')
    bytes = common.get_content_by_url(swfLink)

    return bytes

def get_jpgs(swfLink):
    index = 30
    step = stepMax = 16
    forward = True

    while abs(step) > 0:
        jpgUrl = urlparse.urljoin(swfLink, '%02d.jpg' % (index))
        logging.debug('test url is %s' % (jpgUrl, ))

        if common.is_url_ok(jpgUrl):
            if step != stepMax:
                step /= 2
            forward = True
        else:
            step /= 2
            forward = False

        if forward:
            index += step
        else:
            index -= step

    lastIndex = index
    if not forward:
        lastIndex -= 1

    logging.debug('last index is %d' % (lastIndex))

    jpgs = [urlparse.urljoin(swfLink, '%02d.jpg' % (x, )) for x in range(lastIndex + 1)] 
    return jpgs

def download_jpgs(title, jpgs):
    cwd = os.getcwdu()

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

        task = common.DownloadFile(jpg, path)
        task.start()

        # wait until the thread finish
        task.join()

        print('finish(%d/%d): %s' % (index, length, jpg,))

def downloader(url):
    html = common.get_content_by_url(url)
    html = html.decode('big5')
    swfLink = get_swf_link(url, html)
    title = get_title(url)

    jpgs = get_jpgs(swfLink)

    download_jpgs(title, jpgs)

def main():
    downloader(test_url)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
