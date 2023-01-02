# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BookItem(scrapy.Item):
    name = scrapy.Field()
    tags = scrapy.Field()
    score = scrapy.Field()
    cover = scrapy.Field()
    price = scrapy.Field()
