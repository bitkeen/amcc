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

def yes_or_no(question):
    answer = input(question).lower()
    while answer not in ['', 'y', 'n']:
        answer = input('Wrong input.\n').lower()
    return answer in ['', 'y']
