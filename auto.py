import os
import csv
import pprint


pp = pprint.PrettyPrinter(indent=4)

#read from file dump tinto dict
races = {}

with open('HKraces.csv', mode='r') as infile:
    reader = csv.reader(infile)
    races = {rows[0]:rows[1] for rows in reader}

# pp.pprint(races)


# for k,v in races:
	# os.system("scrapy crawl results -a date=" + thedate +" -a coursecode=" + thecoursecode + "")

#read from dictionary fill command line and run scrapy

thedate = '20141220'
thecoursecode = 'ST'

# "scrapy crawl results -a date=20150120 -a coursecode='ST'"
os.system("scrapy crawl results -a date=" + thedate +" -a coursecode=" + thecoursecode + "")
