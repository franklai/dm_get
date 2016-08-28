# -*- coding: utf8 -*-
import json
import logging
import urlparse

import common

site_index = 'skm'
site_keyword = 'skm'
site_url = 'http://www.skm.com.tw/'
# test_url = 'http://www.skm.com.tw/edm/str120/2012_0830_autumn/index.html'
# test_url = 'http://www.skm.com.tw/edm/?st=str350&dm=20120824_AUTUMN'
test_url = 'http://www.skm.com.tw/zh-TW/OnLineDM/Detail?CTID=5b23384c-1bf4-4909-bba3-d1308d3955c6&storeId=4d6c8b25-f31a-4d83-b016-d97973648188'

def parse_query(url):
    o = urlparse.urlparse(url)
    queries = urlparse.parse_qs(o.query)

    return queries

def get_dm_id(url):
    q = parse_query(url)

    return q['CTID'][0]

def get_dm_id_by_html(html):
    pattern = 'calameo.com\/read\/([0-9a-f]+)" selected'
    return common.get_first_match(pattern, html)

def get_store_id(url):
    q = parse_query(url)

    return q['storeId'][0]

def get_title_by_value(value, html):
    pattern = 'value="%s"[a-z ]*>(.*?)</option>' % (value)
    logging.debug('pattern: %s' % (pattern))
    return common.get_first_match(pattern, html)

def get_dm_title(html):
    pattern = ' selected >(.*?)</option>'
    return common.get_first_match(pattern, html)

def get_title(url, html):
    store_id = get_store_id(url)
    dm_id = get_dm_id(url)

    logging.debug('id, store: %s, dm: %s' % (store_id, dm_id))

    store_title = get_title_by_value(store_id, html).strip()
    dm_title = get_dm_title(html).strip()

    title = u'新光三越 %s - %s' % (store_title, dm_title)

    logging.debug('title = [%s]' % (title, ))

    return title

def get_charset(html):
    pattern = 'charset=([^"]+)'
    charset = common.get_first_match(pattern, html)
    logging.debug('charset = %s' % (charset, ))
    return charset

def find_thumbs(obj):
    if 'content' not in obj:
        return False

    thumbnail = obj['content']['url']['thumbnail']
    logging.debug('thumbnail url template:' + thumbnail)
    pattern = '([0-9]+-[0-9a-z]+)'
    book_id = common.get_first_match(pattern, thumbnail)

    prefix = 'http://p.calameoassets.com/%s' % (book_id)

    pages = obj['content']['pages']
    thumbs = ['%s/%s' % (prefix, x['i']['u']) for x in pages]

    return thumbs

def get_json(dm_id):
    # http://d.calameo.com/3.0.0/book.php?bkcode=0044215047861f75204a4&callback=_jsonBook
    url = 'http://d.calameo.com/3.0.0/book.php?bkcode=%s&callback=_jsonBook' % (dm_id)
    logging.debug('JSON url:' + url)

    raw = common.get_content_by_url(url)
    if not raw:
        return False
    json_str = raw[len('_jsonBook('):-1]
    obj = json.loads(json_str)
    return obj

def get_jpgs(url, html):
    dm_id = get_dm_id_by_html(html)
    if not dm_id:
        logging.warn('Failed to get dm id')
        return False

    obj = get_json(dm_id)
    thumbs = find_thumbs(obj)

#     jpgs = [urlparse.urljoin(url, thumb.replace('/z_', '/')) for thumb in thumbs]
    jpgs = [thumb for thumb in thumbs]

    logging.debug('jpgs:' + repr(jpgs))

    return jpgs

def downloader(url):
    html = common.get_content_by_url(url)
    charset = get_charset(html)
    html = html.decode(charset)

    title = get_title(url, html)
    jpgs = get_jpgs(url, html)

    if not jpgs:
        logging.debug('Failed to get jpgs')
        return False

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
