#auto call horses
import psycopg2
import psycopg2.extras
#ensures unicode output
import psycopg2.extensions
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)
import re
import settings
import pprint
from datetime import datetime
from re import sub
from sqlalchemy.engine.url import URL

def _sanitycheck(val):
	if type(val) == 'list':
		return val[0] is not None
	else:
		return val is not None

#to expand
def makewhere(s):
	return str(s)


def makeselect(*args):
	assert _sanitycheck(args)
	s = " ".join(args)
	return s

def _getbasiccolnames():
	return "ra.racenumber, ru.horsenumber, h.code, h.name "

def _getextendedcolnames():
	return "ra.racenumber,ru.horsenumber "


########CONNECTION
def connect():
	conn_string = "host='localhost' dbname='hkraces100' user='vmac' password=''"
	conn = psycopg2.connect(conn_string)
	# c1= conn.cursor()
	c1= conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
	# print conn.dsn
	return conn,c1

def connectnocursor():
	conn_string = "host='localhost' dbname='hkraces100' user='vmac' password=''"
	conn = psycopg2.connect(conn_string)
	return conn

def teardown(conn):
	conn.close()
