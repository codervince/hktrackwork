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
    RacecourseCode = scrapy.Field()
    RaceDate = scrapy.Field()
    RaceNumber = scrapy.Field()
    Name = scrapy.Field()
    Place = scrapy.Field()
    HorseNumber = scrapy.Field()
    Horse = scrapy.Field()
    HorseCode = scrapy.Field()
    Jockey = scrapy.Field()
    Trainer = scrapy.Field()
    ActualWt = scrapy.Field()
    DeclarHorseWt = scrapy.Field()
    Draw = scrapy.Field()
    LBW = scrapy.Field()
    RunningPosition = scrapy.Field()
    FinishTime = scrapy.Field()
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
    RaceIndex = scrapy.Field()
    RaceName = scrapy.Field()
    Going = scrapy.Field()
    Prizemoney = scrapy.Field()
    Raceratingspan = scrapy.Field()
    Surface = scrapy.Field()
    Railtype = scrapy.Field()
    Raceclass = scrapy.Field()
    Distance = scrapy.Field()
    HorseReport = scrapy.Field()
    IncidentReport = scrapy.Field()
    image_urls = scrapy.Field()
    images = scrapy.Field()
    Inracename = scrapy.Field()
    WinDiv = scrapy.Field()
    Place1Div = scrapy.Field()
    Place2Div = scrapy.Field()
    Place3Div = scrapy.Field()
    QNDiv = scrapy.Field()
    QP12Div = scrapy.Field()
    QP13Div = scrapy.Field()
    QP23Div = scrapy.Field()
    TierceDiv = scrapy.Field()
    TrioDiv = scrapy.Field()
    QuartetDiv = scrapy.Field()
    FirstfourDiv = scrapy.Field()
    ThisDouble11Div = scrapy.Field()
    ThisDouble12Div = scrapy.Field()
    Treble111Div = scrapy.Field()
    Treble112Div= scrapy.Field()
    ThisDoubleTrioDiv = scrapy.Field()
    TripleTrio111Div = scrapy.Field()
    TripleTrio112Div = scrapy.Field()
    SixUpDiv = scrapy.Field()
    SixUpBonusDiv = scrapy.Field()
    #public race index is an artifical field 


class RaceItem(scrapy.Item):
    Racereplay = scrapy.Field()
    #image_urls = scrapy.Field()
    #images = scrapy.Field()
    # File_urls = scrapy.Field()
    # files = scrapy.Field()





    # QNDiv = Column(Float, nullable=True)
    # QP12Div = Column(Float, nullable=True)
    # QP13Div = Column(Float, nullable=True)
    # QP23Div = Column(Float, nullable=True)
    # TierceDiv = Column(Float, nullable=True)
    # TrioDiv = Column(Float, nullable=True)
    # FirstfourDiv = Column(Float, nullable=True)
    # #optionals
    # QuartetDiv = Column(Float)
    # ThisDouble11Div = Column(Float)
    # ThisDouble12Div = Column(Float)
    # Treble111Div = Column(Float)
    # Treble112Div = Column(Float)
    # ThisDoubleTrioDiv = Column(Float)
    # TripleTrio111Div = Column(Float)
    # TripleTrio112Div = Column(Float)
    # SixUpDiv = Column(Float)
