import logging
import os
import re
from threading import Thread
import urllib
import urllib2
import urlparse

site_index = 'dream'
site_keyword = 'dream-mall'
site_url = 'http://www.dream-mall.com.tw/'
test_url = 'http://www.dream-mall.com.tw/ecatalog/newindex.asp'

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

def get_title(url, html):
    # use directory as part of title
    pattern = u'<title>([^<]+)</title>'
    title = get_first_match(pattern, html) + ' - '
    logging.debug(title.encode('big5'))

    pattern = '/EDM/([0-9]+)/'
    title += get_first_match(pattern, html)
    logging.debug(title.encode('big5'))

    return title.strip()

def get_jpgs(url, html):
    pattern = u'class="option" href="([^"]+)" target="_blank"'
    jpgs = re.compile(pattern).findall(html)
    logging.debug('jpgs:' + repr(jpgs))

    o = urlparse.urlparse(url)
    urlPrefix = 'http://%s' % (o.netloc)
    
    full_jpgs = [urlparse.urljoin(urlPrefix, jpg) for jpg in jpgs]
    logging.debug('full_jpgs:' + repr(full_jpgs))

    return full_jpgs

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

        filename = jpg[jpg.rfind('/') + 1:]

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
    html = get_content_by_url(url)
    html = html.decode('utf8', 'ignore')
    title = get_title(url, html)
    jpgs = get_jpgs(url, html)

    download_jpgs(title, jpgs)

def main():
    url = test_url
    url = 'http://www.dream-mall.com.tw/ecatalog/newindex.asp?num=1&pic=%2FEcatalog%2FEDM%2F140730%2Fzoom_page01.jpg&pic2=%2FEcatalog%2FEDM%2F140730%2Fnormal_page01.jpg'
    downloader(url)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
