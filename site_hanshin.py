import logging
import urlparse

import common

site_index = 'hanshin'
site_keyword = 'hanshin'
site_url = 'http://www.hanshinarena.com.tw/'
# test_url = 'http://www.hanshinarena.com.tw/DM/?m_id=69'
test_url = 'http://www.hanshin.com.tw/DM/?m_id=164'

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
    titles = common.get_all_matched(pattern, html)
    logging.debug('titles: %s' % (repr(titles)))

    matchedTitle = ''

    for titleId, titleStr in titles:
        if titleId == id:
            matchedTitle = titleStr
            break

    if matchedTitle:
        title = '%s - %s' % (department, matchedTitle)
    else:
        title = '%s %s' % (department, id)
    logging.debug('title: %s' % (title.encode('big5')))

    return title

def get_jpgs(url, id):
    # get values from xml
    # http://www.hanshinarena.com.tw/DM/39/Pages.xml
    xmlUrl = urlparse.urljoin(url, '/DM/%s/Pages.xml' % (id))
    logging.debug(xmlUrl)
    xml = common.get_content_by_url(xmlUrl)

    pattern = u'<page src="([^"]+)"/>'
    imgs = common.get_all_matched(pattern, xml)

    # http://www.hanshinarena.com.tw/DM/39/pages/4.jpg
    full_imgs = [urlparse.urljoin(xmlUrl, img) for img in imgs]

    logging.debug('images: %s' % (repr(full_imgs)))

    return full_imgs

def downloader(url):
    id = get_id(url)
    title = get_title(url, id)

    jpgs = get_jpgs(url, id)

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

