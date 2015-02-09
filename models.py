# -*- coding: utf-8 -*-
#/Users/vmac/RACING1/HKG/scrapers/dist/hkjc
from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey, UniqueConstraint, CheckConstraint, Time, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import BYTEA, TIMESTAMP
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import relationship, backref
from sqlalchemy.pool import SingletonThreadPool
#for Oracle, Firebird
from sqlalchemy import *
import settings


#for multithreading
# from twisted.web import xmlrpc, server
# from twisted.internet import reactor
Base = declarative_base()
engine = create_engine(URL(**settings.DATABASE))
metadata = MetaData(bind=engine)

ModelBase = declarative_base()



class EventType(ModelBase):
    __tablename__ = "hk_trackwork_type"
    id = Column(Integer, primary_key=True)
    Name = Column("name", String(100), unique=True)
    UniqueConstraint('name', name='EventTypeName_uidx')


class Owner(ModelBase):
    __tablename__ = "owner"
    __tableargs__ = ( CheckConstraint('Homecountry in ("HKG", "SIN", "AUS", "NZL", "RSA". "ENG", "IRE", "DUB", "IRE", "SCO", "MAC")'))
    id = Column(Integer, primary_key=True)
    Name = Column("name", String(255), unique=True)
    Homecountry = Column('homecountry', String(3), nullable=False)
    UniqueConstraint('name', name='OwnerName_uidx')

class Gear(ModelBase):
    __tablename__ = "hk_gear"
    id = Column(Integer, primary_key=True)
    Name = Column("name", String(255), unique=True)
    UniqueConstraint('name', name='GearName_uidx')

class Going(ModelBase):
    __tablename__ = "hk_going"
    id = Column(Integer, primary_key=True)
    Name = Column("name", String(255), unique=True)
    UniqueConstraint('name', name='GoingName_uidx')

class Raceclass(ModelBase):
    __tablename__ = "hk_raceclass"
    id = Column(Integer, primary_key=True)
    Name = Column("name", String(255), unique=True)
    UniqueConstraint('name', name='RaceClassName_uidx')

class Distance(ModelBase):
    __tablename__= "hk_distance"
    id = Column(Integer, primary_key=True)
    MetricName = Column("metricname", Integer)
    Miles = Column("miles", Float)
    Furlongs = Column("furlongs", Integer) 
    UniqueConstraint('metricname', name='HKDistance_MetricName_uidx')

class Railtype(ModelBase):
    __tablename__= "hk_railtype"
    id = Column(Integer, primary_key=True)
    Name = Column("name", String(256))
    UniqueConstraint('name', name='HKRailType_Name_uidx')

class Horse(ModelBase):
    __tablename__ = "horse"
    __tableargs__ = ( CheckConstraint('Homecountry in ("HKG", "SIN", "AUS", "NZL", "RSA". "ENG", "IRE", "DUB", "IRE", "SCO", "MAC")'))
    id = Column(Integer, primary_key=True)
    Code = Column("code", String(6), nullable=False, unique=True)
    Name = Column("name", String(255), nullable=False)
    Sex = Column("sex", String(2), nullable=True)
    Homecountry = Column('homecountry', String(3), nullable=False)
    ImportType = Column("importtype", String(10), default="")
    SireName = Column("sirename", String(255), default="")
    DamName = Column("damname", String(255), default="")
    DamSireName = Column("damsirename", String(255), default="")
    UniqueConstraint('name', 'code', 'homecountry', name='Horsecodehomecountry_uidx')

class HKTrackwork(ModelBase):
    __tablename__ = "hk_trackwork"
    id = Column(Integer, primary_key=True)
    EventDate = Column("eventdate", Date, nullable=False)
    EventVenue = Column("eventvenue", String(100))
    EventDescription = Column("eventdescription", String(255))
    EventTypeid = Column("eventtypeid", Integer, ForeignKey('hk_trackwork_type.id'))
    # Ownerid = Column("ownerid", Integer, ForeignKey("owner.id"))
    Gearid = Column("gearid", Integer, ForeignKey("hk_gear.id"))
    Horseid = Column("horseid", Integer, ForeignKey('horse.id'))
    UniqueConstraint('eventdate', 'eventtypeid', 'gearid', 'horseid', name='HKTrackwork_EventDateTypeIdGearIdHorseId_uidx')

class HKVet(ModelBase):
    __tablename__ = "hk_vet"
    id = Column(Integer, primary_key=True)
    Horseid = Column("horseid", Integer, ForeignKey('horse.id'))
    EventDate = Column("eventdate", Date, nullable=False)
    Details = Column("details", String(255))
    PassedDate = Column("passeddate", Date, nullable=False)
    UniqueConstraint('eventdate', 'details', 'horseid', name='HKVet_EventDateDetailsHorseId_uidx')

# class HKTrackwork(ModelBase):
#     __tablename__ = "hk_trackwork"
#     id = Column(Integer, primary_key=True)
#     eventdate = Column("eventdate", Date, nullable=False)
#     eventvenue = Column("eventvenue", String(100))
#     eventdescription = Column("eventdescription", String(255))
#     eventtypeid = Column(
#         "eventtypeid", Integer, ForeignKey('hk_trackwork_type.id'))
#     ownerid = Column("ownerid", Integer, ForeignKey("owner.id"))
#     gearid = Column("gearid", Integer, ForeignKey("hk_gear.id"))
#     horseid = Column("horseid", Integer, ForeignKey('horse.id'))
#     UniqueConstraint('eventdate', 'eventdescription',
#                      'horseid', name='HKTrackwork_EventDateDescrHorseId_uidx')


class Jockey(ModelBase):
    __tablename__ = "jockey"
    __tableargs__ = ( CheckConstraint('Homecountry in ("HKG", "SIN", "AUS", "NZL", "RSA". "ENG", "IRE", "DUB", "IRE", "SCO", "MAC")'))
    id = Column(Integer, primary_key=True)
    Name = Column("name", String(100), unique=True)
    Code = Column("code", String(10))
    Homecountry = Column('homecountry', String(3), nullable=False)
    UniqueConstraint('name', name='JockeyName_uidx')

class Trainer(ModelBase):
    __tablename__ = "trainer"
    __tableargs__ = ( CheckConstraint('Homecountry in ("HKG", "SIN", "AUS", "NZL", "RSA". "ENG", "IRE", "DUB", "IRE", "SCO", "MAC")'))
    id = Column(Integer, primary_key=True)
    Name = Column("name", String(255), unique=True)
    Code = Column("code", String(10))
    Homecountry = Column('homecountry', String(3), nullable=False)
    UniqueConstraint('name', name='Trainername_uidx')

class HKRace(ModelBase):
    __tablename__ = "hk_race"
    __tableargs__ = ( 
        CheckConstraint('RacecourseCode in ("HV", "ST")'), UniqueConstraint('PublicRaceIndex'), {'autoload': True})
    id = Column(Integer, primary_key=True)
    Url = Column('url', String)
    RacecourseCode = Column('racecoursecode', String, nullable=False)
    Name = Column('name', String(255), nullable=True)
    RaceDate = Column('racedate', Date, nullable=True)
    RaceDateTime = Column('racedatetime', String, nullable=True)
    RaceNumber = Column('racenumber', Integer, nullable=False)
    PublicRaceIndex = Column('publicraceindex', String, nullable=False)
    RaceIndex = Column('raceindex', String, nullable=True)
    IncidentReport = Column('incidentreport', String, nullable=True)
    Goingid = Column("goingid", Integer, ForeignKey("hk_going.id"))
    Raceclassid = Column("raceclassid", Integer, ForeignKey("hk_raceclass.id"))
    Distanceid = Column("distanceid", Integer, ForeignKey("hk_distance.id"))
    Railtypeid = Column("railtypeid", Integer, ForeignKey("hk_railtype.id"))
    HKDividendid = Column("hkdividendid", Integer, ForeignKey("hk_dividend.id"))
    Raceratingspan = Column("raceratingspan", String)
    Prizemoney = Column("prizemoney", Integer)
    Surface = Column('surface', String)
    Dayofweek = Column('dayofweek', String)
    Isnight = Column("isnight", Boolean)       #from raceday
    NoSectionals = Column('nosectionals', Integer)
    Inraceimage = Column('inraceimage', BYTEA, nullable=True)
    UniqueConstraint('publicraceindex', name='HKRace_PublicRaceIndex_uidx')



    def __repr__(self):
        return "HKRace(Racecoursecode='%s', Name= '%s', RaceDate='%s', RaceNumber='%d', RaceIndex='%s',Prizemoney='%s')" % \
        (self.RacecourseCode, self.Name, self.RaceDate, self.RaceNumber, self.RaceIndex, self.RaceIndex, self.Prizemoney)  

class HKDividend(ModelBase):
    __tablename__ = "hk_dividend"
    id = Column(Integer, primary_key=True)
    RacecourseCode = Column('racecoursecode', String, nullable=False)
    RaceDate = Column('racedate', String, nullable=False)
    RaceNumber = Column('racenumber', String, nullable=False)
    PublicRaceIndex = Column('publicraceindex', String, nullable=False)
    WinDiv= Column("windiv", Float, nullable=False)
    Place1Div = Column("place1div",Float, nullable=True)
    Place2Div = Column("place2div", Float, nullable=True)
    Place3Div = Column("place3div", Float, nullable=True)
    QNDiv = Column("qndiv", Float, nullable=True)
    QP12Div = Column("qp12div", Float, nullable=True)
    QP13Div = Column("qp13div", Float, nullable=True)
    QP23Div = Column("qp23div", Float, nullable=True)
    TierceDiv = Column("tiercediv", Float, nullable=True)
    TrioDiv = Column("triodiv", Float, nullable=True)
    FirstfourDiv = Column("firstfourdiv", Float, nullable=True)
    #optionals FirstFourDiv
    QuartetDiv = Column("quartetdiv", Float)
    ThisDouble11Div = Column("thisdouble11div", Float)
    ThisDouble12Div = Column("thisdouble12div", Float)
    Treble111Div = Column("treble111div", Float)
    Treble112Div = Column("treble112div",Float)
    ThisDoubleTrioDiv = Column("thisdoubletriodiv", Float)
    TripleTrio111Div = Column("tripletrio111div", Float)
    TripleTrio112Div = Column("tripletrio112div", Float)
    SixUpDiv = Column("sixupdiv", Float)
    SixUpBonusDiv = Column("sixupbonusdiv", Float)
    UniqueConstraint('racecoursecode', 'racedate','racenumber', name='HKDividendRCCodeDateRaceNumber_uidx') 

class HKRunner(ModelBase):
    __tablename__ = "hk_runner"
    id = Column(Integer, primary_key=True)
    PublicRaceIndex = Column('publicraceindex', String, nullable=False)
    Raceid = Column("raceid", Integer, ForeignKey("hk_race.id"))
    Horseid = Column("horseid", Integer, ForeignKey("horse.id"))
    PlaceNum = Column('placenum', String)
    Place = Column('place', Integer)
    isScratched = Column('isscratched', Boolean)
    Gearid = Column("gearid", Integer, ForeignKey("hk_gear.id"))
    Ownerid = Column("ownerid", Integer, ForeignKey("owner.id"))
    HorseNumber= Column('horsenumber', String, nullable=True)
    Jockeyid =Column("jockeyid", Integer, ForeignKey("jockey.id"))
    Trainerid =Column("trainerid", Integer, ForeignKey("trainer.id"))
    Jockey= Column('jockey', String, nullable=True)
    JockeyWtOver = Column('jockeywtover', Integer, nullable=True)
    Trainer= Column('trainer', String, nullable=True)
    ActualWt= Column('actualWt', Integer, nullable=True)
    DeclarHorseWt= Column('declarhorsewt', Integer, nullable=True)
    HorseWtDeclarChange = Column('horsewtdeclarchange', Integer, nullable=True)
    HorseWtpc = Column('horsewtpc', Float, nullable=True)
    Draw= Column('draw', Integer, nullable=True)
    LBW= Column('lbw', Float, nullable=True)
    Last6runs = Column('last6runs', String(30), nullable=True)
    Priority = Column('priority', String(10), nullable=True)
    RunningPosition= Column('runningposition', String, nullable=True)
    Rating =Column('rating', Integer, nullable=True)
    RatingChangeL1 = Column('ratingchangeL1', Integer, nullable=True)
    SeasonStakes = Column('seasonStakes', Integer, nullable=True)
    Age = Column('age', Integer, nullable=True)  #from raceday
    WFA = Column('wfa', Integer, nullable=True)
    isRanOn = Column('isranon', Boolean, nullable=True)
    Sec1DBL = Column('sec1dbl', Float, nullable=True)
    Sec2DBL = Column('sec2dbl', Float, nullable=True)
    Sec3DBL = Column('sec3dblL', Float, nullable=True)
    Sec4DBL = Column('sec4dbl', Float, nullable=True)
    Sec5DBL = Column('sec5dbl', Float, nullable=True)
    Sec6DBL = Column('sec6dbl', Float, nullable=True)
    FinishTime= Column('finishtime', Time, nullable=True)  #e.g. 1.49.08 --> '00:01:49.08' hhmmss.nn always < 5mins
    Sec1Time = Column('sec1time', Time, nullable=True)
    Sec2Time = Column('sec2time', Time, nullable=True)
    Sec3Time = Column('sec3time', Time, nullable=True)
    Sec4Time = Column('sec4time', Time, nullable=True)
    Sec5Time = Column('sec5time', Time, nullable=True)
    Sec6Time = Column('sec6time', Time, nullable=True)
    WinOdds= Column('winodds', Float, nullable=True)
    Horseprize = Column('horseprize',Float, nullable=True)
    HorseReport = Column('horsereport', String, nullable=True)
    HorseColors = Column('horsecolors', BYTEA, nullable=True)
    UniqueConstraint('publicraceindex', name='HKRunner_PublicRaceIndex_uidx')

#OTHER TABLES

# class RaceStats(ModelBase):
#     __tablename__ = "hk_racestats"
#     id = Column(Integer, primary_key=True)
#     Raceid = Column(Integer, ForeignKey("hk_race.id"))
#     FieldSize= Column('FieldSize', Integer)
#     NoLSWs = Column('NoLSWs', Integer)
#     NoFirstStarters = Column('NoFirstStarters', Integer)
#     MinStarts = Column(Integer)
#     MaxDistChange = Column(Integer)
    #pace?? winning style bias


# class HorseStats(ModelBase):
#     __tablename__ = "hk_horsestats"
#     id = Column(Integer, primary_key=True)
#     Raceid = Column(Integer, ForeignKey("hk_race.id"))
#     Horseid = Column(Integer, ForeignKey("horse.id"))
#     API_career = Column('API_career', Float)    
#     API_season = Column('API_season', Float)
#     CareerWins = Column(Integer)
#     CareerRuns = Column(Integer)
#     CareerScratches = Column(Integer)
#     CareerPlaces = Column(Integer)
#     CareerF4s = Column(Integer)
#     WinsPrep = Column(Integer)
#     RunsPrep = Column(Integer)
#     PlacesPrep = Column(Integer)
#     F4Prep = Column(Integer)
#     TotalDistancePrep = Column(Integer)
#     AVI_career_rk = Column(Integer)
#     AVI_season_rk = Column(Integer)
#     AvgCareerWins_rk = Column(Integer)
#     Winodds_rk = Column(Integer)
#     WeightBelowMax = Column(Integer)



# class FormStats(ModelBase):
#     __tablename__ = "hk_form"
#     id = Column(Integer, primary_key=True)
#     # Raceid = Column(Integer, ForeignKey("hk_race.id"))
#     Runnerid = Column(Integer, ForeignKey("hk_runner.id"))
#     DaystoL1 = Column(Integer)
#     DaystoL2 = Column(Integer)
#     nUp = Column(Integer)
#     WinsatNup = Column(Integer)
#     RunsatNup = Column(Integer)
#     WinsInClass = Column(Integer)
#     RunsInClass = Column(Integer)
#     AvgLBWClass = Column(Float)
#     AvgLBWDistance = Column(Float)
#     AvgLBWCD = Column(Float)
#     AvgLBWL3 = Column(Float)
#     L1Position = Column(String)
#     L2Position = Column(String)
#     L1Margin = Column(Float)
#     L2Margin = Column(Float)
#     isDroppingDown = Column(Boolean)
#     isHorseForCourse = Column(Boolean)
#     isHorseandJockey = Column(Boolean)
#     WinsAtTrack = Column(Integer)
#     RunsAtTrack = Column(Integer)
#     WinsatDistance = Column(Integer)
#     RunsAtDistance = Column(Integer)
#     WinsatCD = Column(Integer)
#     RunsatCD = Column(Integer)
#     WinsOnSurface = Column(Integer)
#     RunsOnSurface = Column(Integer)
#     PlacesOnSurface = Column(Integer)
    ##rankings AVI MAX THIS RACE


#PROGENY
#SWITCHES gear stats incl gelded trackworkthisjockey jockeyswitches
#odds stats
#time stats
#market stats


class HKOdds(ModelBase):
    __tablename__ = "hk_odds"
    id = Column(Integer, primary_key=True)
    Horsenumber = Column("horsenumber", Integer, nullable=False)
    Updatedate = Column("updatedate", Date, nullable=False)
    Updatetime = Column("updaettime",Time, nullable=False)
    Winodds = Column("winodds", Float)
    Placeodds = Column("placeodds", Float)
    Raceid = Column("raceid", Integer, ForeignKey("hk_race.id"))
    # Horseid = Column(Integer, ForeignKey("horse.id"))
    UniqueConstraint('raceid', 'horsenumber', 'updatedate', 'updatetime', name='HKOdds_RaceidHorseNoUpdateDateTime_uidx')

    # 1:M race:HKodds
    race = relationship("HKRace", backref=backref("odds", order_by=(Updatedate, Updatetime)))

# poolclass=SingletonThreadPool, 
def get_engine():
    return create_engine(URL(**settings.DATABASE), pool_size=0)
    # return DBDefer(URL(**settings.DATABASE))

def create_schema(engine):
    ModelBase.metadata.create_all(engine)

