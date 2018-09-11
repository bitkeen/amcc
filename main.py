#!/usr/bin/env python
import amcc_ui
from blessed import Terminal
from configparser import ConfigParser
import errno
import os
from word_parser import WordParser


def run_query(parser, term):
    query = amcc_ui.get_search_query(term)
    parser.run_parser(query)


def prepare_output_structure(config, term):
    (output_dir, media_dir) = (config['output_dir'], config['media_dir'])

    try:
        makedirs_path = '{}/{}'.format(output_dir, media_dir)
        os.makedirs(makedirs_path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    
    tsv_path = '{}/{}'.format(output_dir, config['output_filename'])
    if (config['file_mode'] == 'w'
            and os.path.isfile(tsv_path)
            and amcc_ui.ask_rewrite(term)):
        # Create new file instead of appending to an existing one.
        open(tsv_path, 'w').close() 


if __name__ == '__main__':
    config = ConfigParser()
    config.read('amcc.conf')
    # Select the 'main' section from the config file.
    config = config['main']

    term = Terminal() 
    with term.fullscreen():
        prepare_output_structure(config, term)

        parser = WordParser(config)
        run_query(parser, term)

        question = '\nOne more query ([y]/n)? '
        while amcc_ui.yes_or_no(question):
            run_query(parser, term)
