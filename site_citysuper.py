# -*- coding: utf8 -*-
import logging
import urlparse

import common

site_index = 'citysuper'
site_keyword = 'citysuper'
site_url = 'http://www.citysuper.com.tw/'
test_url = 'http://www.citysuper.com.tw/flippingBook/edmDisplay.asp?lgid=1&euid=801421E5-E642-4314-8924-D5EF0F3A1830'

def get_title(html):
    pattern = 'flippingBook.settings.printTitle = "([^"]+)"'

    title = common.get_first_match(pattern, html)
    title = "city'super %s" % (title,)

    logging.debug('title: %s' % (title.encode('big5')))

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
    pages = common.get_all_matched(pattern, pagesText)
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
    logging.debug('full jpeg path: \n%s' % ('\n'.join(jpgs)))

    return jpgs


def downloader(url):
    html = common.get_content_by_url(url)
    html = html.decode('utf-8')

    title = get_title(html)
    jpgs = get_jpgs(url, html)

    common.download_jpgs(title, jpgs)

def main():
    downloader(test_url)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
