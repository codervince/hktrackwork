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

class ResultsItem(scrapy.Item):
    Url = scrapy.Field()
    Racecoursecode = scrapy.Field()
    Racedate = scrapy.Field()
    Racenumber = scrapy.Field()
    Place = scrapy.Field()
    HorseNo = scrapy.Field()
    Horse = scrapy.Field()
    Horsecode = scrapy.Field()
    Jockey = scrapy.Field()
    Trainer = scrapy.Field()
    ActualWt = scrapy.Field()
    DeclarHorseWt = scrapy.Field()
    Draw = scrapy.Field()
    LBW = scrapy.Field()
    Runningposition = scrapy.Field()
    Finishtime = scrapy.Field()
    Winodds = scrapy.Field()
    #sectionals page
    Sec1DBL = scrapy.Field()  #not nullable e.g. 3/4 , 1/1/4 top right of '1st Sec', '2nd Sec' box
    Sec1time = scrapy.Field() #Time object e.g. '00:00:13.24'
    Sec2DBL = scrapy.Field() #not nullable
    Sec2time = scrapy.Field() #Time object e.g. '00:00:13.24'
    Sec3DBL = scrapy.Field() #not nullable
    Sec3time = scrapy.Field() #Time object e.g. '00:00:13.24'
    Sec4DBL = scrapy.Field() #can be null
    Sec4time = scrapy.Field()#can be null
    Sec5DBL = scrapy.Field() #can be null
    Sec5time = scrapy.Field() #can be null
    Sec6DBL = scrapy.Field() #can be null
    Sec6time = scrapy.Field() #can be null