#stats module
import numpy as np
import scipy
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
import runners

from datetime import datetime, date, time
##EACH CALL WILL UPDATE INSERT TO TABLE

'''
scoipy zscore etc
http://docs.scipy.org/doc/scipy/reference/stats.html
uses 
 list or a numpy array.
'''

####################

'''usage: avg_time([datetime.now(), datetime.now() - timedelta(hours=12)]) '''
#distances!
class Vividict(dict):
    def __missing__(self, key):
        value = self[key] = type(self)()
        return value

def getsecdistfromdistance(distance, sec):
	assert connect._sanitycheck(distance)
	d = Vividict()
	d["1000"] = [200,400,400, None, None, None]
	d["1100"] = [300,400,400, None, None, None]
	d["1200"] = [400,400,400, None, None, None],
	d["1400"] = [200,400,400,400, None, None],
	d["1500"] = [300,400,400,400, None, None],
	d["1600"] = [400,400,400,400, None, None],
	d["1650"] = [450,400,400,400, None, None],
	d["1700"] = [300,400,400,400, None, None],
	d["1750"] = [350,400,400,400, None, None],
	d["1800"] = [200,400,400,400,400, None],
	d["1900"] = [300,400,400,400,400, None],
	d["2000"] = [400,400,400,400,400, None],
	d["2200"] = [200,400,400,400,400,400],
	d["2400"] = [400,400,400,400,400,400]
	return d.getitem(str(distance)[sec-1], None)

# use distance and datetime and sectional speed also consider % weight - get std h weight more wt on back slower less penalty
# get max % weight carried
def avg_time(datetimes):
	nsecs = sum(int(dt.strftime("%f")) for dt in datetimes) 
	# secs = sum(dt.minute * 60 + dt.second + dt.microsecond*0.000001 for dt in datetimes)
	l = len(datetimes)
	if l > 0:
		avg = int(nsecs / l)
		print avg
		seconds,microseconds = divmod(avg,100000)
		minutes,seconds = divmod(seconds, 60)
		# minutes = seconds/60
		# seconds, microseconds = divmod(int(avg),1000000)
		# minutes, seconds = divmod(seconds, 60)
	else:
		# pass
		minutes, seconds, microseconds = 0,0,0
	return datetime.combine(date(1900, 1, 1), time(minutes, seconds, microseconds))

# usage print dumps(datetime.now(), default=json_serial)

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, time):
        serial = obj.strftime("%M:%S.%f")
        return serial





	}.getitem(str(distance), None)

class Stats:

	def __init__(self, statstype):
		self.statstype = statstype

#prize money horse is missing
	#TODO: have getpreviousruns be returned in better format

	def getPrizeMoneyStats(self, horsecode, racedate):
		'''checks if stats in db already else calculate and update/insert'''
		pprint.pprint(horsecode)
		stats = {}
		runs = []
		# assert _sanitycheck(horsecode) is not None
		horseid = horse._gethorseid(horsecode)
		#get horseage
		#get avg per race over career/season/track/
		conn, c1= connect.connect()
		sel = connect.makeselect("ru.horseprize")
		#make where
		wh = connect.makewhere("ra.racedate>'20140901'")
		#season
		runs = runners.getpreviousruns(horsecode, racedate, sel, wh)
		# pprint.pprint(runs[1])
		if runs[1] is not None and runs[1] != '':
			print runs[1] #list of values

			# print("Avg pmoney season= %d", np.mean(runs[1]))
			#numpy.std
			#numpy.median, numpy.var numpy.corrcoef, amin, amax 
		#career

		#get rank cohort

		#update to DB
# finsish time / distanceid s = d/t 
# 
		
	def getTimeStats(self, horsecode, racedate):
		'''exclude null times '''
		assert connect._sanitycheck([horsecode,racedate])
		horseid = horse._gethorseid(horsecode)
		sel = connect.makeselect("ra.racedate, ra.nosectionals, ra.goingid, ra.raceclassid, ra.distanceid, ru.sec1time, ru.sec2time, ru.sec3time, ru.sec4time, ru.sec5time, ru.sec6time, ru.finishtime")
		##career
		runs = runners.getpreviousruns(horsecode, racedate, sel)
		# print json.dumps(runs,default=json_serial)
		sec1s = [ r[5] for r in runs]
		print avg_time(sec1s)

		# pprint.pprint(runs) #list of lists each list is a race 
		# if runs[1] is not None:
			# for r in runs[1]:
				# pprint.pprint(type(r[1])) 
				# print avg_time(runs[1:])

		##season


		##last3 runs


