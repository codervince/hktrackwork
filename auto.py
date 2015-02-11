import os
import csv
import pprint
import time
from twisted.python.logfile import DailyLogFile
from twisted.python import log as twistedlog
from twisted.internet import task
from twisted.internet import reactor, threads
from scrapy import log as thescrapylog
#use API to run spider
from twisted.internet import reactor
from scrapy.crawler import Crawler
from scrapy import log
from scrapy.utils.project import get_project_settings
from spiders import *

pp = pprint.PrettyPrinter(indent=4)

# def setup_crawler(date, coursecode):
#     pp.pprint("%s -> %s", (date, coursecode)) 
#     spider = ResultsSpider(date=date, coursecode=coursecode)
#     settings = get_project_settings()
#     crawler = Crawler(settings)
#     crawler.configure()
#     crawler.crawl(spider)
#     crawler.start()


#rotates to new file 1 per day
#LOGGING

# def runSpider(date, coursecode):
# 	os.system("scrapy crawl results -a date=" + date +" -a coursecode=" + coursecode + "")


#read from file dump tinto dict
# races = {}
# with open('HKraces1415.csv', mode='r') as infile:
#     reader = csv.reader(infile)
#     races = {rows[0]:rows[1] for rows in reader}

# pp.pprint(races.keys())
# for k in races:
#     l = task.LoopingCall(runSpider(k, races[k]))
#     l.start(1.0) #call every second
#     reactor.run
# l.stop()
# pp.pprint(races.keys())
# for k in races:
# 	pp.pprint(k, races[k])
# 	setup_crawler(k, races[k])
# reactor.run
#curl http://localhost:6800/schedule.json -d project=hkjc -d spider=results -d setting=DOWNLOAD_DELAY=2 -d date=20150101 -d coursecode='ST'
# os.system("curl http://localhost:6800/schedule.json -d project=hkjc -d spider=results -d setting=DOWNLOAD_DELAY=2 -d date=" + ,coursecode=\"ST\"")


mynewraces = {}
with open('HKraces1415.csv', mode='r') as infile:
    reader = csv.reader(infile)
    for row in reader:
    	k,v = row
    	mynewraces = {rows[0]:rows[1] for rows in reader}

# pp.pprint(mynewraces)
#log completed 
for r in mynewraces:
	# print r
	# pp.pprint("%s --> %s" % (r, races[r]))
	# setup_crawler(r, races[r])
	# spider = ResultsSpider(date=r, coursecode=races[r])
	# settings = get_project_settings()
	# crawler = Crawler(settings)
	# crawler.signals.connect(reactor.stop, signal=signals.spider_closed)
	# crawler.configure()
	# crawler.crawl(spider)
	# crawler.start()
	# log.start()
	#use scrapyd 
	#vmac$ curl http://localhost:6800/schedule.json -d project=hkjc -d spider=results -d date=20150101 -d coursecode=ST
	#currently: 20141220-d/None/1
	os.system("curl http://localhost:6800/schedule.json -d project=hkjc -d spider=results -d setting=DOWNLOAD_DELAY=2 -d date=" + r + " -d coursecode=" + mynewraces[r])

	# os.system("scrapy crawl results -a date=" + r +" -a coursecode=" + mynewraces[r] + "")
	# reactor.run()

# for k in races:
# 	os.system("scrapy crawl results -a date=" + k +" -a coursecode=" + races[k] + "")
# 	time.sleep(5)

#read from dictionary fill command line and run scrapy
# 20140608,ST
# thedate = '20150201'
# thecoursecode = 'ST'

# "scrapy crawl results -a date=20150120 -a coursecode='ST'"
# os.system("scrapy crawl results -a date=" + thedate +" -a coursecode=" + thecoursecode + "")
