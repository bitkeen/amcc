def clear_screen(term):
    # print without newline, with flush
    print(term.clear, end='', flush=True)


def print_formatted(*args, format_str):
    message = format_str.format(*args)
    print(message)


class Ui:
    def __init__(self, term):
        self.term = term

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
        header = 'Select definition. Press q to exit.'
        menu = Menu(self.term, header, items)
        return menu.run()


class Menu:
    def __init__(self, term, header, items):
        self.current_item = 0
        self.term = term
        self.header = header
        # Limit number of items: temporary measure to prevent overflow.
        # TODO: add pagination to fix this.
        self.items = items[:5]

    def run(self):
        self.draw()

        # Handle keypresses from the user.
        with self.term.cbreak():
            val = ''
            while val.lower() != 'q':
                val = self.term.inkey()
                if val.is_sequence:
                    if val.name == 'KEY_ENTER':
                        clear_screen(self.term)
                        return self.current_item
                    elif val.name == 'KEY_UP':
                        self.item_up()
                    elif val.name == 'KEY_DOWN':
                        self.item_down()
                elif val:
                    if val == 'k':
                        self.item_up()
                    elif val == 'j':
                        self.item_down()

    def draw(self):
        clear_screen(self.term)
        print(self.header)
        for index, item in enumerate(self.items):
            if index == self.current_item:
                print(self.term.bright_red_on_bright_yellow(str(item)))
            else:
                print(item)

    def item_down(self):
        if self.current_item < (len(self.items) - 1):
            # Go down the list.
            self.current_item += 1
            self.draw()
        else:
            # Go to the beginning of the list.
            self.current_item = 0
            self.draw()

    def item_up(self):
        if self.current_item > 0:
            # Go up the list.
            self.current_item -= 1
            self.draw()
        else:
            # Go to the end of the list.
            self.current_item = len(self.items) - 1
            self.draw()
