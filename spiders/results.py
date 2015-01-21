# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.loader import ItemLoader
from scrapy.contrib.loader.processor import TakeFirst, Compose
from hkjc.items import ResultsItem
from datetime import datetime

def timeprocessor(value):
    for format in ("%S.%f", "%M.%S.%f", "%S"):
        try:
            return datetime.strptime(value, format).time()
        except:
            pass
    return None


class ResultsItemsLoader(ItemLoader):
    default_item_class = ResultsItem
    default_output_processor = Compose(TakeFirst(), unicode, unicode.strip)
    Winodds_out = Compose(default_output_processor, float)
    Finishtime_out = Compose(default_output_processor, timeprocessor)
    Sec1time_out = Compose(default_output_processor, timeprocessor)
    Sec2time_out = Compose(default_output_processor, timeprocessor)
    Sec3time_out = Compose(default_output_processor, timeprocessor)
    Sec4time_out = Compose(default_output_processor, timeprocessor)
    Sec5time_out = Compose(default_output_processor, timeprocessor)
    Sec6time_out = Compose(default_output_processor, timeprocessor)
    WinOdds_out = Compose(default_output_processor, timeprocessor)
 
    

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
        """
        if not len(response.css("table.draggable").xpath(".//tr[@class='trBgGrey' or @class='trBgWhite']")):
            yield Request(response.url, dont_filter=True)
        else:
        """
        # for link in LinkExtractor(restrict_xpaths="//div[contains(@class,'raceNum')]").extract_links(response)[:-1]:
        #     yield Request(link.url)
        table_data = list()
        for tr in response.css("table.draggable").xpath(".//tr[@class='trBgGrey' or @class='trBgWhite']"):
            l = ResultsItemsLoader(selector=tr)
            l.add_value("Url", response.url)
            dd = response.url.split("/")
            l.add_value("Racedate", dd[-3])
            l.add_value("Racecoursecode", dd[-2])
            l.add_value("Racenumber", dd[-1])
            l.add_xpath("Place", "./td[1]/text()")
            l.add_xpath("HorseNo", "./td[2]/text()")
            l.add_xpath("Horse", "./td[3]/a/text()")
            l.add_xpath("Horsecode", "./td[3]/text()", re="\((.+?)\)")
            l.add_xpath("Jockey", "./td[4]/a/text()")
            l.add_xpath("Trainer", "./td[5]/a/text()")
            l.add_xpath("ActualWt", "./td[6]/text()")
            l.add_xpath("DeclarHorseWt", "./td[7]/text()")
            l.add_xpath("Draw", "./td[8]/text()")
            l.add_xpath("LBW", "./td[9]/text()")
            l.add_xpath("Runningposition", "./td[10]/text()")
            l.add_xpath("Finishtime", "./td[11]/text()")
            l.add_xpath("Winodds", "./td[12]/text()")
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

