# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NewsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    language=scrapy.Field()
    link=scrapy.Field()
    title=scrapy.Field()
    last_modified_at=scrapy.Field()
    crawled_at=scrapy.Field()
    contents=scrapy.Field()
    pass
