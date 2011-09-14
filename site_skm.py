# -*- coding: utf8 -*-
import logging
import urlparse

import common

site_index = 'skm'
site_keyword = 'skm'
site_url = 'http://www.skm.com.tw/'
test_url = 'http://www.skm.com.tw/edm/str100/2011_newchange/index.html'

def get_title(url, html):
    # use directory as part of title
    pattern = '/([^/]+)/[^/]+$'
    title = common.get_first_match(pattern, url)

    pattern = u'<title>([^<]*)</title>'
    title += common.get_first_match(pattern, html)

    return title

def get_charset(html):
    pattern = 'charset=([^"]+)'
    charset = common.get_first_match(pattern, html)
    logging.debug('charset = %s' % (charset, ))
    return charset

def get_jpgs(url, html):
    pos = url.rfind('/')
    prefix = url[:pos]

    pattern = '"([^"]*bookSettings.js)"'
    js_url = common.get_first_match(pattern, html)

    js_full_url = urlparse.urljoin(url, js_url)
    
    logging.debug('js_full_url:' + js_full_url)

    js = common.get_content_by_url(js_full_url)
    logging.debug('js:' + js)
    pattern = '"pages/([^"]+)'
    jpgs = common.get_all_matched(pattern, js)
    logging.debug('jpgs:' + repr(jpgs))

    full_jpgs = ['%s/pages/large/%s' % (prefix, jpg) for jpg in jpgs]

    return full_jpgs

def downloader(url):
    html = common.get_content_by_url(url)
    charset = get_charset(html)
    html = html.decode(charset)
    title = get_title(url, html)
    jpgs = get_jpgs(url, html)

    common.download_jpgs(title, jpgs)

def main():
    downloader(test_url)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
