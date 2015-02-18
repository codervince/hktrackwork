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
import connect

def _sanitycheck(val):
	if type(val) == 'list':
		return val[0] is not None
	else:
		return val is not None
#refactor get attribute

def _gethorsevalue(horsecode, attr):
	assert _sanitycheck(args)
	
	#does attribute exist?
	conn,c1 = connect()
	try:
		sql = c1.mogrify("SELECT %s from horse h WHERE h.code=%s;", (attr, horsecode) )
		c1.execute(sql)
		val = c1.fetchone()
		c1.close()
		conn.close()
		return val
	except:
		pass

def _gethorsename(horsecode):
	'''returns a single horse name for this horsecode'''
	if horsecode is None:
		return None
	conn,c1 = connect()
	# print horsecode
	sql = c1.mogrify("SELECT h.name from horse h WHERE h.code=%s;", (horsecode,) )
	print sql
	c1.execute(sql)
	horsename = c1.fetchone()[0]
	# print horsename[0]
	c1.close()
	conn.close()
	return horsename

def _gethorse(horsecode):
	'''returns the row of data about this horsecode'''
	if horsecode is None:
		return None
	conn,c1 = connect()
	# print horsecode
	sql = c1.mogrify("SELECT * from horse h WHERE h.code=%s;", (horsecode,) )
	print sql
	c1.execute(sql)
	h = c1.fetchone()
	c1.close()
	conn.close()
	pprint.pprint(h)
	return h

#what about horses which changed names- same code!
def _gethorseid(horsecode):
	'''returns a single horseid for this horsecode'''
	if horsecode is None:
		return None
	conn,c1 = connect.connect()
	print horsecode
	sql = c1.mogrify("SELECT h.id from horse h WHERE h.code=%s;", (horsecode,) )
	print sql
	c1.execute(sql)
	horseid = c1.fetchone()[0]
	c1.close()
	conn.close()
	return horseid