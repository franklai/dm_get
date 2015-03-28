# -*- coding: utf8 -*-
import logging
import urlparse

import common

site_index = 'skm'
site_keyword = 'skm'
site_url = 'http://www.skm.com.tw/'
# test_url = 'http://www.skm.com.tw/edm/str120/2012_0830_autumn/index.html'
# test_url = 'http://www.skm.com.tw/edm/?st=str350&dm=20120824_AUTUMN'
test_url = 'http://www.skm.com.tw/zh-TW/OnLineDM/Detail?CTID=21f47f2f-df94-4045-beef-5e5f5c51cae0&storeId=9e7f2731-ff3c-4d18-b872-ebb2660528f5'

def parse_query(url):
    o = urlparse.urlparse(url)
    queries = urlparse.parse_qs(o.query)

    return queries

def get_dm_id(url):
    q = parse_query(url)

    return q['CTID'][0]

def get_store_id(url):
    q = parse_query(url)

    return q['storeId'][0]

def get_title_by_value(value, html):
    pattern = 'value="%s"[a-z ]*>(.*?)</option>' % (value)
    logging.debug('pattern: %s' % (pattern))
    return common.get_first_match(pattern, html)

def get_title(url, html):
    store_id = get_store_id(url)
    dm_id = get_dm_id(url)

    logging.debug('id, store: %s, dm: %s' % (store_id, dm_id))

    store_title = get_title_by_value(store_id, html).strip()
    dm_title = get_title_by_value(dm_id, html).strip()

    title = u'新光三越 %s - %s' % (store_title, dm_title)

    logging.debug('title = [%s]' % (title, ))

    return title

def get_charset(html):
    pattern = 'charset=([^"]+)'
    charset = common.get_first_match(pattern, html)
    logging.debug('charset = %s' % (charset, ))
    return charset

def find_thumbs(dm_id, html):
    pattern = '<img src="(/upload/%s/.*?)" />' % (dm_id)
    thumbs = common.get_all_matched(pattern, html)
    return thumbs

def get_jpgs(url, html):
    dm_id = get_dm_id(url)
    thumbs = find_thumbs(dm_id, html)

    jpgs = [urlparse.urljoin(url, thumb.replace('/z_', '/')) for thumb in thumbs]

    logging.debug('jpgs:' + repr(jpgs))

    return jpgs

def downloader(url):
    html = common.get_content_by_url(url)
    charset = get_charset(html)
    html = html.decode(charset)

    title = get_title(url, html)
    jpgs = get_jpgs(url, html)

    common.download_jpgs(title, jpgs)

def main():
    url = test_url
#     url = 'http://www.skm.com.tw/edm/str300/20120820_hakka/index.html'
#     url = 'http://www.skm.com.tw/edm/10/201208_midAutumn/index.html'
#     url = 'http://www.skm.com.tw/zh-TW/OnLineDM/Detail?CTID=5c930a1c-0f38-414a-b987-76fd6199ce1d&storeId=9e7f2731-ff3c-4d18-b872-ebb2660528f5'
#     url = 'http://www.skm.com.tw/zh-TW/OnLineDM/Detail?CTID=e647ea24-b4c3-48e3-b3c8-259217cfad5c&storeId=9daa4b7d-1a00-4cb9-a429-8cb99050e88a#1'
    downloader(url)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
