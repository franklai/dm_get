# -*- coding: utf8 -*-
import logging
import urlparse

import common
import requests

site_index = 'citysuper'
site_keyword = 'citysuper'
site_url = 'http://www.citysuper.com.tw/'
test_url = 'http://books.citysuper.com.tw/books/ygku/#p=1'

def get_title(html):
    pattern = 'og:description" content="([^"]+)"'

    title = common.get_first_match(pattern, html)
    title = title.replace('\n', '').replace('\r', '').replace('\\', '')

    logging.debug('title: %s' % (title.encode('big5')))

    return title

def get_pages(url):
    config_url = urlparse.urljoin(url, 'javascript/config.js')

    r = requests.get(config_url)
    r.encoding = 'utf-8'

    text = r.text

    pattern = "'([^']+\.jpg)'"
    pattern = '"l":"(files[^"]+)"'
    pages = common.get_all_matched(pattern, text)
    logging.debug('found pages: %s' % (', '.join(pages)))

    return pages

def get_jpgs(url, html):
    pages = get_pages(url)

    jpgs = [urlparse.urljoin(url, page) for page in pages] 
    logging.debug('full jpeg path: \n%s' % ('\n'.join(jpgs)))

    return jpgs


def downloader(url):
    r = requests.get(url)
    r.encoding = 'utf-8'
    html = r.text

    title = get_title(html)
    jpgs = get_jpgs(url, html)

    common.download_jpgs(title, jpgs)

def main():
    url = test_url
    downloader(url)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
