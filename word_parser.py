from bs4 import BeautifulSoup
import re
import requests
from word_model import Word
import ui
from urllib.request import urlretrieve


class WordParser():
    def __init__(self, config):
        self.mdbg = 'https://www.mdbg.net/chinese/'
        self.base_url = self.mdbg + 'dictionary?wdqb='
        self.charmenu_base = self.mdbg + 'dictionary-ajax?c=cdqchi&i='
        self.image_base = self.mdbg + 'rsc/img/stroke_anim/'

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
                word.strokes = self.parse_charmenu(word.hanzi)
                word.write_to_file(self.filename_out)
                break

    def parse_charmenu(self, hanzi):
        link_path = 'div.nonprintable a[title="Show stroke order"]'
        strokes = []
        for char in hanzi:
            r = requests.get(self.charmenu_base + char)
            soup = BeautifulSoup(r.text, features='lxml')

            strokes_link = soup.select_one(link_path)
            if strokes_link:
                image_name = self.get_image_name(strokes_link)
                image_link = self.image_base + image_name
                urlretrieve(image_link, image_name)
                strokes.append(image_name)
                print(strokes)
        return strokes 

    def get_image_name(self, strokes_link):
        # strokes_link example: 
        # "aj('993d54',this,'cdas',0,'22909'); trackExitLink('inline...".
        onclick = strokes_link['onclick']
        pattern = '(?<=aj\()[^)]+(?=\))'
        # aj_text: "'993d54',this,'cdas',0,'22909'".
        aj_text = re.search(pattern, onclick).group()
        parts = aj_text.split(',')
        # parts[-1]: "'22909'".
        # image_name: "22909".
        image_name = re.search('(?<=\')\d*(?=\')', parts[-1]).group()
        return '{}.gif'.format(image_name)
