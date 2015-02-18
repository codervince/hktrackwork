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

from stats import *


###HELPERS
def _getdateo(racedate):
	if racedate is None:
		return datetime.today().date()
	else:
		return datetime.strptime(racedate, '%Y%m%d').date()
##################


########CONNECTION
def connect():
	conn_string = "host='localhost' dbname='hkraces100' user='vmac' password=''"
	conn = psycopg2.connect(conn_string)
	c1= conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
	# print conn.dsn
	return conn,c1

def connectnocursor():
	conn_string = "host='localhost' dbname='hkraces100' user='vmac' password=''"
	conn = psycopg2.connect(conn_string)
	return conn

def teardown(conn):
	conn.close()

####################


	# mypic = open('picture.png', 'rb').read()
	# curs.execute("insert into blobs (file) values (%s)",
    # (psycopg2.Binary(mypic),))

#all columns and secondary table columns relevant for a race
#each task uses a separate connection
def printallformeeting(racedate, racenumber):
	'''prints all ra + ru records for a date'''
	#use unique name to ensure server cursor created

	 # c2 = conn.cursor('cursor_allformeeting', cursor_factory=psycopg2.extras.DictCursor)
	#GET raceid for racedate and racenumber


	#TRANSACTION 1 same conn different cursors
	conn,c1 = connect()
	#use mogrify to get cursor statment. e.g.
	# sqls = c1.mogrify("select id from hk_race ra where ra.racenumber=%s;", (racenumber,))
	c1.execute("SELECT id FROM hk_race ra WHERE ra.racedate=%s and ra.racenumber=%s;", (racedate, racenumber))
	raceid = c1.fetchone()
	c1.close()
	
	c2 = conn.cursor()
	c2.execute(
"""
SELECT ra.name as rname,g.name as gname, h.name as hname
FROM hk_race ra JOIN hk_going g ON (ra.goingid = g.id)
JOIN hk_raceclass rc ON (ra.raceclassid = rc.id) JOIN hk_distance  d ON (ra.distanceid = d.id)
JOIN hk_railtype rt ON (ra.railtypeid = rt.id)
JOIN hk_runner ru ON (ru.raceid = ra.id)
JOIN horse h ON (ru.horseid = h.id)
WHERE ra.id=%s
""", raceid)
	pprint.pprint(c2.fetchall())
	pprint.pprint(conn.notices)
	conn.commit()	#even for selects

# 	print cursor.fetchall();
# 	runner_count = 0
# 	#only prints 12! 
# 	print "Printing todays runners:\n"
# 	for runner in cursor:
# 		runner_count +=1
# 		print "runner: %s    %s\n" % (runner_count, runner)
	# cursor.close()
	c2.close()
	conn.close()

#name of file 
def copyallracestofile(racedate):
	f = open(racedate + '.dat', 'a+') 
	conn,c1 = connect()
	#usage: copy_to(file, table, sep='\t', null='\\N', columns=None)
	c1.copy_to(f, 'hk_race',',', 'NONE')
	c1.close()
	conn.close()


def getraceids(racedate, racenumber=None,cursor= None):
	'''returns a cursor (result) obj from racedate and optional racenumber'''
	if cursor is not None:
		conn,c1 = connect()
	else:
		conn = connectnocursor()
		c1 = conn.cursor()
	if racenumber is not None:
		c1.execute("SELECT id FROM hk_race ra WHERE ra.racedate=%s and ra.racenumber=%s;", (racedate, racenumber))
		raceids = c1.fetchone()
	else:
		c1.execute("SELECT id FROM hk_race ra WHERE ra.racedate=%s;", (racedate,)) 
		raceids = c1.fetchall()
	c1.close()
	conn.close()
	return raceids

#see also make up own selects
def _getbasiccolnames():
	return "ra.racenumber, ru.horsenumber, h.code, h.name "

def _getextendedcolnames():
	return "ra.racenumber,ru.horsenumber "

##MINIMIZE QUEIRIES GET BASIC DATA AND EXTENDED DATA IN ONE QUERY 
#ONE QUERY FOR RACE INFO
#ONE FOR RUNNER
##get basic data including odds data max min avg starting
## AVGPrizemoney AVGSeasonStakes 
#Used to dump to HTML with salient information for a racedate
def getrunnerinfo(racedate,racenumber=None,extended=False):
	'''takes a date and returns a list of horse codes for all races that date'''
	raceids = []
	horsecodes = []
	raceids = getraceids(_getdateo(racedate), racenumber)
	pprint.pprint(raceids)
	basic = _getbasiccolnames()
	ext = _getextendedcolnames()
	# raceids2 = [i[0] for i in raceids]
	if not extended: 
		conn,c1 = connect()
		sql = c1.mogrify("SELECT " + basic + "from hk_race ra JOIN hk_runner ru ON (ra.id = ru.raceid) JOIN horse h on (h.id = ru.horseid) WHERE ru.raceid IN %s ORDER BY ra.racenumber ASC;", (tuple(raceids),)  )
		print sql
		c1.execute(sql)
		colnames = [desc[0] for desc in c1.description]
		horsecodes.append(colnames)
		horsecodes.append(c1.fetchall())
		c1.close()
		conn.close()
	else:
		pass
		# assert _hastimedata == True
	return horsecodes
	#returns list of tuples with horsecodes
	# horsecodes = [i[0] for i in c1.fetchall()]
	# return horsecodes

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
	conn,c1 = connect()
	print horsecode
	sql = c1.mogrify("SELECT h.id from horse h WHERE h.code=%s;", (horsecode,) )
	print sql
	c1.execute(sql)
	horseid = c1.fetchone()[0]
	c1.close()
	conn.close()
	return horseid

# def _dofetchall(sql):
# 	res = []
# 	conn,c1  = connect()
# 	c1.execute(sql)
# 	colnames = [desc[0] for desc in c1.description]
# 	res.append(colnames)
# 	runs.append(c1.fetchall())
# 	c1.close()
# 	conn.close()
# 	return res
def _tableexists(tablename):
	conn,c1  = connect()
	c1.execute("select exists(select * from information_schema.tables where table_name=%s)", (tablename,))
	return c1.fetchone()[0]


def scrapepage(url):
	from bs4 import BeautifulSoup
	BASE_URL = "http://www.racenet.com.au/horse/"
	from urllib2 import urlopen
	if url is None:
		return None
	html = urlopen(url).read()
	soup = BeautifulSoup(html, "lxml")
	return soup.find(id="saleDbLbl")

#http://www.racenet.com.au/horse/Fabulous-November
#develop this into scrapy
#WHAT IF MORE tHAN ONE NEED SIRE AND DAM!
def getsaleprice(horsecode):
	
	from bs4 import BeautifulSoup
	BASE_URL = "http://www.racenet.com.au/horse/"
	if horsecode is None:
		return None
	# horsename = _gethorsename(horsecode)
	h = _gethorse(horsecode)
	horseid = h["id"]
	horsename = h['name']
	sirename = h["sirename"]
	damname = h["damname"]
	# print horsename
	if horsename is not None:
		horsename = horsename.replace(" ", "-") # or %20 - 
		section_url = BASE_URL + horsename
		print section_url
		sp= scrapepage(section_url)
		if sp is not None:
			saleprice = sp.get_text()  #can be 
			if "not offered at yearling sale" in saleprice:
				saleprice = 0.00
			elif "$" in saleprice:
				#WAIT FOR RESULTS AND NEW COLUMN
				saleprice = float(sub(r'[^\d.]', '', saleprice))
				# saleprice = float(saleprice.replace("$", "").replace(",", ""))
			#add to horse table we have horseid
				# conn, c1 = connect()
				# sql = c1.mogrify("UPDATE horse SET salepriceyearling=%s where ts.horseid=%s;", (saleprice,horseid))
				# c1.execute(sql)
				# assert c1.fetchone()[0] == horseid, "Mistake when updating table"
			else:
				pass
		else:
			#TEST WHEN WE HAVE RACEDAY WITH SIRE DAM INFO
			#get (God's Own x Cannilateral) sirename x damname
			# parents = str(sirename) + " x " + str(damname)
			#look for parents in soup
			# sp = soup.find(p)
			#  /horse/
			links = soup.find_all('a', href=re.compile('^/horse/')  )	
			pprint.pprint(links)
			# for l in links:
			# 	print l.get('href')
				# sp = scrapepage(section_url)
				#rconstrit link  http://www.racenet.com.au/horse')

			#choose ! based on sire dam
			#NEED SIRE SAMW INFO
			#try horsenanme_countryorigin
		# saleprice = hdata.findall("span", "saleDbLbl")
		# print saleprice
	#go to racenet


def _hastimedata(horsecode):
	if horsecode is None:
		return None
	horseid = _gethorseid(horsecode)
	conn,c1  = connect()
	assert _tableexists('hk_timestats') == True, "hk_timestats table does not exist"
	sql = c1.mogrify("SELECT count(*) FROM hk_timestats ts where ts.horseid=%s;", (horsecode,))
	c1.execute(sql)
	return c1.fetchone()

#basic and extended
#get all then filter locally.
def getpreviousruns(horsecode, racedate, extended=False):
	''' returns race and runner horse odds stats info in DESC order for a particular horsecode '''
	horseid = _gethorseid(horsecode)
	conn,c1  = connect()
	runs = [] #or JSON
 	# basic = _getbasiccolnames()
 	basic = "* "
	if not extended:
		sql = c1.mogrify("SELECT " + basic + "from hk_race ra JOIN hk_runner ru ON (ra.id = ru.raceid) JOIN horse h on (h.id = ru.horseid) WHERE ra.racedate <%s AND ru.horseid=%s ORDER BY ra.racedate DESC;", (racedate,horseid,)  )
		print sql

	else:
		'''check that time data and stats are present for a horse'''
		assert _hastimedata(horsecode) < 1, "no timedata avaiable: %s" % horsecode
		ext = _getextendedcolnames()
		sql = c1.mogrify("SELECT " + basic + "from hk_race ra JOIN hk_runner ru ON (ra.id = ru.raceid) JOIN horse h on (h.id = ru.horseid) WHERE ru.horseid=%s ORDER BY ra.racedate DESC;", (horseid,)  )
		print sql
	c1.execute(sql)
	colnames = [desc[0] for desc in c1.description]
	runs.append(colnames)
	runs.append(c1.fetchall())
	c1.close()
	conn.close()
	pprint.pprint(runs)
	return runs

def head2head(horsecode1, horsecode2):
	pass

def main():

	# Open a cursor to perform database operations on the connection (=session)
	#RETURNS COLUMN NAMES NOT INDEX
	# copyallracestofile()
	#GET VARS OF INTEREST
	horsecodes =[]
	racenumber = 10
	# racedate = datetime.strptime('20141115', "%Y%m%d").date()
	# racenumber = 1
	#DO WHAT WITH THEM
	racedate = '20150201'
	#het race info
	
	horsecodes= getrunnerinfo(racedate)
	#[0] is columns [1] is data [1][0] horse
	# pprint.pprint(horsecodes)


	###BEFORE PRINTING MAKE SURE STATS ARE DONE!
	for c in horsecodes[1]:
		# getsaleprice(c[2])
		# print c
		# getpreviousruns(c[2], racedate)
		stats = Stats('time')
		stats.getTimeStats(c[2], '20150201')
	#run spider for todays horses to updaet tracktype and vet
	
	# printallformeeting(racedate,racenumber)
	# cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
	#ADDS MEMORY
	# work_mem = 2048
	# cursor.execute('SET work_mem TO %s', (work_mem,))
	# cursor.execute('SHOW work_mem')
	# memory = cursor.fetchone()
	# print "Value: ", memory[0]
	# execute a command return as PY objects?
	# sql_getrace = """

	# 	SELECT * FROM hk_race where RaceDate='%s';

	# 	"""
	# dt = datetime.strptime('20141022', "%Y%m%d").date()
	# dt2 = '20141022'

	# #MINIMIZE QUERY

	# cursor = conn.cursor('cursor_unique_name', cursor_factory=psycopg2.extras.DictCursor)
	# cursor.execute('SELECT * FROM my_table LIMIT 1000')
	# print cur.mogrify("SELECT * from hk_race where RaceDate=%s;", ( dt2, ))

	# racedate2 = (datetime.strptime('20150101', "%Y%m%d").date(),)
	# racedate = (datetime.strptime('20150115', '%Y%m%d'),)
	# cur.execute(sql_getrace, racedate2)
	#eecute many seq_of_parameters

#GETTING DATA BACK
# fetchone(), fetchmany(), fetchall()
	# print cur.fetchone()
	#get it all back
	#fetchone() if you know its just one
	# records = cursor.fetchall()
	# pprint.pprint(records)

	# try:
	# 	conn.commit()
	# 	cur.close()
	# 	conn.close()
	# except:
	# 	conn.rollback()

if __name__ == "__main__":
	main()