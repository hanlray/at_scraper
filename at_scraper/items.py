# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class AppItem(scrapy.Item):
    slug = scrapy.Field()
    name = scrapy.Field()
    desc_primary = scrapy.Field()

class SoftwareDetailsItem(scrapy.Item):
    slug = scrapy.Field()
    name = scrapy.Field()
    lead = scrapy.Field()
    creator_link = scrapy.Field()
    description = scrapy.Field()
    website = scrapy.Field()


class AltItem(AppItem):
    alt_to = scrapy.Field()
    rank = scrapy.Field()