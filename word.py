import scrapy


class WordItem(scrapy.Item):
    hanzi = scrapy.Field()
    pinyin = scrapy.Field()
    english = scrapy.Field()
    strokes = scrapy.Field()
    mnemonics = scrapy.Field()
    audio = scrapy.Field()
    notes = scrapy.Field()
