import errno
import json
import os
import re
import requests
import time
from bs4 import BeautifulSoup
from word_model import Word
from urllib.request import urlretrieve


class WordParser():
    mdbg = 'https://www.mdbg.net/chinese/'
    base_url = mdbg + 'dictionary?wdqb='
    charmenu_base = mdbg + 'dictionary-ajax?c=cdqchi&i='
    image_base = mdbg + 'rsc/img/stroke_anim/'
    sound_base = 'https://api.soundoftext.com/sounds/'

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

        try:
            rows = results_table.select('tr.row')
        except AttributeError:
            # No results were found for the search query;
            # results_table is None.
            self.ui.print_no_results()
            return

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

        # Download stroke animations.
        selected.strokes = self.download_strokes(selected.hanzi)

        # Download pronunciation audio.
        selected.audio = self.download_audio(selected.hanzi)

        self.ui.print_write(selected.pinyin, self.filename_out)
        selected.write_to_file(self.tsv_path)

    def download_strokes(self, hanzi):
        '''Find and download stroke animations.
        Return an array of image tags to be inserted in the output file.
        '''
        link_path = 'div.nonprintable a[title="Show stroke order"]'
        strokes = []
        for char in hanzi:
            r = requests.get(self.charmenu_base + char)
            soup = BeautifulSoup(r.text, features='lxml')

            strokes_link = soup.select_one(link_path)
            if strokes_link:
                image_filename = self.get_image_filename(strokes_link)
                image_path = '{}/{}'.format(self.media_path, image_filename)
                image_tag = '<img src="{}">'.format(image_filename)
                image_link = self.image_base + image_filename

                self.ui.print_image_download(char, image_filename)
                urlretrieve(image_link, image_path)
                strokes.append(image_tag)
        return strokes 

    def get_image_filename(self, strokes_link):
        '''Parse a JS line derived from the original HTML to get
        the name of the strokes animation that will be downloaded.
        '''
        # Example of variable values:
        # strokes_link: 
        # "aj('993d54',this,'cdas',0,'22909'); trackExitLink('inline...".
        # aj_text: "'993d54',this,'cdas',0,'22909'".
        # parts[-1]: "'22909'".
        # image_filename: "22909".
        onclick = strokes_link['onclick']
        pattern = '(?<=aj\()[^)]+(?=\))'
        aj_text = re.search(pattern, onclick).group()
        parts = aj_text.split(',')
        image_filename = re.search('(?<=\')\d*(?=\')', parts[-1]).group()
        return '{}.gif'.format(image_filename)

    def download_audio(self, hanzi):
        '''Download audio pronunciation file for the word.
        Use api.soundoftext.com which retrieves the audio generated
        by Google Translate.
        '''
        payload = {
                      'engine': 'Google',
                      'data': {
                          'text': hanzi,
                          'voice': 'cmn-Hant-TW'
                      }
                  }
        # Send a post request to get the id of audio file.
        r = requests.post(self.sound_base, json=payload)
        try:
            r.raise_for_status()
        except requests.HTTPError as e:
            message = 'Error. There was a problem with the request.' 
            message += 'Status code: ' + str(e)
            print(message)
            return

        try:
            response_json = json.loads(r.text)
            if response_json['success'] == True:
                sound_id = response_json['id']
                audio_link = self.get_sound_from_id(sound_id)

                audio_filename = audio_link.split('/')[-1]
                audio_path = '{}/{}'.format(self.media_path, audio_filename)
                audio_tag = '[sound:{}]'.format(audio_filename)

                self.ui.print_audio_download(hanzi, audio_filename)
                urlretrieve(audio_link, audio_path)
                return audio_tag
            else:
                raise Exception('Error. {}'.format(response_json['message']))
        except Exception as e:
            print(e)

    def get_sound_from_id(self, sound_id):
        '''Return url of the sound to be downloaded.'''
        request_url = self.sound_base + sound_id
        r = requests.get(request_url)
        response_json = json.loads(r.text)

        # Wait until the sound is ready.
        while response_json['status'] == 'Pending':
            r = requests.get(request_url)
            response_json = json.loads(r.text)
            time.sleep(1)

        if response_json['status'] == 'Done':
            return response_json['location']
        elif response_json['status'] == 'Error':
            message = 'Error. ' + response_json['message']
            raise Exception(message)

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
