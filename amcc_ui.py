def get_search_query(term):
    # print without newline, with flush
    print(term.clear, end='', flush=True)
    search_query = input('Enter pinyin: ')
    return search_query

def check_item(word):
    '''Ask user if parsed data is good.
    Return True if user enters 'y', False if 'n'. 
    '''
    question = str(word) + '\nIs this what you\'re looking for ([y]/n)? '
    return yes_or_no(question)

def ask_rewrite(term):
    # print without newline, with flush
    print(term.clear, end='', flush=True)
    question = 'Are you sure you want to rewrite the existing file ([y]/n)? '
    return yes_or_no(question)

def yes_or_no(question):
    answer = input(question).lower()
    while answer not in ['', 'y', 'n']:
        answer = input('Wrong input.\n').lower()
    return answer in ['', 'y']

def print_formatted(*args, format_str):
    message = format_str.format(*args)
    print(message)

def print_download(image_name, char):
    format_str = 'Downloading {} for {}...'
    print_formatted(image_name, char, format_str=format_str)

def print_search_request(search_url):
    format_str = 'Sending request to {}...'
    print_formatted(search_url, format_str=format_str)

def print_write(pinyin, filename_out):
    format_str = 'Writing {} to {}...'
    print_formatted(pinyin, filename_out, format_str=format_str)
