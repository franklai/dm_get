# -*- coding: utf8 -*-
import logging


sites = [
    'dream', 'feds', 
    'hankyu_taipei', 
    'hanshin', 'pz', 'skm', 'sogo', 
    'citysuper',
]
def get_module_list():
    return ['site_' + site for site in sites]

modules = [__import__(x) for x in get_module_list()]
site_dict = {}
for module in modules:
    site_dict[module.site_index] = module

def main():
    input = 'input.txt'

    for line in open(input, 'rb'):
        line = line.strip()

        if len(line) == 0:
            # skip blank line
            continue

        if line[0] == '#':
            # skip comment
            continue

        print line

        for key in site_dict:
            item = site_dict[key]

            if line.find(item.site_keyword) != -1:
                item.downloader(line)


if __name__ == '__main__':
    main()
