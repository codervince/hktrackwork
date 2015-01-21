# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from collections import defaultdict

from sqlalchemy.orm import sessionmaker, exc

from hkjc.models import *

from hkjc.items import *


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
            trackwork = HKRunner(Raceid=self.get_id(session, HKRace, "id", {"Url": item["Url"],
                                                                            "Racecoursecode": item["Racecoursecode"],
                                                                            "RaceDate": item["Racedate"],
                                                                            "RaceNumber": item["Racenumber"]}),
                                 Horseid=self.get_id(session, Horse, "Code",
                                                     {"Code": item["HorseCode"], "Name": item["HorseName"],
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
                                 RunningPosition=item["RunningPosition"],
                                 Sec1DBL=item["Sec1DBL"],
                                 Sec2DBL=item["Sec2DBL"],
                                 Sec3DBL=item["Sec3DBL"],
                                 Sec4DBL=item["Sec4DBL"],
                                 Sec5DBL=item["Sec5DBL"],
                                 Sec6DBL=item["Sec6DBL"],
                                 FinishTime=item["Finishtime"],
                                 Sec1Time=item["Sec1time"],
                                 Sec2Time=item["Sec2time"],
                                 Sec3Time=item["Sec3time"],
                                 Sec4Time=item["Sec4time"],
                                 Sec5Time=item["Sec5time"],
                                 Sec6Time=item["Sec6time"],
                                 Winodds=item["WinOdds"],
            )

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