# coding: utf-8
import logging
import urlparse

import common
import requests

site_index = 'dream'
site_keyword = 'dream-mall'
site_url = 'http://www.dream-mall.com.tw/'
test_url = 'http://www.dream-mall.com.tw/EDM'

class Parser:
    def __init__(self, url):
        self.url = url
        self.s = requests.Session()

        self.site = 'www.dream-mall.com.tw'
        self.is_dream_mall = True

        url = 'http://%s/' % (self.site, )
        self.s.get(url)

    def switch_to_hankyu(self):
        url = 'http://%s/Home/ChangeIsDM?isDreamMall=false' % (self.site, )
        self.s.get(url)
        self.is_dream_mall = False

    def get_guids(self):
        url = 'http://%s/EDM/' % (self.site, )
        r = self.s.get(url)
        html = r.text

        pattern = 'data-guid="(.*?)"'
        guids = common.get_all_matched(pattern, html)

        logging.debug('guids: %s' % (repr(guids), ))

        return guids

    def get_page_by_guid(self, guid):
        url = 'http://%s/Edm/Detail' % (self.site, )

        r = self.s.post(url, {'guid': guid})

        return r.text

    def get_title(self, html):
        pattern = '<h3>(.*?)</h3>'

        dm_title = common.get_first_match(pattern, html)

        if self.is_dream_mall:
            store = u'夢時代'
        else:
            store = u'統一阪急高雄店'

        title = u'%s - %s' % (store, dm_title)
        title = title.strip()

        return title
    
    def get_jpgs(self, html):
        pattern = '(/Upload/EDM/[^"]+/large_[0-9]+.jpg)'

        jpgs = common.get_all_matched(pattern, html)

        url_prefix = 'http://%s' % (self.site)
        full_jpgs = [urlparse.urljoin(url_prefix, jpg) for jpg in jpgs]
        logging.debug('full_jpgs:' + repr(full_jpgs))

        return full_jpgs

def downloader(url):
    # dreammall use ajax based to show dm, so cannot find out dm from url
    # so we just download all dm

    # this request is to get cookie
    parser = Parser(url)

    def run_download():
        guids = parser.get_guids()

        for guid in guids:
            html = parser.get_page_by_guid(guid)
            title = parser.get_title(html)
            jpgs = parser.get_jpgs(html)

            common.download_jpgs(title, jpgs)

    run_download() # for dreammall

    parser.switch_to_hankyu()
    run_download() # for hankyu kaohsiung

def main():
    url = test_url
    url = ''
    downloader(url)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
