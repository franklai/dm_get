# -*- coding: utf8 -*-
import logging
import os
import re
import urlparse

import common

site_index = 'citysuper'
site_keyword = 'citysuper'
site_url = 'http://www.citysuper.com.tw/'
test_url = 'http://www.citysuper.com.tw/flippingBook/edmDisplay.asp?lgid=1&euid=801421E5-E642-4314-8924-D5EF0F3A1830'

def get_title(html):
    pattern = 'flippingBook.settings.printTitle = "([^"]+)"'

    title = common.get_first_match(pattern, html)

    logging.debug('title: %s' % (title))

    return title

def get_pages(html):
    prefix = 'flippingBook.pages'

    posStart = html.find(prefix)
    if posStart == -1:
        return []

    posEnd = html.find(']', posStart)
    if posEnd == -1:
        return []

    logging.debug('pages position %d:%d' % (posStart, posEnd, ))

    pagesText = html[posStart:posEnd]
    pattern = "'([^']+\.jpg)'"
    pages = re.findall(pattern, pagesText)
    logging.debug('found pages: %s' % (', '.join(pages)))

    return pages

def get_zoom_path(html):
    pattern = 'flippingBook.settings.zoomPath = "([^"]+)"'
    return common.get_first_match(pattern, html)

def get_jpgs(url, html):
    pages = get_pages(html)
    zoomPath = get_zoom_path(html)

    imgs = [page[page.rfind('/') + 1:] for page in pages]
    logging.debug('images: %s' % (', '.join(imgs)))

    urlPrefix = urlparse.urljoin(url, zoomPath)
    jpgs = [urlparse.urljoin(urlPrefix, img) for img in imgs] 
    logging.debug('full jpeg path: %s' % (', '.join(jpgs)))

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
    html = html.decode('utf-8')

    title = get_title(html)
    jpgs = get_jpgs(url, html)

    download_jpgs(title, jpgs)

def main():
    downloader(test_url)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
