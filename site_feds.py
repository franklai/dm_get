import logging
import urlparse
import common

site_index = 'feds'
site_keyword = 'feds'
site_url = 'http://www.feds.com.tw/'
test_url = 'http://www.feds.com.tw/store/dm.aspx?store=16&dm=20140731153420f55'

def get_title(url, html):
    # use directory as part of title
    pattern = u'<title>([^<]*)</title>'
    title = common.get_first_match(pattern, html)
    logging.debug(title)

    return title.strip()

def get_jpgs(url, html):
    pattern = '"(\.\./photo/dm/small/[^"]+)"'
    jpgs = common.get_all_matched(pattern, html)
    logging.debug('jpgs:' + repr(jpgs))

    full_jpgs = [urlparse.urljoin(url, jpg.replace('small', 'large')) for jpg in jpgs] 
    logging.debug('full_jpgs:' + repr(full_jpgs))

    return full_jpgs


def downloader(url):
    # replace url to flash book
    url = url.replace('/store/dm.aspx', '/store/book.aspx')

    logging.debug('url: %s' % (url,))
    html = common.get_content_by_url(url)
    html = html.decode('utf-8')
    title = get_title(url, html)
    jpgs = get_jpgs(url, html)

    common.download_jpgs(title, jpgs)

def main():
    downloader(test_url)


if __name__ == '__main__':
#     print urlparse.urljoin('http://asdfas.erwe/asdf/th.asp?d', '../oh/oh.htm')
    logging.basicConfig(level=logging.DEBUG)
    main()
