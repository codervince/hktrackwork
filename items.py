# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class HorseItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    HorseCode = scrapy.Field()
    HorseName = scrapy.Field()
    EventDate = scrapy.Field()
    EventType = scrapy.Field()
    EventVenue = scrapy.Field()
    EventDescription = scrapy.Field()
    Gear = scrapy.Field()
    SireName = scrapy.Field()
    DamName = scrapy.Field()
    DamSireName = scrapy.Field()
    ImportType = scrapy.Field()
    Owner = scrapy.Field()
    Homecountry = scrapy.Field()
