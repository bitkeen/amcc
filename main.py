#!/usr/bin/env python
from amcc_ui import Ui
from blessed import Terminal
from configparser import ConfigParser
from word_parser import WordParser


if __name__ == '__main__':
    config = ConfigParser()
    config.read('amcc.conf')
    # Select the 'main' section from the config file.
    config = config['main']

    term = Terminal() 
    with term.fullscreen():
        ui = Ui(term)
        parser = WordParser(config, ui)
        parser.start()
