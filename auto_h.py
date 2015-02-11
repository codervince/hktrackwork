#auto call horses
import psycopg2
import psycopg2.extras
#ensures unicode output
import psycopg2.extensions
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)

import settings
import pprint
from datetime import datetime

from sqlalchemy.engine.url import URL

#returns a connection
def connect():
	conn_string = "host='localhost' dbname='hkraces' user='vmac' password=''"
	conn = psycopg2.connect(conn_string)
	c1= conn.cursor()
	return conn,c1

def connectnocursor():
	conn_string = "host='localhost' dbname='hkraces' user='vmac' password=''"
	conn = psycopg2.connect(conn_string)
	return conn

def teardown():
	conn.close()

def uploadracecardstodb():
	pass
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

#very quick
def copyallracestofile():
	f = open('race.dat', 'a+') 
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

def gethorses(racedate,racenumber=None):
	'''takes a date and returns a list of horse codes for all races that date'''
	raceids = []
	horsecodes = []
	raceids = getraceids(racedate, racenumber)
	pprint.pprint(raceids)
	# raceids2 = [i[0] for i in raceids]
	#for each of these raceids, create a connection and a cursor and 
	conn,c1 = connect()
	sql = c1.mogrify("SELECT h.code from hk_runner ru JOIN horse h on (h.id = ru.horseid) WHERE ru.raceid IN %s;", (tuple(raceids),)  )
	print sql
	c1.execute(sql)
	#returns list of tuples with horsecodes
	horsecodes = [i[0] for i in c1.fetchall()]
	return horsecodes


def main():

	# Open a cursor to perform database operations on the connection (=session)
	#RETURNS COLUMN NAMES NOT INDEX
	# copyallracestofile()
	#GET VARS OF INTEREST
	horsecodes =[]
	racenumber = 10
	racedate = datetime.strptime('20141115', "%Y%m%d").date()
	# racenumber = 1
	#DO WHAT WITH THEM
	horsecodes = gethorses(racedate)
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