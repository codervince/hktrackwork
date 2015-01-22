# -*- coding: utf-8 -*-
__author__ = 'Vince'

from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey, UniqueConstraint, CheckConstraint, Time, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.url import URL

import settings


ModelBase = declarative_base()

#create ALL models here for DB



class EventType(ModelBase):
    __tablename__ = "hk_trackwork_type"
    id = Column(Integer, primary_key=True)
    Name = Column(String(100), unique=True)
    UniqueConstraint('Name', name='EventTypeName_uidx')


class Owner(ModelBase):
    __tablename__ = "owner"
    __tableargs__ = ( CheckConstraint('Homecountry in ("HKG", "SIN", "AUS", "NZL", "RSA". "ENG", "IRE", "DUB", "IRE", "SCO", "MAC")'))
    id = Column(Integer, primary_key=True)
    Name = Column(String(255), unique=True)
    Homecountry = Column('Homecountry', String(3), nullable=False)
    UniqueConstraint('Name', name='Ownername_uidx')

class Gear(ModelBase):
    __tablename__ = "hk_gear"
    id = Column(Integer, primary_key=True)
    Name = Column(String(255), unique=True)
    UniqueConstraint('Name', name='Gear_uidx')

class Horse(ModelBase):
    __tablename__ = "horse"
    __tableargs__ = ( CheckConstraint('Homecountry in ("HKG", "SIN", "AUS", "NZL", "RSA". "ENG", "IRE", "DUB", "IRE", "SCO", "MAC")'))
    id = Column(Integer, primary_key=True)
    Code = Column(String(6), nullable=False, unique=True)
    Name = Column(String(255), nullable=False)
    Homecountry = Column('Homecountry', String(3), nullable=False)
    ImportType = Column(String(10), default="")
    SireName = Column(String(255), default="")
    DamName = Column(String(255), default="")
    DamSireName = Column(String(255), default="")
    UniqueConstraint('Code', 'Homecountry', name='Horsecodehomecountry_uidx')

class HKTrackwork(ModelBase):
    __tablename__ = "hk_trackwork"
    id = Column(Integer, primary_key=True)
    EventDate = Column(Date, nullable=False)
    EventVenue = Column(String(100))
    EventDescription = Column(String(255))
    EventTypeid = Column(Integer, ForeignKey('hk_trackwork_type.id'))
    Ownerid = Column(Integer, ForeignKey("owner.id"))
    Gearid = Column(Integer, ForeignKey("hk_gear.id"))
    Horseid = Column(Integer, ForeignKey('horse.id'))
    UniqueConstraint('EventDate', 'EventDescription', 'Horseid', name='EventDateDescrHorseId_uidx')


class Jockey(ModelBase):
    __tablename__ = "jockey"
    __tableargs__ = ( CheckConstraint('Homecountry in ("HKG", "SIN", "AUS", "NZL", "RSA". "ENG", "IRE", "DUB", "IRE", "SCO", "MAC")'))
    id = Column(Integer, primary_key=True)
    Name = Column(String(100), unique=True)
    Homecountry = Column('Homecountry', String(3), nullable=False)
    UniqueConstraint('Name', name='JockeyName_uidx')

class Trainer(ModelBase):
    __tablename__ = "trainer"
    __tableargs__ = ( CheckConstraint('Homecountry in ("HKG", "SIN", "AUS", "NZL", "RSA". "ENG", "IRE", "DUB", "IRE", "SCO", "MAC")'))
    id = Column(Integer, primary_key=True)
    Name = Column(String(255), unique=True)
    Homecountry = Column('Homecountry', String(3), nullable=False)
    UniqueConstraint('Name', name='Trainername_uidx')

class HKRace(ModelBase):
    __tablename__ = "hk_race"
    __tableargs__ = ( CheckConstraint('Racecoursecode in ("HV", "ST")'))
    id = Column(Integer, primary_key=True)
    Url = Column('url', String)
    Racecoursecode = Column('Racecoursecode', String, nullable=False)
    RaceDate = Column('RaceDate', String, nullable=False)
    RaceNumber = Column('RaceNumber', String, nullable=False)
    RaceIndex = Column('RaceIndex', String, nullable=False)


class HKRunner(ModelBase):
    __tablename__ = "hk_runner"
    id = Column(Integer, primary_key=True)
    Raceid = Column(Integer, ForeignKey("hk_race.id"))
    Horseid = Column(Integer, ForeignKey("horse.id"))
    HorseNo= Column('HorseNo', String, nullable=False)
    Jockeyid =Column(Integer, ForeignKey("jockey.id"))
    Trainerid =Column(Integer, ForeignKey("trainer.id"))
    #horse id code + name + name + Homecountry='HKG'
    # Horse= Column('Horse', String, nullable=False)
    # HorseCode= Column('HorseCode', String, nullable=False)
    #jockey name + Homecountry='HKG'
    Jockey= Column('Jockey', String, nullable=False)
    #trainer name + name + Homecountry='HKG'
    Trainer= Column('Trainer', String, nullable=False)

    ActualWt= Column('ActualWt', Integer, nullable=False)
    DeclarHorseWt= Column('DeclarHorseWt', Integer, nullable=False)
    Draw= Column('Draw', Integer, nullable=False)
    LBW= Column('LBW', Float, nullable=False)
    RunningPosition= Column('RunningPosition', String, nullable=False)
    Sec1DBL = Column('Sec1DBL', Float, nullable=True)
    Sec2DBL = Column('Sec2DBL', Float, nullable=True)
    Sec3DBL = Column('Sec3DBL', Float, nullable=True)
    Sec4DBL = Column('Sec4DBL', Float, nullable=True)
    Sec5DBL = Column('Sec5DBL', Float, nullable=True)
    Sec6DBL = Column('Sec6DBL', Float, nullable=True)
    FinishTime= Column('FinishTime', Time, nullable=False)  #e.g. 1.49.08 --> '00:01:49.08' hhmmss.nn always < 5mins
    Sec1Time = Column('Sec1Time', Time, nullable=True)
    Sec2Time = Column('Sec2Time', Time, nullable=True)
    Sec3Time = Column('Sec3Time', Time, nullable=True)
    Sec4Time = Column('Sec4Time', Time, nullable=True)
    Sec5Time = Column('Sec5Time', Time, nullable=True)
    Sec6Time = Column('Sec6Time', Time, nullable=True)
    WinOdds= Column('WinOdds', Float, nullable=False)


def get_engine():
    return create_engine(URL(**settings.DATABASE))


def create_schema(engine):
    ModelBase.metadata.create_all(engine)

