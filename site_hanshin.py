import logging
import os
import re
from threading import Thread
import urllib
import urlparse

import common

site_index = 'hanshin'
site_keyword = 'hanshin'
site_url = 'http://www.hanshinarena.com.tw/'
# test_url = 'http://www.hanshinarena.com.tw/DM/?m_id=69'
test_url = 'http://www.hanshin.com.tw/DM/?m_id=70'

def get_id(url):
    pattern = u'm_id=([0-9]+)'
    id = common.get_first_match(pattern, url)

    if id == '':
        pattern = u'/DM/([0-9]+)'
        id = common.get_first_match(pattern, url)

    return id

def get_title(url, id):
    # http://www.hanshinarena.com.tw/DM/bottom.php
    # http://www.hanshin.com.tw/DM/bottom.php
    # get title from list
    listUrl = urlparse.urljoin(url, '/DM/bottom.php')
    logging.debug('bottom url: %s' % (listUrl))

    html = common.get_content_by_url(listUrl)
    html = html.decode('utf-8')

    pattern = u'<title>([^<]+)</title>'
    department = common.get_first_match(pattern, html)
    logging.debug('department: %s' % (department.encode('big5')))

    pattern = u'option value="([0-9]+)" *>([^<]+)<'
    titles = re.compile(pattern).findall(html)
    logging.debug('titles: %s' % (repr(titles)))

    matchedTitle = ''

    for titleId, titleStr in titles:
        if titleId == id:
            matchedTitle = titleStr
            break
            
    title = '%s - %s' % (department, matchedTitle)
    logging.debug('title: %s' % (title.encode('big5')))

    return title

def get_jpgs(url, id):
    # get values from xml
    # http://www.hanshinarena.com.tw/DM/39/Pages.xml
    xmlUrl = urlparse.urljoin(url, '/DM/%s/Pages.xml' % (id))
    xml = common.get_content_by_url(xmlUrl)

    pattern = u'<page src="([^"]+)"/>'
    imgs = re.compile(pattern).findall(xml)

    # http://www.hanshinarena.com.tw/DM/39/pages/4.jpg
    full_imgs = [urlparse.urljoin(xmlUrl, img) for img in imgs]

    logging.debug('images: %s' % (repr(full_imgs)))

    return full_imgs


class DownloadFile(Thread):
    def __init__(self, url, path):
        Thread.__init__(self)
        self.url = url
        self.path = path

    def run(self):
        urllib.urlretrieve(self.url, self.path)

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

        task = DownloadFile(jpg, path)
        task.start()

        # wait until the thread finish
        task.join()

        print('finish(%d/%d): %s' % (index, length, jpg,))

def downloader(url):
    id = get_id(url)
    title = get_title(url, id)

    jpgs = get_jpgs(url, id)

    download_jpgs(title, jpgs)

def main():
    downloader(test_url)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
    # http://www.hanshinarena.com.tw/DM/39/
    # http://www.hanshinarena.com.tw/DM/?m_id=39
    # http://www.hanshinarena.com.tw/DM/39/Pages.xml
    # http://www.hanshinarena.com.tw/DM/39/pages/4.jpg

