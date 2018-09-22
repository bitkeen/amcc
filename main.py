#!/usr/bin/env python
from amcc_ui import Ui
from blessed import Terminal
from configparser import ConfigParser
from word_parser import WordParser


if __name__ == '__main__':
    config = ConfigParser()
    config.read('amcc.conf')
    # Select the 'main' section from the config file.
    parser_config = config['main']
    ui_config = config['ui']


    term = Terminal() 
    with term.fullscreen():
        ui = Ui(ui_config, term)
        parser = WordParser(parser_config, ui)
        parser.start()
