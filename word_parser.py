from bs4 import BeautifulSoup
import requests
from word_model import Word
import ui


class WordParser():
    def __init__(self, config):
        self.mdbg = 'https://www.mdbg.net/'
        self.base_url = self.mdbg + 'chinese/dictionary?wdqb='
        self.charmenu_base = self.mdbg + 'chinese/dictionary-ajax?c=cdqchi&i='

        self.filename_out = config['output_filename']
        self.max_defs = config.getint('max_definitions')

    def run_parser(self, query):
        '''Parse mdbg.net search results.'''
        search_url = self.base_url + query

        r = requests.get(search_url)
        soup = BeautifulSoup(r.text, features='lxml')

        results_table = soup.select_one('table.wordresults')
        rows = results_table.select('tr.row')

        hanzi_css = 'td.head div.hanzi'
        pinyin_css = 'td.head div.pinyin'
        english_css = 'td.details div.defs'

        for row in rows:
            word = Word()

            word.hanzi = row.select_one(hanzi_css).text
            word.pinyin = row.select_one(pinyin_css).text
            # Get all definitions.
            definitions = row.select_one(english_css).text
            # Write no more than max_defs definitions.
            word.english = '/'.join(definitions.split('/')[:self.max_defs])
            if ui.check_item(word) == True:
                self.write_to_file(word)
                break
                

    def write_to_file(self, word):
        '''Append a word to a tsv file.'''
        with open(self.filename_out, 'a') as fout:
            line = '\t'.join([word.hanzi, word.pinyin, word.english])
            fout.write(line) 
            fout.write('\n')
