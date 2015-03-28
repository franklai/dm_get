import logging
import re
import urlparse

import common

site_index = 'hanshin'
site_keyword = 'hanshin'
site_url = 'http://www.hanshinarena.com.tw/'
test_url = 'http://www.hanshinarena.com.tw/webc/html/dm/02.php?num=43&page=1'

def get_dm_num(qs):
    obj = urlparse.parse_qs(qs)
    return obj['num']

def get_title(url):
    # http://www.hanshinarena.com.tw/webc/html/dm/index.php
    # http://www.hanshin.com.tw/webc/html/dm/index.php
    # no title information on DM page, get title from index page
    obj = urlparse.urlparse(url)

    index_page = '%s://%s/webc/html/dm/index.php' % (obj.scheme, obj.netloc)
    logging.debug('index page url: %s' % (index_page))

    html = common.get_content_by_url(index_page)
    html = html.decode('utf-8')

    pattern = u'<meta name="description" Content="(.*)">'
    store = common.get_first_match(pattern, html).strip()

    num = get_dm_num(obj.query)[0]

    one_line = common.to_one_line(html)

    pattern = u'<a href="02.php\?num=%s\&.*?">\s*<p class="title">([^<]+)</p>\s*<p class="date">([^<]+)</p>' % (num, )
    logging.debug('pattern: %s' % (pattern))

    regex = re.search(pattern, one_line)
    if regex:
        dm_title = regex.group(1)
        dm_date = regex.group(2)

        title = '%s - %s %s' % (store, dm_title, dm_date)
    else:
        title = u'%s - num %s' % (store, num)
        
    title = title.strip()
    logging.debug('title: %s' % (title.encode('big5')))

    return title

def get_jpgs(url):
    html = common.get_content_by_url(url)

    pattern = '_lsrc="(.*?.jpg)"'
    imgs = common.get_all_matched(pattern, html)

    # http://www.hanshinarena.com.tw/upload/photo/pic20150327_04162844.jpg
    full_imgs = [urlparse.urljoin(url, img) for img in imgs]

    logging.debug('images: %s' % (repr(full_imgs)))

    return full_imgs

def downloader(url):
    title = get_title(url)

    jpgs = get_jpgs(url)

    common.download_jpgs(title, jpgs)

def main():
    url = test_url
#     url = 'http://www.hanshinarena.com.tw/DM/?m_id=147'
    downloader(url)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
    # http://www.hanshinarena.com.tw/DM/39/
    # http://www.hanshinarena.com.tw/DM/?m_id=39
    # http://www.hanshinarena.com.tw/DM/39/Pages.xml
    # http://www.hanshinarena.com.tw/DM/39/pages/4.jpg

