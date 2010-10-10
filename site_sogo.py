# -*- coding: utf8 -*-
import site_skm

site_index = 'sogo'
site_keyword = 'sogo'
site_url = 'http://www.sogo.com.tw/'
test_url = 'http://www.sogo.com.tw/NEWSOGO/04/flippingbook/091006_1018AWjp/index.html'

def downloader(url):
    site_skm.downloader(url)

def main():
    input = 'input_skm.txt'

    for line in open(input, 'rb'):
        line = line.strip()

        if len(line) == 0:
            # skip blank line
            continue

        if line[0] == '#':
            # skip comment
            continue

        print line
        downloader(line)


if __name__ == '__main__':
#     r = urllib2.urlopen('http://www.sogo.com.tw/NEWSOGO/04/flippingbook/091006_1018AWjp/index.html')
#     html = r.read()
#     print html
    main()
