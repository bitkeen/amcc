#!/usr/bin/env python
from blessed import Terminal
from scrapy.crawler import CrawlerProcess
from word_spider import WordSpider


if __name__ == '__main__':
    term = Terminal() 
    with term.fullscreen():
        filename_out = 'out.csv'
        process = CrawlerProcess({
            'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
            'LOG_LEVEL': 'ERROR',
        })
        process.crawl(WordSpider, filename_out=filename_out, term=term)
        process.start() # the script will block here until the crawling is finished
