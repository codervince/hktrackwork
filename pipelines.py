# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from collections import defaultdict

from sqlalchemy.orm import sessionmaker, exc

from hkjc.models import *


class SQLAlchemyPipeline(object):
    def __init__(self):
        engine = get_engine()
        create_schema(engine)
        self.Session = sessionmaker(bind=engine)
        self.cache = defaultdict(lambda: defaultdict(lambda: None))

        #TODO: get horsecolors!
    def process_item(self, item, spider):
        session = self.Session()

        trackwork = HKTrackwork(EventDate=item["EventDate"],
                                EventVenue=item["EventVenue"],
                                EventDescription=item["EventDescription"],
                                # ImportType=item["ImportType"],
                                # SireName=item["SireName"],
                                # DamName=item["DamName"],
                                # DamSireName=item["DamSireName"],
                                EventTypeid=self.get_id(session, EventType, "Name", {"Name": item["EventType"]}),
                                Ownerid=self.get_id(session, Owner, "Name", {"Name": item["Owner"], "Homecountry": item["Homecountry"]}),
                                Gearid=self.get_id(session, Gear, "Name", {"Name": item["Gear"]}),
                                Horseid=self.get_id(session, Horse, "Code",
                                                      {"Code": item["HorseCode"], "Name": item["HorseName"], \
                                                      "Homecountry": item["Homecountry"],\
                                                      "SireName": item["SireName"], "DamName": item["DamName"], \
                                                      "DamSireName": item["DamSireName"], "ImportType": item["ImportType"]          
                                                      }        ))
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