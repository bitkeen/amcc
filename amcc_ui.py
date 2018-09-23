def clear_screen(term):
    '''Clear screen by using print without newline, with flush.'''
    print(term.clear, end='', flush=True)


class Ui:
    def __init__(self, config, term):
        self.term = term
        self.config = config

    def get_search_query(self):
        clear_screen(self.term)
        search_query = input('Enter pinyin: ')
        return search_query

    def check_item(self, word):
        '''Ask user if parsed data is good.
        Return True if user enters 'y', False if 'n'. 
        '''
        question = str(word) + '\nIs this what you\'re looking for ([y]/n)? '
        return self.yes_or_no(question)

    def ask_rewrite(self):
        clear_screen(self.term)
        question = 'Are you sure you want to rewrite the existing file ([y]/n)? '
        return self.yes_or_no(question)

    def yes_or_no(self, question):
        '''Return True if yes, else False.'''
        answer = input(question).lower()
        while answer not in ['', 'y', 'n', 'yes', 'no']:
            answer = input('Wrong input.\n').lower()
        return answer in ['', 'y', 'yes']

    def print_no_results(self):
        print('No results were found for your search query.')

    def print_image_download(self, char, image_name):
        format_str = 'Downloading strokes for {} - {}...'
        print(format_str.format(char, image_name))

    def print_audio_download(self, hanzi, audio_name):
        format_str = 'Downloading audio for {} - {}...'
        print(format_str.format(hanzi, audio_name))

    def print_search_request(self, search_url):
        format_str = 'Sending request to {}...'
        print(format_str.format(search_url))

    def print_write(self, pinyin, filename_out):
        format_str = 'Writing {} to {}...'
        print(format_str.format(pinyin, filename_out))

    def print_menu(self, items):
        # header = '{} definitions found.\n'.format(len(items))
        header = 'Select definition. Press q to exit.\n'
        menu = Menu(self.config, self.term, header, items)
        return menu.run()


class Menu:
    def __init__(self, config, term, header, items):
        try:
            self.vi_bindings = config.getint('vi_bindings')
        except:
            self.vi_bindings = 1

        self.term = term
        self.header = header

        self.selected_value = 0

        # Limit number of items: temporary measure to prevent overflow.
        # TODO: add pagination to fix this.
        self.items = items[:5]

    @property
    def selected_item(self):
        return self.selected_value

    @selected_item.setter
    def selected_item(self, value):
        '''Change the value and redraw the menu.'''
        self.selected_value = value
        self.draw()

    def run(self):
        # Hide the cursor.
        with self.term.hidden_cursor():
            self.draw()

            # Handle keypresses from the user.
            with self.term.cbreak():
                key = ''
                while key.lower() != 'q':
                    key = self.term.inkey()
                    if key.is_sequence:
                        if key.name == 'KEY_ENTER':
                            clear_screen(self.term)
                            return self.selected_item
                        elif key.name == 'KEY_UP':
                            self.item_up()
                        elif key.name == 'KEY_DOWN':
                            self.item_down()
                    elif key == 'q':
                        exit(0)
                    elif self.vi_bindings and key == 'k':
                        self.item_up()
                    elif self.vi_bindings and key == 'j':
                        self.item_down()

    def draw(self):
        '''Draw the menu with current item in selection.'''
        clear_screen(self.term)
        print(self.term.bold(self.header))
        for index, item in enumerate(self.items):
            if index == self.selected_item:
                print(self.term.white_on_blue(str(item)))
            else:
                print(item)

    def item_down(self):
        '''Move down the list.'''
        if self.selected_item < (len(self.items) - 1):
            # Go down the list.
            self.selected_item += 1
        else:
            # Go to the beginning of the list.
            self.selected_item = 0

    def item_up(self):
        '''Move up the list.'''
        if self.selected_item > 0:
            # Go up the list.
            self.selected_item -= 1
        else:
            # Go to the end of the list.
            self.selected_item = len(self.items) - 1
