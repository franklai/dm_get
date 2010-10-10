import os
import re
import struct
from threading import Thread
import urllib
import urllib2
import urlparse
import zlib

site_index = 'hanshin'
site_keyword = 'hanshin'
site_url = 'http://www.hanshinarena.com.tw/'
test_url = 'http://www.hanshinarena.com.tw/03-2/n_list01.php?m_id=137'

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
    pos = url.find('=')
    title = url[pos + 1:]

    html = get_content_by_url(url)
    html = html.decode('utf8')

    pattern = '<div align="center"><strong>([^<]+)</strong></div>'
    title += get_first_match(pattern, html)
    print title

    return title

def get_swfs(url):
    html = get_content_by_url(url)
    html = html.decode('utf8')

    pattern = "ursor:hand onClick=\"MM_openBrWindow\('([^']+)'"
    swfs = re.compile(pattern).findall(html)

    swfs = [urlparse.urljoin(url, swf) for swf in swfs]

    return swfs

def get_jpgs(url):
    html = get_content_by_url(url)

    pattern = 'img src="([^"]+)"'
    imgs = re.compile(pattern).findall(html)

    full_imgs = [urlparse.urljoin(url, img.replace('S.jpg', 'B.jpg')) for img in imgs]

    return full_imgs


class DownloadFile(Thread):
    def __init__(self, url, path):
        Thread.__init__(self)
        self.url = url
        self.path = path

    def run(self):
        urllib.urlretrieve(self.url, self.path)

def download_swfs(title, swfs):
    cwd = os.getcwdu()

    path_prefix = os.path.join(cwd, title, 'SWFs')

    if not os.path.exists(path_prefix):
        # mkdir if directory not exists
        os.makedirs(path_prefix)

    length = len(swfs)
    index = 0
    print('Start to downloading %s (total: %d)' % (title.encode('big5'), length))

    local_files = []

    for swf in swfs:
        index += 1

        pos = swf.rfind('/')
        filename = swf[pos + 1:]

        path = os.path.join(path_prefix, filename)

        if os.path.exists(path) and os.path.getsize(path) > 0:
            print('(%d/%d) skip %s, already exists' % (index, length, path,))
            continue

        task = DownloadFile(swf, path)
        task.start()

        # wait until the thread finish
        task.join()

        local_files.append(path)

        print('finish(%d/%d): %s' % (index, length, path,))
        
    return local_files

def extract_jpg_from_swf(local_files):
    if len(local_files) == 0:
        return

    path_prefix = os.path.dirname(local_files[0]).replace('SWFs', 'JPGs')

    if not os.path.exists(path_prefix):
        # mkdir if directory not exists
        os.makedirs(path_prefix)

    for swf in local_files:
        bytes = open(swf, 'rb').read()
        
        if bytes[0:3] == 'CWS':
            compressed_str = bytes[8:]
            uncompressed_str = zlib.decompress(compressed_str)

            mark = struct.pack('BBBB', 0xFF, 0xD8, 0xFF, 0xE0)
            pos = uncompressed_str.find(mark)

            length_bytes = uncompressed_str[pos - 6: pos - 2]
            length = struct.unpack('<I', length_bytes)[0]
            length -= 2

            jpg_path = os.path.join(path_prefix, os.path.split(swf)[1])
            jpg_path = jpg_path[:jpg_path.rfind('.')] + '.jpg'

            open(jpg_path, 'wb').write(uncompressed_str[pos:pos+length])

#         open('un.swf', 'wb').write(uncompressed_str)

def downloader(url):
    title = get_title(url)

    swfs = get_swfs(url)

    local_files = download_swfs(title, swfs)

    extract_jpg_from_swf(local_files)

def main(input):
    for line in open(input, 'rb'):
        line = line.strip()

        if len(line) == 0:
            # skip blank line
            continue

        if line[0] == '#':
            # skip comment
            continue

        downloader(line)


if __name__ == '__main__':
    input = 'input_hanshin.txt'
    main(input)

