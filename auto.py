import os
import csv
import pprint
import time
from twisted.python.logfile import DailyLogFile
from twisted.python import log as twistedlog
from twisted.internet import task
from twisted.internet import reactor, threads
from scrapy import log as thescrapylog

pp = pprint.PrettyPrinter(indent=4)



#rotates to new file 1 per day
#LOGGING
twistedlog.startLogging(DailyLogFile.fromFullPath("/Users/vmac/RACING1/HKG/scrapers/dist/hkjc/logs/twistedlog.log"))
thescrapylog.start()

def runSpider(date, coursecode):
	os.system("scrapy crawl results -a date=" + date +" -a coursecode=" + coursecode + "")


#read from file dump tinto dict
races = {}
with open('HKraces1415.csv', mode='r') as infile:
    reader = csv.reader(infile)
    races = {rows[0]:rows[1] for rows in reader}

# pp.pprint(races.keys())
# for k in races:
#     l = task.LoopingCall(runSpider(k, races[k]))
#     l.start(1.0) #call every second
#     reactor.run
# l.stop()
for k in races:
	os.system("scrapy crawl results -a date=" + k +" -a coursecode=" + races[k] + "")
	time.sleep(5)

#read from dictionary fill command line and run scrapy
# 20140608,ST
# thedate = '20150201'
# thecoursecode = 'ST'

# "scrapy crawl results -a date=20150120 -a coursecode='ST'"
# os.system("scrapy crawl results -a date=" + thedate +" -a coursecode=" + thecoursecode + "")
