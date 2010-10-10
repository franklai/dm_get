import logging
import os
import re
from threading import Thread
import urllib
import urllib2
import urlparse

site_index = 'hankyu'
site_keyword = 'uni-hankyu'
site_url = 'http://www.uni-hankyu.com.tw/'
test_url = 'http://www.uni-hankyu.com.tw/onlineDM_1.asp?ID=000085'


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

    pattern = u'<td class="18"[^>]+>(.*)</td>'
    title += get_first_match(pattern, html)
    logging.debug(title.encode('big5'))

    pattern = u'<[^>]+>'
    title = re.sub(pattern, '', title)
    logging.debug(title.encode('big5'))

    # replace slash in datetime (10/8-10/21)
    title = title.replace('/', '_')
    logging.debug(title.encode('big5'))

    return title.strip()

def get_jpgs(url, html):
    pattern = u'maintain/thumbnail.aspx\?FileName=([^&]+)'
    jpgs = re.compile(pattern).findall(html)
    logging.debug('jpgs:' + repr(jpgs))

    # http://www.uni-hankyu.com.tw/maintain/Upload/DM/000085/P03.jpg
    full_jpgs = [urlparse.urljoin(url, '/maintain/%s' % (jpg,)) for jpg in jpgs]
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
    html = html.decode('big5')
    title = get_title(url, html)
    jpgs = get_jpgs(url, html)

    download_jpgs(title, jpgs)

def main():
    downloader(test_url)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
