# -*- coding: utf-8 -*-
__author__ = 'Vince'

from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey, UniqueConstraint, CheckConstraint
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
    ImportType = Column(String(10))
    SireName = Column(String(255))
    DamName = Column(String(255))
    DamSireName = Column(String(255))
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

def get_engine():
    return create_engine(URL(**settings.DATABASE))


def create_schema(engine):
    ModelBase.metadata.create_all(engine)

