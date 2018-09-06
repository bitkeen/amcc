import scrapy
from word_item import WordItem


class WordSpider(scrapy.Spider):
    name = 'word'

    def __init__(self, filename_out, term):
        self.base_url = 'https://www.mdbg.net/chinese/dictionary?wdqb='
        self.ui = self.SpiderUi(term)
        self.filename_out = filename_out
        self.start_urls = [self.base_url + self.ui.get_search_query()]

    def parse(self, response):
        item = self.parse_mdbg(response)
        if item:
            self.write_item(item)

        question = '\nOne more query ([y]/n)? '
        if self.ui.yes_or_no(question):
            next_search = self.ui.get_search_query()
            yield response.follow(self.base_url+next_search, self.parse)

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
            if self.ui.check_item(item) == True:
                return item

    def write_item(self, item):
        '''Append an item to a csv file.'''
        with open(self.filename_out, 'a') as fout:
            line = '\t'.join([item['hanzi'], item['pinyin'], item['english']])
            fout.write(line) 
            fout.write('\n')

    class SpiderUi:
        def __init__(self, term):
            self.term = term

        def get_search_query(self):
            print(self.term.clear, end='', flush=True)
            search_query = input('Enter pinyin: ')
            return search_query

        def check_item(self, item):
            '''Ask user if parsed data is good.
            Return True if user enters 'y', False if 'n'. 
            '''
            question = '{} ({}) - {}\nIs this what you\'re looking for ([y]/n)? '
            question = question.format(item['hanzi'], item['pinyin'], item['english'])
            return self.yes_or_no(question)

        def yes_or_no(self, question):
            answer = input(question).lower()
            while answer not in ['', 'y', 'n']:
                answer = input('Wrong input.\n').lower()
            return answer in ['', 'y']
