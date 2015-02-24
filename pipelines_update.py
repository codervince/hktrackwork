# -*- coding: utf-8 -*-

from __future__ import print_function

import traceback
import logging
from Queue import Queue, Empty
from collections import defaultdict, Counter
import pprint

from hkjc.items import *
from hkjc.models import *

from scrapy import log
from scrapy.signalmanager import SignalManager
from scrapy.signals import spider_closed
from scrapy.xlib.pydispatch import dispatcher


from sqlalchemy impoty update, _or
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.sql.expression import ClauseElement

from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.threads import deferToThreadPool
from twisted.python.threadable import isInIOThread
from twisted.python.threadpool import ThreadPool

from StringIO import StringIO

from datetime import datetime, date

import re
import scrapy

from scrapy.contrib.pipeline.images import ImagesPipeline
from scrapy.exceptions import DropItem

# Needed for multithreading, as I remember
Session = scoped_session(sessionmaker(bind=engine))
from thesus import Tracer

def dicthash(inp):
    return tuple(sorted(inp.iteritems(), key=lambda item: item[0]))


def row2dict(row):

    if isinstance(row, dict):
        return row

    d = {}
    for column in row.__table__.columns:
        d[column.name] = str(getattr(row, column.name))

    return d


class ProfiledThreadPool(ThreadPool):

    @staticmethod
    def output_callgrind(out):
        with open('callgrind.theseus', 'ab') as f:
            f.write(out)

    def _worker(self):
        from twisted.internet import reactor
        tracer = Tracer()
        tracer.install()
        ThreadPool._worker(self)

        out = StringIO()

        tracer.write_data(out)

        reactor.callFromThread(self.output_callgrind, out.getvalue())
        out.close()
        tracer.uninstall()




def get_or_create(model, defaults=None, **kwargs):
    ''' Short get or create implementation. Like in Django.
    This can run within the thread_pool
    We don't use write scheduling here, because of very low amount of writes.
    Optimization unneeded, as I think.
    We use this function to prevent IntegrityError messages.
    '''

    defaults = defaults or {}

    session = Session()  # I'm thread safe =)

    query = session.query(model).filter_by(**kwargs)

    instance = query.first()

    created = False

    if not instance:
        params = dict(
            (k, v) for k, v in kwargs.iteritems()
            if not isinstance(v, ClauseElement))
        params.update(defaults)
        instance = model(**params)

        try:
            session.add(instance)
            session.commit()
            created = True
        except IntegrityError:
            session.rollback()
            instance = query.one()
            created = False
        except Exception:
            session.rollback()
            session.close()
            raise

    session.refresh(instance)  # Refreshing before session close
    session.close()
    return instance, created


class Reporter(object):

    def __init__(self):
        self.counters = defaultdict(lambda: Counter())
        ''' Statistical counters. You may access them directly if needed '''

        self.id_counters = defaultdict(
            lambda: defaultdict(
                lambda: set()))
        ''' More complex counter used storing item keys '''

        self._created = defaultdict(lambda: list())
        ''' All created items by type '''

        self._updated = defaultdict(lambda: list())
        ''' All updated items. Should be list of tuples '''

    def saved(self, model, item_id):
        self.id_counters['created'][model].add(item_id)

    def updated(self, model, item_id, item, old_item):
        self.id_counters['updated'][model].add(item_id)
        self._updated[model].append((item_id, item, old_item))

    def unchanged(self, model, item_id):
        self.id_counters['unchanged'][model].add(item_id)

    def get_report(self):
        out = StringIO()

        print('========== Spider report ==========', file=out)
        print(file=out)
        print('---------- Counters ---------------', file=out)

        for counter, results in self.counters.iteritems():
            print(counter, file=out)
            for modelname, count in results.iteritems():
                print('  {} - {}'.format(modelname.__name__, count), file=out)

        for counter, results in self.id_counters.iteritems():
            print(counter, file=out)
            for modelname, items in results.iteritems():
                print('  {} - {}'.format(
                    modelname.__name__, len(items)), file=out)

        print('---------- Updated objects --------', file=out)
        print(file=out)

        for counter, items in self._updated.iteritems():
            print(str(counter), file=out)

            items = sorted(items)

            for item_id, new, old in items:
                print('-----------------------------------', file=out)
                print(item_id, file=out)
                old = row2dict(old)
                for key, value in row2dict(new).iteritems():
                    old_value = old.get(key)

                    if str(old_value) != str(value):
                        print('{}: {} to {}'.format(
                            key, old_value, value), file=out)

        result = out.getvalue()
        out.close()

        return result



class DBScheduler(object):
    ''' Database operation scheduler
    We will have one or more read thread and only one write thread.
    '''

    def __init__(self, spider):
        from twisted.internet import reactor  # Imported here.inside

        self.spider = spider
        ''' Used for logging for now '''

        self.reactor = reactor
        ''' Used for thred pools '''

        engine = get_engine()
        create_schema(engine)

        self.thread_pool = ThreadPool(
            minthreads=1, maxthreads=13, name="ReadPool")

        # There should be only one pool in the write_pool
        # Never increase maxtreads value
        self.write_pool = ProfiledThreadPool(
            minthreads=1, maxthreads=1, name="WritePool")

        self.thread_pool.start()
        self.write_pool.start()

        self.signals = SignalManager(dispatcher.Any).connect(
            self.stop_threadpools, spider_closed)

        self.reporter = Reporter()
        ''' Reporer is used for statistics collection '''
        self.counters = self.reporter.counters

        self.cache = defaultdict(
            lambda: dict())

        self.write_queue = Queue()
        self.writelock = False  # Write queue mutex

    def stop_threadpools(self):
        self.thread_pool.stop()
        self.write_pool.stop()

        for line in self.reporter.get_report().splitlines():
            log.msg(line)

    def _do_save_item(self, item):
        ''' Save items one by one '''
        assert not isInIOThread()

        session = Session()

        session.add(item)

        try:
            session.commit()
            self.reporter.saved(item.__class__, item)
            result = True
        except IntegrityError as error:
            session.rollback()
            result = False
        finally:
            session.close()

        return result

    def _do_save(self):
        assert not isInIOThread()

        while not self.write_queue.empty():
            items = []

            try:
                self.writelock = True
                try:
                    while True:
                        items.append(self.write_queue.get_nowait())
                except Empty:
                    pass

                session = Session()

                try:
                    session.add_all(items)
                    session.commit()

                    # All items were unique.
                    # All of them are counted

                    for item in items:
                        self.reporter.saved(item.__class__, item)

                except IntegrityError as error:
                    # This is needed because we are calling from the thread

                    self.spider.log(
                        'Exception occured while saving objects: {}'.format(
                            error), level=log.WARNING)

                    self.spider.log(
                        traceback.format_exc(), level=log.DEBUG)

                    session.rollback()

                    self.spider.log(
                        'Saving {} items one by one'.format(len(items)))

                    for item in items:
                        # Saving items one by one
                        self._do_save_item(item)
                except Exception:
                    session.rollback()
                    raise
                finally:
                    session.close()
            finally:
                self.writelock = False

    def save(self, obj):
        ''' Save object.
        Very effective if we know, that object
        doesn't exist within the database.
        If the object already exists - ignore it.
        TODO: Maybe we need to implement strategy when
        object update will be needed on duplicate.
        '''

        self.write_queue.put(obj)

        if self.writelock:
            return None
        else:
            return deferToThreadPool(
                self.reactor, self.write_pool, self._do_save)

    def _do_update_if_changed(self, model, selector, updated):
        ''' Update model matching some *selector* dict and
        if it's changed.
        For each custom situation custom query should be built
        using *case* function.
        This function is very general.
        '''

        assert not isInIOThread()

        result_query = update(model)

        for field, value in selector.iteritems():
            result_query = result_query.where(
                getattr(model, field) == value)

        result_query = result_query.where(
            reduce(or_, [getattr(model, field) != value
                         for field, value in updated.iteritems()]))

        result_query = result_query.values(**updated)

        session = Session()

        try:
            result = session.execute(result_query)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

        return result.rowcount

    @inlineCallbacks
    def update_if_changed(self, model, selector, updated):
        result = 0

        item = dict(selector)
        item.update(updated)

        old_item = yield self.get_changed(model, selector, updated)

        if old_item is not None:
            result = yield deferToThreadPool(
                self.reactor, self.thread_pool,
                self._do_update_if_changed, model, selector, updated)

            if result:
                self.reporter.updated(
                    model, dicthash(selector), item, old_item)
        else:
            self.reporter.unchanged(model, dicthash(selector))

        returnValue(result)

    def _do_update(self, model, selector, updated):
        assert not isInIOThread()

        session = Session()

        try:
            result = session.query(model).filter_by(**selector).update(updated)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

        return result

    def update(self, model, selector, updated):
        ''' Update model matching some *selector* dict and
        replacing it's values from *updated* dict.
        Universal solution, but slow. Really slow.
        For each custom situation custom query should be built
        using *case* function.
        '''

        return deferToThreadPool(
            self.reactor, self.thread_pool,
            self._do_update, model, selector, updated)

    def _do_exists(self, model, selector):
        session = Session()

        try:
            result = bool(
                session.query(model.id).filter_by(**selector).scalar())
            return result
        finally:
            session.close()

    def exists(self, model, selector):
        ''' Check whether object matching selector exists '''
        return deferToThreadPool(
            self.reactor, self.thread_pool,
            self._do_exists, model, selector)

    def _do_is_changed(self, model, selector, updated):
        session = Session()

        result_query = session.query(model.id).filter(**selector)

        result_query = result_query.filter(
            reduce(or_, [getattr(model, field) != value
                         for field, value in updated.iteritems()]))

        try:
            result = bool(result_query.scalar())
        finally:
            session.close()

        return result

    def is_changed(self, model, selector, updated):
        ''' Check whether model fields are changed '''
        return deferToThreadPool(
            self.reactor, self.thread_pool,
            self._do_is_changed, model, selector, updated)

    def _do_get_changed(self, model, selector, updated):
        session = Session()

        query = session.query(model).filter_by(**selector)

        query = query.filter(
            reduce(or_, [getattr(model, field) != value
                         for field, value in updated.iteritems()]))

        try:
            item = query.first()

            if item is not None:
                item = row2dict(item)

            return item
        finally:
            session.close()

    def get_changed(self, model, selector, updated):
        ''' Return model if it's changed and None if it's unchanged '''
        return deferToThreadPool(
            self.reactor, self.thread_pool,
            self._do_get_changed, model, selector, updated)

    def _do_get_id(self, model, unique, fval, fields):
        assert not isInIOThread()

        session = Session()

        try:
            result = session.query(model.id).filter(
                getattr(model, unique) == fval).one().id
            return result
        finally:
            session.close()

    @inlineCallbacks
    def get_id(self, model, unique, fields,
               update_existing=False):
        ''' Get an ID from the cache or from the database.
        If doesn't exist - create an item.
        All database operations are done from
        the separate thread
        - update_existing: Update object if it exists within the database.
        '''
        assert isInIOThread()

        fval = fields[unique]

        try:
            result = self.cache[model][fval]
            self.counters['cache.hit'][model] += 1
            returnValue(result)
        except KeyError:
            self.counters['cache.miss'][model] += 1

        selectors = {unique: fval}

        result, created = yield deferToThreadPool(
            self.reactor, self.thread_pool,
            get_or_create,
            model, fields, **selectors)

        if created:
            self.reporter.saved(model, result)
        else:
            self.counters['db.cache.hit'][model] += 1
            if update_existing:
                yield self.update_if_changed(
                    model, {unique: fval}, fields)

        result = result.id

        self.cache[model][fval] = result
        returnValue(result)


# metadata = MetaData(dbdefer.engine)

# def_time = datetime(year=1900, month=1, day=1).time()
# def_DBL = None
# def_int = None

# pp = pprint.PrettyPrinter(indent=4)
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

def getplace(place):
    # r_dh = r'.*[0-9].*DH$'
    if "DH" in place:
        return int(re.sub(r'[^\d.]', '', place))
        # return int(placenum.replace("DH", ''))
    else:
        return 
        {
    "WV": 99,
    "WV-A": 99,
    "WX": 99,
    "WX-A": 99,
    "UV": 99,
    "DISQ": 99,
    "FE": 99,
    "DNF":99,
    "PU": 99,
    "TNP":99,
    "UR": 99,
    }.get(str(place), int(place))


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
# class MyImagesPipeline(ImagesPipeline):
   
#     def file_path(self, request, response=None, info=None):
#         #item=request.meta['item'] # Like this you can use all from item, not just url.
#         #http://www.hkjc.com/english/racing/finishphoto.asp?racedate=20141220R1_L.jpg
#         image_id = request.url.split('/')[-1]
#         # image_id = request.meta.get('Inracename')
#         #get name
#         return 'full/%s' % (image_id)
#     # def set_filename(self, response):
#     #     # pp.pprint(response.meta)
#     #     theurl = response.meta["RacecourseCode"][0] + response.meta["RaceDate"][0] + response.meta["RaceNumber"][0]
#     #     #add a regex here to check the title is valid for a filename.
#     #     return 'full/{0}.jpg'.format(theurl)   

#     # def get_images(self, response, request, info):
#     #     for key, image, buf in super(MyImagesPipeLine, self).get_images(response, request, info):
#     #         key = self.set_filename(response)
#     #     yield key, image, buf

#     def get_media_requests(self, item, info):
#         try:
#             for image in item['image_urls']:
#                 yield scrapy.Request(image)
#         except:
#             None        

#     def item_completed(self, results, item, info):
#         image_urls = [x['url'] for ok,x in results if ok]
#         if not image_urls:
#             raise DropItem("no images in this item: sucks")
#         item['image_urls'] = image_urls
#         return item 

class SQLAlchemyPipeline(object):

    def __init__(self):

        self.scheduler = DBScheduler()

    @inlineCallbacks
    def process_item(self, item, spider): 
        #only 1 instance
        if isinstance(item, ResultsItem):

            hkdividendid = self.scheduler.get_id(
                HKDividend, 'PublicRaceIndex',
                {
                    "PublicRaceIndex": item["RacecourseCode"] + item["RaceDate"] + str(item["RaceNumber"]),
                                        "RaceDate": item["RaceDate"], 
                                        "RaceNumber": item["RaceNumber"],
                                        "RacecourseCode": item.get("RacecourseCode", None),
                                        "PublicRaceIndex": item["RacecourseCode"] +
                   item["RaceDate"] + str(item["RaceNumber"]),
                                        "WinDiv": item.get("WinDiv", None), 
                                       "Place1Div":item.get("Place1Div"), 
                                       "Place2Div": item.get("Place2Div", None), 
                                       "Place3Div":item.get("Place3Div", None),
                                        "QNDiv": item.get("QNDiv", None), 
                                        "QP12Div": item.get("QP12Div"), 
                                        "QP13Div": item.get("QP13Div", None), 
                                        "QP23Div": item.get("QP23Div", None),  
                                        "TierceDiv": item.get("TierceDiv"), 
                                        "TrioDiv": item.get("TrioDiv", None), 
                                        "FirstfourDiv": item.get("FirstfourDiv", None), 
                                        "QuartetDiv": item.get("QuartetDiv", None),
                                        "ThisDouble11Div": item.get("ThisDouble11Div", None), 
                                        "ThisDouble12Div": item.get("ThisDouble12Div",None),
                                        "Treble111Div": item.get("Treble111Div", None), 
                                        "Treble112Div": item.get("Treble112Div",None),
                                        "ThisDoubleTrioDiv": item.get("ThisDoubleTrioDiv", None), 
                                        "TripleTrio111Div": item.get("TripleTrio111Div", None),
                                         "TripleTrio112Div": item.get("TripleTrio112Div", None), 
                                         "SixUpDiv": item.get("SixUpDiv", None), 
                                         "SixUpBonusDiv": item.get("SixUpBonusDiv", None)
                },update_existing=True)


            raceclassid = self.scheduler.get_id(
                Raceclass, "Name", 
                {
                    "Name": item.get("Raceclass", None) 
                },update_existing=True)

            railtypeid = self.scheduler.get_id(
                Railtype, "Name",
                {
                    "Name": item.get("Railtype", None)
                },update_existing=True)
                                                                                   
            goingid = self.scheduler.get_id(
                Going, "Name",
                {
                    "Name": item.get("Going", None)

                },update_existing=True)                                                                      
            distanceid = self.scheduler.get_id(
                Distance, "MetricName",

                {
                "MetricName": int(item.get("Distance", 0)),
                "Miles": float(float(item.get("Distance", 0))/1600.0),
                "Furlongs": int(int(item.get("Distance", 0))/200)
                },update_existing=True)                                                                                  
                                                                 
            # gearid = self.scheduler.get_id(
            #     Gear, "name",
            #     {
            #         "name": item["Gear"]
            #     })

            trainerid = self.scheduler.get_id(
                Trainer, "Name",
                {

                    "Name": item["Trainer"],
                    "Homecountry": "HKG"
                },update_existing=True)    

            jockeyid = self.scheduler.get_id(
                Jockey, "Name",
                {

                    "Name": item["Jockey"],
                    "Homecountry": "HKG"
                },update_existing=True)


            horseid=self.scheduler.get_id( 
                Horse, "Code",
                {
                "Code": item["HorseCode"], 
                "Name": item["Horse"],
                "Homecountry": "HKG"

                },update_existing=True)

            hkdividendid = yield hkdividendid
            raceclassid = yield raceclassid
            railtypeid = yield railtypeid
            goingid = yield goingid
            distanceid = yield distanceid

            raceid = self.scheduler.get_id(
                HKRace, "PublicRaceIndex",
                {
                "Url": item.get("Url", None),
                "RacecourseCode": item["RacecourseCode"],
                "RaceDate": item["RaceDate"],
                "Name": item["Name"],
               # "Inraceimage": item["images"],
                # "Inraceimage": item["images"][0]['data'],
               "Inraceimage": item["images"][0]['data'] if item["images"] else None,
                "RaceNumber": int(item["RaceNumber"]),
                "PublicRaceIndex": item["RacecourseCode"] +
                   item["RaceDate"] + str(item["RaceNumber"]),
                "IncidentReport": item.get("IncidentReport", None),
                "RaceIndex": item.get("RaceIndex", None),
                "Prizemoney": item.get("Prizemoney", None),
                "Raceratingspan": item.get("Raceratingspan", None),
                "Surface": item.get("Surface", None),
                "Dayofweek": item.get("Dayofweek", None),
                "NoSectionals": getnosectionals(item.get("Distance", 0)), 
                "hk_going_id": goingid,
                "hk_raceclass_id": raceclassid,
                "hk_railtype_id": railtypeid,
                "hk_distance_id": distanceid,
                "hk_dividend_id": hkdividendid
                },update_existing=True)


            # ownerid = yield ownerid
  
            jockeyid = yield jockeyid
            horseid = yield horseid
            raceid = yield raceid
            trainerid  = yield trainerid


            runner = HKRunner(
                HorseNumber=item.get("HorseNumber", def_int),
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
                PlaceNum = getplace(item.get("Place", None)),
                Place = item.get("Place", None),
                Horseprize = gethorseprize(item.get("PlaceNum", None), item.get("Prizemoney", None)),
                PublicRaceIndex = item["RacecourseCode"] + item["RaceDate"] + str(item["RaceNumber"]) + item["Horse"],
                hk_race_id=raceid,
                jockey_id= jockeyid,
                trainer_id=trainerid,
                horse_id=horseid)


                exists = yield self.scheduler.exists(
                    HKRunner, 
                    {
                    'PublicRaceIndex':item["RacecourseCode"] + item["RaceDate"] + str(item["RaceNumber"]) + item["Horse"]

                    }
                    )

                if exists:
                    res = yield seld.scheduler.update_if_changed(
                        HKRunner, 
                    {
                    'PublicRaceIndex':item["RacecourseCode"] + item["RaceDate"] + str(item["RaceNumber"]) + item["Horse"]

                    })
                    
                    if res:
                        self.scheduler.counters['updated'][HKRunner] += 1
                    else:
                        self.scheduler.counters['unchanged'][HKRunner] += 1
                else:
                    self.scheduler.save(runner)
                    self.scheduler.counters['create'][HKRunner] += 1

        returnValue(item)

'''
usage instructions:
'''

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
