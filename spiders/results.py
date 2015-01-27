# -*- coding: utf-8 -*-
import scrapy
from scrapy import log
from scrapy.http import Request
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.loader import ItemLoader
from scrapy.contrib.loader.processor import TakeFirst, Compose, Join, MapCompose
# from scrapy.contrib.loader.processor import MapCompose
from hkjc.items import ResultsItem, RaceItem
from datetime import datetime
from time import sleep
from fractions import Fraction
import re
import pprint

def getHorseReport(ir, h):
    lir = ir.split('.')
    return [e.replace(".\\n", "...") for e in lir if h in e]


#done in default output processor?
def noentryprocessor(value):
    return None if value == '' else value



def timeprocessor(value):
    #tries for each possible format
    for format in ("%S.%f", "%M.%S.%f", "%S"):
        try:
            return datetime.strptime(value, format).time()
        except:
            pass
    return None
    

 #add Fractionprocessor here to convert fractions to ints for SecDBL and LBW  
def horselengthprocessor(value):
    #covers '' and '-'

    if '---' in value:
        return None
    elif value == '-':
        #winner
        return 0.0
    elif "-" in value and len(value) > 1:
        return float(Fraction(value.split('-')[0]) + Fraction(value.split('-')[1]))
    elif value == 'N':
        return 0.3
    elif value == 'SH':
        return 0.1
    elif value == 'HD':
        return 0.2
    elif value == 'SN':
        return 0.25  
    #nose?           
    elif value == 'NOSE':
        return 0.05
    elif '/' in value:
         return float(Fraction(value))        
    elif value.isdigit():
        return try_float(value)
    else:
        return None   

def didnotrun(value):
    if "---" in value:
        return None


def try_float(value):
    try:
        return float(value)
    except:
        return 0.0

def try_int(value):
    try:
        return int(value)
    except:
        return 0    

def _cleanurl(value):
    print value
    return value

class RaceItemsLoader(ItemLoader):
    default_item_class = ResultsItem
    # default_output_processor = Compose(TakeFirst(), unicode, unicode.strip)        

class ResultsItemsLoader(ItemLoader):
    default_item_class = ResultsItem
    default_output_processor = Compose(TakeFirst(), unicode, unicode.strip)
    Winodds_out = Compose(default_output_processor, try_float)
    FinishTime_out = Compose(default_output_processor, timeprocessor)
    Sec1time_out = Compose(default_output_processor, timeprocessor)
    Sec2time_out = Compose(default_output_processor, timeprocessor)
    Sec3time_out = Compose(default_output_processor, timeprocessor)
    Sec4time_out = Compose(default_output_processor, timeprocessor)
    Sec5time_out = Compose(default_output_processor, timeprocessor)
    Sec6time_out = Compose(default_output_processor, timeprocessor)
    LBW_out = Compose(default_output_processor, horselengthprocessor)
    Draw_out = Compose(default_output_processor, try_int)
    HorseNumber_out = Compose(default_output_processor, noentryprocessor)
    Sec1DBL_out = Compose(default_output_processor, horselengthprocessor)
    Sec2DBL_out = Compose(default_output_processor, horselengthprocessor)
    Sec3DBL_out = Compose(default_output_processor, horselengthprocessor)
    Sec4DBL_out = Compose(default_output_processor, horselengthprocessor)
    Sec5DBL_out = Compose(default_output_processor, horselengthprocessor)
    Sec6DBL_out = Compose(default_output_processor, horselengthprocessor)
    image_urls_out = MapCompose(_cleanurl) 
    RunningPosition_out = Join(' ')
   
   

class ResultsSpider(scrapy.Spider):
    name = "results"
    allowed_domains = ["hkjc.com"]
    start_url = "http://racing.hkjc.com/racing/Info/meeting/Results/english/Local/%s/%s/1"

    def __init__(self, date=None, coursecode=None):
        if date is None or coursecode is None:
            raise ValueError("Invalid spider parameters")
        self.racedate = date
        self.racecode = coursecode


    def parse(self, response):
        if not len(response.css("table.draggable").xpath(".//tr[@class='trBgGrey' or @class='trBgWhite']")):
            log.msg("Results page not ready, waiting 2 secs...", logLevel=log.INFO)
            sleep(2)
            yield Request(response.url, dont_filter=True)
        else:
            for link in LinkExtractor(restrict_xpaths="//div[contains(@class,'raceNum')]").extract_links(response)[:-1]:
                yield Request(link.url)
            table_data = list()
            #Race ItemsLoader
            
            # l.add_value("Raceindex", re.search(r"\(([0-9]+)\)", response.xpath('/html/body/div[2]/div[2]/div[2]/div[5]/div[1]/text()').extract()[0]).group(1))
            # l.add_value("Prizemoney", re.sub("\D", "", response.xpath('//td[@class="number14"]/text()').extract()[0]))
            # l.add_xpath("Windiv",'//td[@class= "number14 tdAlignR"]/text()') 
            # j = rl.load_item()
            # table_data.append(j)


            #for images and odds data does not make sense to use a separate itemloader??
            ####Inraceimage + video files
            for s1 in response.selector.css('img').xpath('@src'):

                rl = RaceItemsLoader(selector=s1)
                base_url = "http://racing.hkjc.com/racing/content/Images/RaceResult" 
                # image_url = response.selector.css('img').xpath('@src').re(r'RaceResult(.*)')
                image_urls = s1.re(r'RaceResult(.*)')
                # log.msg("image link:  %s " % imagelink[0])
                image_urls = [base_url + x for x in image_urls]

                if image_urls:
                    rl.add_value("image_urls", image_urls)
                    j = rl.load_item()
                    table_data.append(j)

            for tr in response.css("table.draggable").xpath(".//tr[@class='trBgGrey' or @class='trBgWhite']"):
                l = ResultsItemsLoader(selector=tr)
                l.add_value("Url", response.url)
                dd = response.url.split("/")
                l.add_value("RaceDate", dd[-3])
                l.add_value("RacecourseCode", dd[-2])
                l.add_value("RaceNumber", dd[-1])
                #racedata table: response.xpath('//table[contains(@class, \"tableBorder0 font13\")]').extract()
                l.add_value("RaceIndex", re.search(r"\(([0-9]+)\)", response.xpath('/html/body/div[2]/div[2]/div[2]/div[5]/div[1]/text()').extract()[0]).group(1))
                l.add_value("Prizemoney", re.sub("\D", "", response.xpath('//td[@class="number14"]/text()').extract()[0]))
                l.add_value("Going", response.xpath('//table[contains(@class, \"tableBorder0 font13\")]/tr[1]/td[3]/text()').extract()[0])
                if "ALL WEATHER TRACK" in response.xpath('//table[contains(@class, \"tableBorder0 font13\")]/tr[2]/td[3]/text()').extract()[0]:
                    l.add_value("Railtype", "AWT")
                    l.add_value("Surface", None)
                else:    
                    l.add_value("Railtype", response.xpath('//table[contains(@class, \"tableBorder0 font13\")]/tr[2]/td[3]/text()').extract()[0].split('-')[1].strip())
                l.add_value("Surface", response.xpath('//table[contains(@class, \"tableBorder0 font13\")]/tr[2]/td[3]/text()').extract()[0].split('-')[0].strip())
                l.add_value("Raceclass", response.xpath('//table[contains(@class, \"tableBorder0 font13\")]/tr[1]/td[1]/text()').extract()[0].split('-')[0].strip())
                l.add_value("Distance", re.sub("\D", "", response.xpath('//table[contains(@class, \"tableBorder0 font13\")]/tr[1]/td[1]/span/text()').extract()[0].split('-')[0].strip()))
                if "Class" in response.xpath('//table[contains(@class, \"tableBorder0 font13\")]/tr[1]/td[1]/text()').extract()[0].split('-')[0].strip():
                    rs = response.xpath('//table[contains(@class, \"tableBorder0 font13\")]/tr[1]/td[1]/span/text()').extract()[0].split('- ')[1].strip()
                    l.add_value("Raceratingspan", re.sub(r'([^\s\w-]|_)+', '',rs).strip().split(u" ")[0].replace("Rating", ""))
                else:
                    l.add_value("Raceratingspan", None)                
                #get incident report
                # l.add_value("Incidentreport", response.xpath("//td[contains(text(), \"Racing Incident Report\")]/following::tr/td/text()").extract()[0].strip())
                ir = response.xpath("//td[contains(text(), \"Racing Incident Report\")]/following::tr/td/text()").extract()[0].strip()
                h = tr.xpath("./td[3]/a/text()").extract()[0]
                l.add_value("HorseReport", '..'.join(getHorseReport(ir, h)))
                l.add_value("IncidentReport", ir)
                #table starts here
                l.add_xpath("Place", "./td[1]/text()")
                l.add_xpath("HorseNumber", "./td[2]/text()")
                l.add_xpath("Horse", "./td[3]/a/text()")
                l.add_xpath("HorseCode", "./td[3]/text()", re="\((.+?)\)")
                l.add_xpath("Jockey", "./td[4]/a/text()")
                l.add_xpath("Trainer", "./td[5]/a/text()")
                l.add_xpath("ActualWt", "./td[6]/text()")
                l.add_xpath("DeclarHorseWt", "./td[7]/text()")
                l.add_xpath("Draw", "./td[8]/text()")
                l.add_xpath("LBW", "./td[9]/text()")
                #incorrect RP
                l.add_xpath("RunningPosition", "./td[10]//td/text()")
                l.add_xpath("FinishTime", "./td[11]/text()")
                l.add_xpath("Winodds", "./td[12]/text()")
                #get odds data
                oddspath = response.xpath('//td[@class= "number14 tdAlignR"]/text()')
                headers = response.xpath('//td[@class= "number14 tdAlignR"]/preceding-sibling::td/text()').extract()
                l.add_value("WinDiv", oddspath[0].extract().replace(',', ''))
                l.add_value("Place1Div", oddspath[1].extract().replace(',', ''))
                l.add_value("Place2Div", oddspath[2].extract().replace(',', ''))
                l.add_value("Place3Div", oddspath[3].extract().replace(',', ''))
                l.add_value("QNDiv", oddspath[4].extract().replace(',', ''))
                l.add_value("QP12Div", oddspath[5].extract().replace(',', ''))
                l.add_value("QP13Div", oddspath[6].extract().replace(',', ''))
                l.add_value("QP23Div", oddspath[7].extract().replace(',', ''))
                l.add_value("TierceDiv", oddspath[8].extract().replace(',', ''))
                l.add_value("TrioDiv", oddspath[9].extract().replace(',', ''))
                l.add_value("FirstfourDiv", oddspath[10].extract().replace(',', ''))
                #optionals
                '''
                R1 from JAN 2015 QUARTET owise NONE
                R2 1ST DOUBLE
                R3 2ND DOUBLE
                R4 QUARTET  [11] 3RD DOUBLE [12][13] 1ST DOUBLE TRIO
                R5 QUARTET  [11] 4TH DOUBLE [12][13]
                R6 QUARTET 5TH DOUBLE | TRIPLE TRIO | TRIPLE TRIO(Consolation)
                R7 QUARTET 6TH DOUBLE 2ND DOUBLE TRIO
                R8 QUARTET 7TH DOUBLE
                R9 QUARTET 8TH DOUBLE
                R10 QUARTET 9TH DOUBLE 12 13 TREBLE 14 15 3RD DOUBLE TRIO 16 SIX UP JOCKEY CHALLENGE

                '''
                r_finddble = r'.*DOUBLE.*'
                r_findtrble = r'.*TREBLE.*'
                r_finddbletrio = r'.*DOUBLE TRIO.*'
                r_findtripletrio = r'.*TRIPLE TRIO.*'

                if "QUARTET" in headers: #1
                    l.add_value("QuartetDiv", oddspath[11].extract().replace(',', ''))
                if  len([m.group(0) for m in (re.search(r_finddble, l) for l in headers) if m]) ==1:#2
                    l.add_value("ThisDouble11Div", oddspath[12].extract().replace(',', ''))
                    l.add_value("ThisDouble12Div", oddspath[13].extract().replace(',', ''))
                if len([m.group(0) for m in (re.search(r_finddbletrio, l) for l in headers) if m]) ==1 and len([m.group(0) for m in (re.search(r_findtrble, l) for l in headers) if m]) !=1:
                    l.add_value("Treble111Div", oddspath[14].extract().replace(',', ''))
                    l.add_value("Treble112Div", oddspath[15].extract().replace(',', ''))
                if len([m.group(0) for m in (re.search(r_finddbletrio, l) for l in headers) if m]) ==1 and len([m.group(0) for m in (re.search(r_findtrble, l) for l in headers) if m]) ==1: #last race
                    l.add_value("Treble111Div", oddspath[14].extract().replace(',', ''))
                    l.add_value("Treble112Div", oddspath[15].extract().replace(',', ''))
                    l.add_value("ThisDoubleTrioDiv", oddspath[16].extract().replace(',', ''))
                    l.add_value("SixUpDiv", oddspath[17].extract().replace(',', '')) 
                if len([m.group(0) for m in (re.search(r_findtripletrio, l) for l in headers) if m]) ==1: #r4
                    l.add_value("TripleTrio111Div", oddspath[14].extract().replace(',', ''))
                    l.add_value("TripleTrio112Div", oddspath[15].extract().replace(',', ''))      
                    # Place1div = response.xpath('//td[@class= "number14 tdAlignR"]/text()')[1].extract(),
                    # Place2div = response.xpath('//td[@class= "number14 tdAlignR"]/text()')[2].extract(),
                    # Place3div = response.xpath('//td[@class= "number14 tdAlignR"]/text()')[3].extract(),
                    # QNdiv = response.xpath('//td[@class= "number14 tdAlignR"]/text()')[4].extract(),
                    # QP12div = response.xpath('//td[@class= "number14 tdAlignR"]/text()')[5].extract(),
                    # QP13div = response.xpath('//td[@class= "number14 tdAlignR"]/text()')[6].extract(),
                    # QP23div = response.xpath('//td[@class= "number14 tdAlignR"]/text()')[7].extract(),
                    # Tiercediv = response.xpath('//td[@class= "number14 tdAlignR"]/text()')[8].extract(),
                    # Triodiv = response.xpath('//td[@class= "number14 tdAlignR"]/text()')[9].extract(),
                    # Firstfourdiv = response.xpath('//td[@class= "number14 tdAlignR"]/text()')[10].extract()
                i = l.load_item()
                table_data.append(i)

            for link in LinkExtractor(restrict_xpaths="//img[contains(@src,'sectional_time')]/..").extract_links(response):
                yield Request(link.url, callback=self.parse_sectional, meta=dict(table_data=table_data))



    def parse_sectional(self, response):
        table_data = response.meta["table_data"]
        for item, tr in zip(table_data, response.xpath("//table[@cellspacing=1 and @width='100%']//td[@rowspan=2]/..")):
            ntr = tr.xpath("./following-sibling::tr[1]")
            l = ResultsItemsLoader(item=item, selector=tr)
            for i in range(4,10):
                j = i-3
                l.add_xpath("Sec%sDBL" % j, "./td[%s]/table/tr/td[2]/text()" % i)
                l.add_xpath("Sec%stime" % j, "./following-sibling::tr[1]/td[%s]/text()" % j)
            yield l.load_item()


    def start_requests(self):
        return [Request(self.start_url % (self.racedate, self.racecode))]

