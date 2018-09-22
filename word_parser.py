import errno
import os
import re
import requests
from bs4 import BeautifulSoup
from word_model import Word
from urllib.request import urlretrieve


class WordParser():
    mdbg = 'https://www.mdbg.net/chinese/'
    base_url = mdbg + 'dictionary?wdqb='
    charmenu_base = mdbg + 'dictionary-ajax?c=cdqchi&i='
    image_base = mdbg + 'rsc/img/stroke_anim/'

    def __init__(self, config, ui):
        self.output_dir = config['output_dir']
        self.media_dir = config['media_dir']
        self.file_mode = config['file_mode']
        self.filename_out = config['output_filename']
        self.max_defs = config.getint('max_definitions')
        self.ui = ui

    @property
    def media_path(self):
        return '{}/{}'.format(self.output_dir, self.media_dir)

    @property
    def tsv_path(self):
        return '{}/{}'.format(self.output_dir, self.filename_out)

    def start(self):
        '''Run the parser in an infinite loop until the user chooses
        to stop.
        '''
        self.prepare_output_structure()

        while True:
            self.run_once()
            if self.ui.yes_or_no('\nOne more query ([y]/n)? ') == False:
                break

    def run_once(self):
        '''Parse mdbg.net search results.'''
        # Get query from the user; compose the search url.
        query = self.ui.get_search_query()
        search_url = self.base_url + query

        self.ui.print_search_request(search_url)
        r = requests.get(search_url)
        soup = BeautifulSoup(r.text, features='lxml')

        results_table = soup.select_one('table.wordresults')
        rows = results_table.select('tr.row')

        hanzi_css = 'td.head div.hanzi'
        pinyin_css = 'td.head div.pinyin'
        english_css = 'td.details div.defs'

        words = []
        for row in rows:
            word = Word()
            word.hanzi = row.select_one(hanzi_css).text
            word.pinyin = row.select_one(pinyin_css).text
            # Get all definitions.
            definitions = row.select_one(english_css).text
            # Write no more than max_defs definitions.
            word.english = '/'.join(definitions.split('/')[:self.max_defs])
            words.append(word)

        selected_index = self.ui.print_menu(words)
        selected = words[selected_index]
        selected.strokes = self.get_strokes(selected.hanzi)

        self.ui.print_write(selected.pinyin, self.filename_out)
        selected.write_to_file(self.tsv_path)

    def get_strokes(self, hanzi):
        '''Find and download stroke animations.'''
        link_path = 'div.nonprintable a[title="Show stroke order"]'
        strokes = []
        for char in hanzi:
            r = requests.get(self.charmenu_base + char)
            soup = BeautifulSoup(r.text, features='lxml')

            strokes_link = soup.select_one(link_path)
            if strokes_link:
                image_name = self.get_image_name(strokes_link)
                image_path = '{}/{}'.format(self.media_path, image_name)
                image_tag = '<img src="{}">'.format(image_name)
                image_link = self.image_base + image_name

                self.ui.print_download(image_name, char)
                urlretrieve(image_link, image_path)
                strokes.append(image_tag)
        return strokes 

    def get_image_name(self, strokes_link):
        '''Parse a JS line derived from the original HTML to get
        the name of the strokes animation that will be downloaded.
        '''
        # Example of variable values:
        # strokes_link: 
        # "aj('993d54',this,'cdas',0,'22909'); trackExitLink('inline...".
        # aj_text: "'993d54',this,'cdas',0,'22909'".
        # parts[-1]: "'22909'".
        # image_name: "22909".
        onclick = strokes_link['onclick']
        pattern = '(?<=aj\()[^)]+(?=\))'
        aj_text = re.search(pattern, onclick).group()
        parts = aj_text.split(',')
        image_name = re.search('(?<=\')\d*(?=\')', parts[-1]).group()
        return '{}.gif'.format(image_name)

    def prepare_output_structure(self):
        '''Create the necessary output directories and files depending
        on the config file.
        '''
        try:
            os.makedirs(self.media_path)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        
        if (self.file_mode == 'w'
                and os.path.isfile(self.tsv_path)
                and self.ui.ask_rewrite()):
            # Create new file instead of appending to an existing one.
            open(self.tsv_path, 'w').close() 
