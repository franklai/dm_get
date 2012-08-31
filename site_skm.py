# -*- coding: utf8 -*-
import logging
import urlparse

import common

site_index = 'skm'
site_keyword = 'skm'
site_url = 'http://www.skm.com.tw/'
# test_url = 'http://www.skm.com.tw/edm/str120/2012_0830_autumn/index.html'
test_url = 'http://www.skm.com.tw/edm/?st=str350&dm=20120824_AUTUMN'

def get_title(url, html):
    # use directory as part of title
    pattern = '/([^/]+)/[^/]+$'
    title = common.get_first_match(pattern, url)

    pattern = u'<title>([^<]*)</title>'
    title += common.get_first_match(pattern, html)

    logging.debug('title = %s' % (title, ))

    return title

def get_charset(html):
    pattern = 'charset=([^"]+)'
    charset = common.get_first_match(pattern, html)
    logging.debug('charset = %s' % (charset, ))
    return charset

def get_book_settings_content(url, html):
    pattern = '"([^"]*bookSettings.*.js)"'
    js_url = common.get_first_match(pattern, html)

    js_full_url = urlparse.urljoin(url, js_url)
    
    logging.debug('js_full_url:' + js_full_url)

    js = common.get_content_by_url(js_full_url)
#     logging.debug('js:' + js)

    return js

def get_pages_from_js(js):
    pattern = '"pages/([^"]+)'
    jpgs = common.get_all_matched(pattern, js)

    return jpgs

def get_jpgs(url, html):
    pos = url.rfind('/')
    prefix = url[:pos]

    js = get_book_settings_content(url, html)

    jpgs = get_pages_from_js(js)

    logging.debug('prefix:' + prefix)
    logging.debug('jpgs:' + repr(jpgs))

    full_jpgs = ['%s/pages/large/%s' % (prefix, jpg) for jpg in jpgs]

    return full_jpgs

def get_title_from_js(js):
    pattern = 'var eDmTitle="([^"]+)";'
    title = common.get_first_match(pattern, js)

    return title

def get_prefix_from_url(url):
    # http://www.skm.com.tw/edm/?st=str350&dm=20120824_summersale
    # http://www.skm.com.tw/edm/str350/20120824_summersale/pages/large/01.jpg

    o = urlparse.urlparse(url)
    queries = urlparse.parse_qs(o.query)
    prefix = '%s://%s%s%s/%s' % (
        o.scheme, o.netloc, o.path, 
        queries['st'][0], queries['dm'][0]
    )

    return prefix

def handle_new_style(url, html):
    title = 'skm edm'
    jpgs = []

    pos = url.rfind('/')
    prefix = url[:pos]

    js = get_book_settings_content(url, html)
    js = js.decode('utf-8')

    jpgs = get_pages_from_js(js)
    prefix = get_prefix_from_url(url)
    full_jpgs = ['%s/pages/large/%s' % (prefix, jpg) for jpg in jpgs]
    logging.debug('prefix:' + prefix)
    logging.debug('jpgs:' + repr(jpgs))

    eDmTitle = get_title_from_js(js)
    pattern = 'document.title="([^"]+)"'
    title = common.get_first_match(pattern, html) + eDmTitle

    logging.debug('title:' + title)

    return title, full_jpgs

def downloader(url):
    html = common.get_content_by_url(url)
    charset = get_charset(html)
    html = html.decode(charset)

    if charset == 'big5':
        # old style
        title = get_title(url, html)
        jpgs = get_jpgs(url, html)
    else:
        # new style, only ZuoYing uses this (2012 Aug 31)
        title, jpgs = handle_new_style(url, html)

    common.download_jpgs(title, jpgs)

def main():
    url = test_url
#     url = 'http://www.skm.com.tw/edm/str300/20120820_hakka/index.html'
#     url = 'http://www.skm.com.tw/edm/10/201208_midAutumn/index.html'
    downloader(url)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
