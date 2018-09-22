def clear_screen(term):
    # print without newline, with flush
    print(term.clear, end='', flush=True)


def print_formatted(*args, format_str):
    message = format_str.format(*args)
    print(message)


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
        while answer not in ['', 'y', 'n']:
            answer = input('Wrong input.\n').lower()
        return answer in ['', 'y']

    def print_no_results(self):
        print('No results were found for your search query.')

    def print_download(self, image_name, char):
        format_str = 'Downloading {} for {}...'
        print_formatted(image_name, char, format_str=format_str)

    def print_search_request(self, search_url):
        format_str = 'Sending request to {}...'
        print_formatted(search_url, format_str=format_str)

    def print_write(self, pinyin, filename_out):
        format_str = 'Writing {} to {}...'
        print_formatted(pinyin, filename_out, format_str=format_str)

    def print_menu(self, items):
        header = 'Select definition. Press q to exit.\n'
        menu = Menu(self.config, self.term, header, items)
        return menu.run()


class Menu:
    def __init__(self, config, term, header, items):
        try:
            self.vi_bindings = config.getint('vi_bindings')
        except:
            self.vi_bindings = 1

        self.current_item = 0
        self.term = term
        self.header = header
        # Limit number of items: temporary measure to prevent overflow.
        # TODO: add pagination to fix this.
        self.items = items[:5]

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
                            return self.current_item
                        elif key.name == 'KEY_UP':
                            self.item_up()
                        elif key.name == 'KEY_DOWN':
                            self.item_down()
                    elif key and self.vi_bindings:
                        if key == 'k':
                            self.item_up()
                        elif key == 'j':
                            self.item_down()

    def draw(self):
        '''Draw the menu with current item in selection.'''
        clear_screen(self.term)
        print(self.term.bold(self.header))
        for index, item in enumerate(self.items):
            if index == self.current_item:
                print(self.term.white_on_blue(str(item)))
            else:
                print(item)

    def item_down(self):
        '''Move down the list.'''
        if self.current_item < (len(self.items) - 1):
            # Go down the list.
            self.current_item += 1
            self.draw()
        else:
            # Go to the beginning of the list.
            self.current_item = 0
            self.draw()

    def item_up(self):
        '''Move up the list.'''
        if self.current_item > 0:
            # Go up the list.
            self.current_item -= 1
            self.draw()
        else:
            # Go to the end of the list.
            self.current_item = len(self.items) - 1
            self.draw()
