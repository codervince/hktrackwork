# -*- coding: utf-8 -*-

# Define your item pipelines here
#/Users/vmac/RACING1/HKG/scrapers/dist/hkjc
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import scrapy
import pprint
from scrapy.contrib.pipeline.images import ImagesPipeline
from scrapy.exceptions import DropItem

from collections import defaultdict
from datetime import datetime

from sqlalchemy.orm import sessionmaker, exc

from scrapy.contrib.pipeline.files import FileException
from scrapy import log
import hashlib

from hkjc.models import *
from hkjc.items import *


from sa_decorators import DBDefer

dbdefer = DBDefer(URL(**settings.DATABASE))
# metadata = MetaData(dbdefer.engine)

def_time = datetime(year=1900, month=1, day=1).time()
def_DBL = None
def_int = None

pp = pprint.PrettyPrinter(indent=4)
# class NoInRaceImagePipeLine(ImagesPipeline):

#     def set_filename(self, response):
#         #add a regex here to check the title is valid for a filename.
#         return 'full/{0}.jpg'.format(response.meta['Url'][0])

#     def get_media_requests(self, item, info):
#         for image_url in item['image_urls']:
#             # yield scrapy.Request(image_url, meta={'url': item['url']})
#             yield scrapy.Request(image_url)

#     def get_images(self, response, request, info):
#         for key, image, buf in super(NoInRaceImagePipeLine, self).get_images(response, request, info):
#             key = self.set_filename(response)
#         yield key, image, buf

def getLBW(lbw, place, LBWFirst):
    if place == 1:
        return LBWFirst
    else:
        return lbw

def getnosectionals(distance):
    if distance is None or distance == 0:
        return 0
    else:
        return {
        '1000': 3,
        '1100': 3,
        '1200': 3,
        '1400': 4,
        '1500': 4,
        '1600': 4,
        '1650': 4,
        '1700': 5,
        '1750': 5,
        '1800': 5,
        '1900': 5,
        '2000': 6,
        '2200': 6,
        '2400': 6
        }.get(str(distance),0)

def gethorseprize(placenum, prizemoney):
    # print (place, float(prizemoney))
    if placenum is None or prizemoney is None:
        return None
    # print (place, prizemoney)
    return {
        '1': float(57.0*float(prizemoney))/100.0,
        '2': float(22.0*float(prizemoney))/100.0,
        '3': float(11.5*float(prizemoney))/100.0,
        '4': float(6.0*float(prizemoney))/100.0,
        '5': float(3.5*float(prizemoney))/100.0
    }.get(str(placenum), 0.0)
#inraceimage one per race
# @dbdefer
class MyImagesPipeline(ImagesPipeline):
   
    def file_path(self, request, response=None, info=None):
        #item=request.meta['item'] # Like this you can use all from item, not just url.
        #http://www.hkjc.com/english/racing/finishphoto.asp?racedate=20141220R1_L.jpg
        image_id = request.url.split('/')[-1]
        # image_id = request.meta.get('Inracename')
        #get name
        return 'full/%s' % (image_id)
    # def set_filename(self, response):
    #     # pp.pprint(response.meta)
    #     theurl = response.meta["RacecourseCode"][0] + response.meta["RaceDate"][0] + response.meta["RaceNumber"][0]
    #     #add a regex here to check the title is valid for a filename.
    #     return 'full/{0}.jpg'.format(theurl)   

    # def get_images(self, response, request, info):
    #     for key, image, buf in super(MyImagesPipeLine, self).get_images(response, request, info):
    #         key = self.set_filename(response)
    #     yield key, image, buf

    def get_media_requests(self, item, info):
        try:
            for image in item['image_urls']:
                yield scrapy.Request(image)
        except:
            None        

    def item_completed(self, results, item, info):
        image_urls = [x['url'] for ok,x in results if ok]
        if not image_urls:
            raise DropItem("no images in this item: sucks")
        item['image_urls'] = image_urls
        return item 


class SQLAlchemyPipeline(object):
    def __init__(self):
        engine = get_engine()
        create_schema(engine)

        self.Session = sessionmaker(bind=engine)
        self.cache = defaultdict(lambda: defaultdict(lambda: None))
        # metadata = sa.MetaData(dbdefer.engine) 
        # TODO: get horsecolors!
    # @dbdefer    
    def process_item(self, item, spider):
        if not isinstance(item, (HorseItem, ResultsItem)):
            return item

        session = self.Session()
        if isinstance(item, HorseItem):
            trackwork = HKTrackwork(EventDate=item["EventDate"],
                                    EventVenue=item["EventVenue"],
                                    EventDescription=item["EventDescription"],
                                    # ImportType=item["ImportType"],
                                    # SireName=item["SireName"],
                                    # DamName=item["DamName"],
                                    # DamSireName=item["DamSireName"],
                                    EventTypeid=self.get_id(session, EventType, "Name", {"Name": item["EventType"]}),
                                    Ownerid=self.get_id(session, Owner, "Name",
                                                        {"Name": item["Owner"], "Homecountry": item["Homecountry"]}),
                                    Gearid=self.get_id(session, Gear, "Name", {"Name": item["Gear"]}),
                                    Horseid=self.get_id(session, Horse, "Code",
                                                        {"Code": item["HorseCode"], "Name": item["HorseName"], \
                                                         "Homecountry": item["Homecountry"], \
                                                         "SireName": item["SireName"], "DamName": item["DamName"], \
                                                         "DamSireName": item["DamSireName"],
                                                         "ImportType": item["ImportType"]
                                                        }))

        if isinstance(item, ResultsItem):


            # racework = HKRace(
            #     Url=item["Url"],
            #     RacecourseCode = item["RacecourseCode"],
            #     RaceNumber =  item["RaceNumber"],       
            #     Prizemoney = item["Prizemoney"],
            #     Raceratingspan = item.get("Raceratingspan", None),
            #     Surface=item["Surface"],
            #     IncidentReport = item["IncidentReport"],
            #     RaceIndex = item["RaceIndex"],
            #     PublicRaceIndex = item["RacecourseCode"] + item["RaceDate"] + item["RaceNumber"],
            #     Raceclassid= self.get_id(session, Raceclass, "Name", {"Name": item["Raceclass"]}),
            #     Railtypeid = self.get_id(session, Railtype, "Name", {"Name": item["Railtype"]}),
            #     Goingid = self.get_id(session, Going, "Name", {"Name": item["Going"]}),
            #     Distanceid = self.get_id(session, Distance, "MetricName", {"MetricName": int(item["Distance"]),"Miles": float(float(item["Distance"])/1600.0),
            #         "Furlongs": int(int(item["Distance"])/200) })
                
            #     )



            trackwork = HKRunner(
                                # Raceid =self.get_id(session, HKRace, "PublicRaceIndex", {"PublicRaceIndex": item["RacecourseCode"] + item[
                                                                                       # "RaceDate"] + item["RaceNumber"]}),

                                Raceid=self.get_id(session, HKRace, "PublicRaceIndex", {
                                                                                   "Url": item.get("Url", None),
                                                                                   "RacecourseCode": item["RacecourseCode"],
                                                                                   "RaceDate": item["RaceDate"],
                                                                                   "Name": item["Name"],
                                                                                   # "Inraceimage": item["images"],
                                                                                   # "Inraceimage": item["images"][0]['data'],
                                                                                   "RaceNumber": int(item["RaceNumber"]),
                                                                                   "Prizemoney": item.get("Prizemoney", None),
                                                                                   "Raceratingspan": item.get("Raceratingspan", None),
                                                                                   "Surface": item.get("Surface", None),
                                                                                   "IncidentReport": item.get("IncidentReport", None),
                                                                                   "RaceIndex": item.get("RaceIndex", None),
                                                                                   "Dayofweek": item.get("Dayofweek", None),
                                                                                   "NoSectionals": getnosectionals(item.get("Distance", 0)),
                                                                                   # "Winodds": item["Winodds"],
                                                                                   "PublicRaceIndex": item["RacecourseCode"] +
                                                                                       item["RaceDate"] + str(item["RaceNumber"]),
                                                                                    "Raceclassid": self.get_id(session, Raceclass, "Name", {"Name": item.get("Raceclass", None)}),
                                                                                    "Railtypeid": self.get_id(session, Railtype, "Name", {"Name": item.get("Railtype", None)}),
                                                                                    "Goingid": self.get_id(session, Going, "Name", {"Name": item.get("Going", None)}),
                                                                                    "Distanceid": 
                                                                                        self.get_id(session, Distance, "MetricName", {"MetricName": int(item.get("Distance", 0)     ),
                                                                                    "Miles": float(float(item.get("Distance", 0)    )/1600.0),
                                                                                    "Furlongs": int(int(item.get("Distance", 0))/200)

                                    }),
                                       "HKDividendid": 
                                       self.get_id(session, HKDividend, "PublicRaceIndex", {
                                        "RaceDate": item["RaceDate"], "RaceNumber": item["RaceNumber"],
                                        "RacecourseCode": item.get("RacecourseCode", None),
                                         "PublicRaceIndex": item["RacecourseCode"] + item["RaceDate"] + str(item["RaceNumber"]),
                                       "WinDiv": item.get("WinDiv", None), "Place1Div":item.get("Place1Div"), "Place2Div": item.get("Place2Div", None), "Place3Div":item.get("Place3Div", None),
                                        "QNDiv": item.get("QNDiv", None), "QP12Div": item.get("QP12Div"), "QP13Div": item.get("QP13Div", None), "QP23Div": item.get("QP23Div", None),  
                                        "TierceDiv": item.get("TierceDiv"), "TrioDiv": item.get("TrioDiv", None), "FirstfourDiv": item.get("FirstfourDiv", None), "QuartetDiv": item.get("QuartetDiv", None),
                                        "ThisDouble11Div": item.get("ThisDouble11Div", None), "ThisDouble12Div": item.get("ThisDouble12Div",None),"Treble111Div": item.get("Treble111Div", None), 
                                        "Treble112Div": item.get("Treble112Div",None),
                                        "ThisDoubleTrioDiv": item.get("ThisDoubleTrioDiv", None), "TripleTrio111Div": item.get("TripleTrio111Div", None),
                                         "TripleTrio112Div": item.get("TripleTrio112Div", None), "SixUpDiv": item.get("SixUpDiv", None), "SixUpBonusDiv": item.get("SixUpBonusDiv", None)

                                       })

                                                                                       }),
                                 Horseid=self.get_id(session, Horse, "Code",
                                                     {"Code": item["HorseCode"], "Name": item["Horse"],
                                                      "Homecountry": "HKG"}),

                                 # Raceclassid=self.get_id(session, Raceclass, "Name", {"Name": item["Raceclass"]}),
                                 # Railtypeid=self.get_id(session, Railtype, "Name", {"Name": item["Railtype"]}),
                                 # Goingid=self.get_id(session, Going, "Name", {"Name": item["Going"]}),
                                 # Distanceid=self.get_id(session, Distance, "MetricName", {"MetricName": int(item["Distance"]),
                                                                                    # "Miles": float(float(item["Distance"])/1600.0),
                                                                                    # "Furlongs": int(int(item["Distance"])/200)

                                    # }), 
                                 HorseNumber=item.get("HorseNumber", def_int),
                                 Jockeyid=self.get_id(session, Jockey, "Name",
                                                      {"Name": item["Jockey"], "Homecountry": "HKG"}),
                                 Trainerid=self.get_id(session, Trainer, "Name",
                                                       {"Name": item["Trainer"], "Homecountry": "HKG"}),
                                 Jockey=item["Jockey"],
                                 Trainer=item["Trainer"],
                                 ActualWt=item["ActualWt"],
                                 DeclarHorseWt=item["DeclarHorseWt"],
                                 Draw=item.get("Draw", None),
                                 LBW = item.get("LBW", None),
                                 isScratched = item.get("isScratched", None),
                                 # LBW= getLBW(item.get("LBW", None),item.get("Place", None), item.get("LBWFirst", None)),
                                 RunningPosition=item.get("RunningPosition", None),
                                 Sec1DBL=item.get("Sec1DBL", None),
                                 Sec2DBL=item.get("Sec2DBL", def_DBL),
                                 Sec3DBL=item.get("Sec3DBL", def_DBL),
                                 Sec4DBL=item.get("Sec4DBL", def_DBL),
                                 Sec5DBL=item.get("Sec5DBL", def_DBL),
                                 Sec6DBL=item.get("Sec6DBL", def_DBL),
                                 FinishTime=item.get("FinishTime", def_time),
                                 Sec1Time=item.get("Sec1time", def_time),
                                 Sec2Time=item.get("Sec2time", def_time),
                                 Sec3Time=item.get("Sec3time", def_time),
                                 Sec4Time=item.get("Sec4time", def_time),
                                 Sec5Time=item.get("Sec5time", def_time),
                                 Sec6Time=item.get("Sec6time", def_time),
                                 WinOdds=item.get("Winodds", None),
                                 HorseReport=item.get("HorseReport", None),
                                 PlaceNum = item.get("PlaceNum", None),
                                 Place = item.get("Place", None),
                                 #computations: horseprize, 
                                 Horseprize = gethorseprize(item.get("PlaceNum", None), item.get("Prizemoney", None)),
                                 PublicRaceIndex = item["RacecourseCode"] + item["RaceDate"] + str(item["RaceNumber"]) + item["Horse"]

                                 )
        #need last updated
        #do ranks and counts ru. OddsRank, Av Prizemoney Rank, ru.weightbelowtop
        #  ra. FieldSize, ra.dayofweek, ra.isnight, ru.isoace, ru.ismidfield, ru.isleader, isbackmarker, ismadeall, 
        #is favorite, isoddson, onetrickjockey NOT HK
        #LBW winners = 2nd x -1


        #(HKodds wasfavorite, 


        #do historical comparison for times table noFUPs, noFS, noMdns, noLSWS,
    
        try:
            session.add(trackwork)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

        return item

    def get_id(self, session, model, unique, fields):
        fval = fields[unique]
        id = self.cache[model][fval]
        if id is None:
            # log.msg("[%s] %s cache missed for '%s'" % (self.__class__.__name__, model, fval), logLevel=log.DEBUG)
            try:
                id = session.query(model).filter(getattr(model, unique) == fval).one().id
            except exc.NoResultFound:
                item = model(**fields)
                session.add(item)
                session.flush()
                session.refresh(item)
                id = item.id
            self.cache[model][fval] = id
        # else:
        # log.msg("[%s] %s cache hit for '%s'" % (self.__class__.__name__, model, fval), logLevel=log.DEBUG)
        return id

# @dbdefer
class ByteStorePipeline(ImagesPipeline):
  def media_downloaded(self, response, request, info):
        referer = request.headers.get('Referer')

        if response.status != 200:
            log.msg(format='File (code: %(status)s): Error downloading file from %(request)s referred in <%(referer)s>',
                    level=log.WARNING, spider=info.spider,
                    status=response.status, request=request, referer=referer)
            raise FileException('download-error')

        if not response.body:
            log.msg(format='File (empty-content): Empty file from %(request)s referred in <%(referer)s>: no-content',
                    level=log.WARNING, spider=info.spider,
                    request=request, referer=referer)
            raise FileException('empty-content')

        status = 'cached' if 'cached' in response.flags else 'downloaded'
        log.msg(format='File (%(status)s): Downloaded file from %(request)s referred in <%(referer)s>',
                level=log.DEBUG, spider=info.spider,
                status=status, request=request, referer=referer)
        self.inc_stats(info.spider, status)

        try:
            bytestr = response.body
            m = hashlib.md5()
            m.update(bytestr)
            checksum = m.hexdigest()
        except FileException as exc:
            whyfmt = 'File (error): Error processing file from %(request)s referred in <%(referer)s>: %(errormsg)s'
            log.msg(format=whyfmt, level=log.WARNING, spider=info.spider,
                    request=request, referer=referer, errormsg=str(exc))
            raise
        except Exception as exc:
            whyfmt = 'File (unknown-error): Error processing file from %(request)s referred in <%(referer)s>'
            log.err(None, whyfmt % {'request': request, 'referer': referer}, spider=info.spider)
            raise FileException(str(exc))

        return {'url': request.url, 'data': bytestr, 'checksum': checksum}
