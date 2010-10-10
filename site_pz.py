import logging
import re
import os
from threading import Thread
import urllib
import urllib2
import urlparse

site_index = 'pz'
site_keyword = 'pz-peace'
site_url = 'http://www.pz-peace.com.tw/'
test_url = 'http://www.pz-peace.com.tw/onsale.asp'

def get_first_match(pattern, string):
    result = ''
    
    regex = re.compile(pattern).search(string)
    if regex:
        result = regex.group(1)

    return result

def get_content_by_url(url):
    f = urllib2.urlopen(url)
    html = f.read()

    return html

def get_title(url):
    # get html to parse <title>
    html = get_content_by_url(url)
    html = html.decode('big5')

    pattern = u'<title>([^<]*)</title>'
    title = get_first_match(pattern, html)

    return title

def get_iframes(url):
    pos = url.rfind('/')
    prefix = url[:pos]

    html = get_content_by_url(url)

    pattern = 'src="(OnSales[^"]+)"'
    iframes = re.compile(pattern).findall(html)

    iframes = [urlparse.urljoin(url, iframe) for iframe in iframes]

    return iframes

def get_jpgs(url):
    logging.debug('get jpgs from url: %s' % (url))
    html = get_content_by_url(url)

    pattern = 'img src="([^"]+)"'
    imgs = re.compile(pattern).findall(html)

    full_imgs = [urlparse.urljoin(url, img.replace('S.jpg', 'B.jpg')) for img in imgs]

    return full_imgs


class DownloadJpg(Thread):
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

        pattern = '/([^/]+)/B.jpg$'
        num = get_first_match(pattern, jpg)

        filename = 'DM_%s_B.jpg' % (num,)

        path = os.path.join(path_prefix, filename)

        if os.path.exists(path) and os.path.getsize(path) > 0:
            print('(%d/%d) skip %s, already exists' % (index, length, path,))
            continue

        task = DownloadJpg(jpg, path)
        task.start()

        # wait until the thread finish
        task.join()

        print('finish(%d/%d): %s' % (index, length, jpg,))

def downloader(url):
    title = get_title(url)
    iframes = get_iframes(url)

    for iframe in iframes:
        jpgs = get_jpgs(iframe)

        download_jpgs(title, jpgs)

def main():
    downloader(test_url)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
