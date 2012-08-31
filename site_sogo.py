# -*- coding: utf8 -*-
import logging
import re
import urlparse

import common

site_index = 'sogo'
site_keyword = 'sogo'
site_url = 'http://www.sogo.com.tw/'
test_url = 'http://www.sogo.com.tw/www/flippingbook/index.asp?id=742&BranchIds=8'
# test_url = 'http://www.sogo.com.tw/www/flippingbook/index2.asp?id=432&sp=&flag=&BranchIds=2'


def get_real_content_by_html(url, html):
    pattern = '<frame src="(index[^"]+)"'
    frame_url = common.get_first_match(pattern, html)
    logging.debug('real content frame url is [%s]' % (frame_url, ))

    realUrl = urlparse.urljoin(url, frame_url)
    realHtml = common.get_content_by_url(realUrl)

    return realHtml

def get_charset(html):
    pattern = 'charset=([^"]+)'
    charset = common.get_first_match(pattern, html)
    logging.debug('charset = %s' % (charset, ))
    return charset

def get_title(url, html):
    pattern = '<title>([^<]+)</title>'
    title = common.get_first_match(pattern, html)
    logging.debug('title: %s' % (title.encode('big5')))

    return title.strip()

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
    pattern = '"([^"]+\.jpg)"'
    pages = common.get_all_matched(pattern, pagesText)
    logging.debug('found pages: %s' % (', '.join(pages)))

    return pages

def get_jpgs(url, html):
    pattern = '"(js/bookSettings[^"]+)"'
    jsUrl = common.get_first_match(pattern, html)

    jsFullUrl = urlparse.urljoin(url, jsUrl)
    jsContent = common.get_content_by_url(jsFullUrl)

    pages = get_pages(jsContent)

    imgs = [page.replace('small', 'large') for page in pages]
    logging.debug('full images path:\n%s' % ('\n'.join(imgs)))

    return imgs

def downloader(url):
    html = common.get_content_by_url(url)

    if -1 == html.find('swfobject'):
        # Cannot find swfobject, may be iframe page
        html = get_real_content_by_html(url, html)

    charset = get_charset(html)
    html = html.decode(charset)
    title = get_title(url, html)
    jpgs = get_jpgs(url, html)

    logging.debug('title: [%s], ' % (title, ))
    common.download_jpgs(title, jpgs)

def main():
    downloader(test_url)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()

