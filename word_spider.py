import scrapy
from word_item import WordItem


class WordSpider(scrapy.Spider):
    name = 'word'
    base_url = 'https://www.mdbg.net/chinese/dictionary?wdqb='

    def __init__(self, filename_out):
        self.filename_out = filename_out
        self.start_urls = [self.ask_pinyin()]

    def ask_pinyin(self):
        search_query = input('Enter pinyin of the character (q to exit): ')
        if search_query.lower() != 'q':
            return self.base_url + search_query

    def parse(self, response):
        item = self.parse_mdbg(response)
        if item:
            self.write_item(item)

        next_search = self.ask_pinyin()
        if next_search:
            yield response.follow(next_search, self.parse)

    def parse_mdbg(self, response):
        '''Parse mdbg.net search results.'''
        results_table = response.css('table.wordresults')
        rows = results_table.css('tr.row')
        for row in rows:
            hanzi_css = 'td.head div.hanzi'
            pinyin_css = 'td.head div.pinyin'
            english_css = 'td.details div.defs'
            normalize = 'normalize-space()'

            item = WordItem()
            item['hanzi'] = row.css(hanzi_css).xpath(normalize).extract_first()
            item['pinyin'] = row.css(pinyin_css).xpath(normalize).extract_first()
            item['english'] = row.css(english_css).xpath(normalize).extract_first()
            if self.ask_user(item) == True:
                return item

    def ask_user(self, item):
        '''Ask user if parsed data is good.
        Return True if user enters 'y', False if 'n'. 
        '''
        text = '{} ({}) - {}\nIs this what you\'re looking for (y/n)?\n'
        text = text.format(item['hanzi'], item['pinyin'], item['english'])
        answer = input(text).lower()
        while answer not in ['y', 'n']:
            answer = input('Wrong input.\n').lower()
        return answer == 'y'

    def write_item(self, item):
        '''Append an item to a csv file.'''
        with open(self.filename, 'a') as fout:
            line = '\t'.join([item['hanzi'], item['pinyin'], item['english']])
            fout.write(line) 
            fout.write('\n')
