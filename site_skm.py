import logging
import os
import re
from threading import Thread
import urllib
import urllib2
import urlparse

site_index = 'skm'
site_keyword = 'skm'
site_url = 'http://www.skm.com.tw/'
test_url = 'http://www.skm.com.tw/edm/str120/2009_1005_PHOTO/index.html'

# logging.basicConfig(level=logging.DEBUG)


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
    pattern = '/([^/]+)/[^/]+$'
    title = get_first_match(pattern, url)

    pattern = u'<title>([^<]*)</title>'
    title += get_first_match(pattern, html)

    return title

def get_jpgs(url, html):
    pos = url.rfind('/')
    prefix = url[:pos]

    pattern = '"([^"]*bookSettings.js)"'
    js_url = get_first_match(pattern, html)

    js_full_url = urlparse.urljoin(url, js_url)
    
    logging.debug('js_full_url:' + js_full_url)

    js = get_content_by_url(js_full_url)
    logging.debug('js:' + js)
    pattern = '"pages/([^"]+)'
    jpgs = re.compile(pattern).findall(js)
    logging.debug('jpgs:' + repr(jpgs))

    full_jpgs = ['%s/pages/large/%s' % (prefix, jpg) for jpg in jpgs]

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
    html = html.decode('big5')
    title = get_title(url, html)
    jpgs = get_jpgs(url, html)

    download_jpgs(title, jpgs)

def main():
    downloader(test_url)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
