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
#remove ALchemy dependency?
from sqlalchemy.engine.url import URL

def setup():
	conn_string = "host='localhost' dbname='hkraces3' user='vmac' password=''"
	conn = psycopg2.connect(conn_string)
	return conn


def uploadracecardstodb():
	pass
	# mypic = open('picture.png', 'rb').read()
	# curs.execute("insert into blobs (file) values (%s)",
    # (psycopg2.Binary(mypic),))

#all columns and secondary table columns relevant for a race
def printallformeeting(conn, racedate, racenumber=(1,)):
	'''uses a cursor to print all ra + ru records for a date'''
	#use unique name to ensure server cursor created
	cursor = conn.cursor('cursor_allformeeting', cursor_factory=psycopg2.extras.DictCursor)
	#find better way to write these queries 
	qs = cursor.execute(
		"""
SELECT ra.name as rname,g.name as gname, h.name as hname
FROM hk_race ra JOIN hk_going g ON (ra.goingid = g.id)
JOIN hk_raceclass rc ON (ra.raceclassid = rc.id) JOIN hk_distance  d ON (ra.distanceid = d.id)
JOIN hk_railtype rt ON (ra.railtypeid = rt.id)
JOIN hk_runner ru ON (ru."Raceid" = ra.id)
JOIN horse h ON (ru."Horseid" = h.id)
WHERE ra."Racenumber"=%s
		""", racenumber)
	# print qs
	qs = cursor.mogrify(''' 

		SELECT
		ra.name as rname,
		g.name as gname, 
		h.name as hname

		FROM hk_race ra
		JOIN hk_going g ON (ra.goingid = g.id)
		JOIN hk_raceclass rc ON (ra.raceclassid = rc.id)
		JOIN hk_distance  d ON (ra.distanceid = d.id)
		JOIN hk_railtype rt ON (ra.railtypeid = rt.id)

		JOIN hk_runner ru ON (ru."Raceid" = ra.id)
		JOIN horse h ON (ru."Horseid" = h.id)
		WHERE ra.racedate = %s  
		AND ra."Racenumber"=%s
		''', (racedate, racenumber))
	# cursor.execute(qs);
	cursor.execute;
	#DO NOT USE UP CURSOR!!!
	print cursor.fetchall();
	runner_count = 0
	#only prints 12! 
	print "Printing todays runners:\n"
	for runner in cursor:
		runner_count +=1
		print "runner: %s    %s\n" % (runner_count, runner)
	conn.commit()
	# cursor.close()
	conn.close()

def main():

	# Open a cursor to perform database operations on the connection (=session)
	#RETURNS COLUMN NAMES NOT INDEX
	conn = setup()
	racedate = datetime.strptime('20141203', "%Y%m%d").date()
	# racenumber = 1
	printallformeeting(conn, ('2014-12-03',))
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