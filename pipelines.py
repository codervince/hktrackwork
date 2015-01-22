# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from collections import defaultdict
from datetime import datetime

from sqlalchemy.orm import sessionmaker, exc

from hkjc.models import *
from hkjc.items import *

def_time = datetime(year=1900, month=1, day=1).time()
def_DBL = None 

class SQLAlchemyPipeline(object):
    def __init__(self):
        engine = get_engine()
        create_schema(engine)
        self.Session = sessionmaker(bind=engine)
        self.cache = defaultdict(lambda: defaultdict(lambda: None))

        # TODO: get horsecolors!

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
            trackwork = HKRunner(Raceid=self.get_id(session, HKRace, "RaceIndex", {"Url": item["Url"],
                                                                                   "Racecoursecode": item["Racecoursecode"],
                                                                                   "RaceDate": item["Racedate"],
                                                                                   "RaceNumber": item["Racenumber"],
                                                                                   "RaceIndex": item["Racecoursecode"] + item[
                                                                                       "Racedate"] + item["Racenumber"]}),
                                 Horseid=self.get_id(session, Horse, "Code",
                                                     {"Code": item["Horsecode"], "Name": item["Horse"],
                                                      "Homecountry": "HKG"}),
                                 HorseNo=item["HorseNo"],
                                 Jockeyid=self.get_id(session, Jockey, "Name",
                                                      {"Name": item["Jockey"], "Homecountry": "HKG"}),
                                 Trainerid=self.get_id(session, Trainer, "Name",
                                                       {"Name": item["Trainer"], "Homecountry": "HKG"}),
                                 Jockey=item["Jockey"],
                                 Trainer=item["Trainer"],
                                 ActualWt=item["ActualWt"],
                                 DeclarHorseWt=item["DeclarHorseWt"],
                                 Draw=item["Draw"],
                                 LBW=item["LBW"],
                                 RunningPosition=item.get("Runningposition", None),
                                 Sec1DBL=item.get("Sec1DBL", def_DBL),
                                 Sec2DBL=item.get("Sec2DBL", def_DBL),
                                 Sec3DBL=item.get("Sec3DBL", def_DBL),
                                 Sec4DBL=item.get("Sec4DBL", def_DBL),
                                 Sec5DBL=item.get("Sec5DBL", def_DBL),
                                 Sec6DBL=item.get("Sec6DBL", def_DBL),
                                 FinishTime=item.get("Finishtime", def_time),
                                 Sec1Time=item.get("Sec1time", def_time),
                                 Sec2Time=item.get("Sec2time", def_time),
                                 Sec3Time=item.get("Sec3time", def_time),
                                 Sec4Time=item.get("Sec4time", def_time),
                                 Sec5Time=item.get("Sec5time", def_time),
                                 Sec6Time=item.get("Sec6time", def_time),
                                 WinOdds=item.get("Winodds", None))

        session.add(trackwork)
        session.commit()
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