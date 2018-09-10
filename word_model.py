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
        return '{} ({}) - {}'.format(self.hanzi, self.pinyin, self.english)
