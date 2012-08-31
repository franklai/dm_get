import logging
import os
import re
import urlparse

import common

site_index = 'hankyu_taipei'
site_keyword = 'uni-hankyu.com.tw/taipei'
site_url = 'http://www.uni-hankyu.com.tw/taipei/'
test_url = 'http://www.uni-hankyu.com.tw/taipei/upload/dm/no48/index.html'

def get_charset(html):
    pattern = 'charset=([^"]+)'
    charset = common.get_first_match(pattern, html)
    logging.debug('charset = %s' % (charset, ))
    return charset

def get_title_from_html(html):
    # use directory as part of title
    pattern = u'<title>([^<]*)</title>'
    prefix = common.get_first_match(pattern, html)

    pattern = "var title = '([^']+)';"
    dmTitle = common.get_first_match(pattern, html)

    title = '%s - %s' % (prefix, dmTitle)

    logging.debug('title = %s' % (title, ))

    return title

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

def downloader(url):
    html = common.get_content_by_url(url)
    charset = get_charset(html)
    html = html.decode(charset)

    title = get_title_from_html(html)

    jpgs = get_jpgs(url, html)

    common.download_jpgs(title, jpgs)

def main():
    downloader(test_url)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
