class Word:
    def __init__(self):
        self.hanzi = ''
        self.pinyin = ''
        self.english = ''
        self.strokes = []
        self.mnemonics = ''
        self.audio = ''
        self.notes = ''

    def __str__(self):
        format_str = '{} ({}) - {}\n'
        return format_str.format(self.hanzi, self.pinyin, self.english)

    def write_to_file(self, filename_out):
        '''Append the word to a tsv file.'''
        fields = (self.hanzi,
                  self.pinyin,
                  self.english,
                  ''.join(self.strokes))
        with open(filename_out, 'a') as fout:
            line = '\t'.join(fields)
            fout.write(line) 
            fout.write('\n')
