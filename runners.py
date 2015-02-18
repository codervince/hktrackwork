#runners
#stats module
import psycopg2
import psycopg2.extras
import json
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
import horse


def getpreviousruns(horsecode, racedate, selectstring=None, where=None):
	''' returns race and runner horse odds stats info in DESC order for a particular horsecode '''
	horseid = horse._gethorseid(horsecode)
	conn,c1  = connect.connect()
 	# basic = _getbasiccolnames()
	if selectstring is not None:
		if where is None: 
			sql = c1.mogrify("SELECT " + selectstring + " from hk_race ra JOIN hk_runner ru ON (ra.id = ru.raceid) JOIN horse h on (h.id = ru.horseid) WHERE ra.racedate <%s AND ru.horseid=%s ORDER BY ra.racedate DESC;", (racedate,horseid,)  )
		else:
			sql = c1.mogrify("SELECT " + selectstring + " from hk_race ra JOIN hk_runner ru ON (ra.id = ru.raceid) JOIN horse h on (h.id = ru.horseid) WHERE ra.racedate <%s AND " + where + " AND ru.horseid=%s ORDER BY ra.racedate DESC;", (racedate,horseid,)  )
			print sql
	else:
		'''check that time data and stats are present for a horse'''
		assert _hastimedata(horsecode) < 1, "no timedata avaiable: %s" % horsecode
		basic = "*"
		sql = c1.mogrify("SELECT " + basic + " from hk_race ra JOIN hk_runner ru ON (ra.id = ru.raceid) JOIN horse h on (h.id = ru.horseid) WHERE ru.horseid=%s ORDER BY ra.racedate DESC;", (horseid,)  )
		# print sql
	c1.execute(sql)
	# colnames = [desc[0] for desc in c1.description]
	# runs.append(colnames)
	# print colnames
	runs = c1.fetchall()
	c1.close()
	conn.close()
	# pprint.pprint(runs)
	return runs
	# print json.dumps(results, indent=2)