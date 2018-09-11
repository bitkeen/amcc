#!/usr/bin/env python
from blessed import Terminal
from configparser import ConfigParser
from word_parser import WordParser
import amcc_ui


def run_query(parser, term):
    query = amcc_ui.get_search_query(term)
    parser.run_parser(query)


if __name__ == '__main__':
    config = ConfigParser()
    config.read('amcc.conf')
    # Select the 'main' section from the config file.
    config = config['main']

    term = Terminal() 
    with term.fullscreen():
        parser = WordParser(config)
        run_query(parser, term)

        question = '\nOne more query ([y]/n)? '
        while amcc_ui.yes_or_no(question):
            run_query(parser, term)
