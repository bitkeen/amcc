#!/usr/bin/env python
from blessed import Terminal
from configparser import ConfigParser
from scrapy.crawler import CrawlerProcess
from word_spider import WordSpider


if __name__ == '__main__':
    config = ConfigParser()
    config.read('amcc.conf')
    # Select the 'main' section from the config file.
    config = config['main']

    term = Terminal() 
    with term.fullscreen():
        process = CrawlerProcess({
            'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
            'LOG_LEVEL': 'ERROR',
        })
        process.crawl(WordSpider, term=term, config=config)
        process.start() # the script will block here until the crawling is finished
