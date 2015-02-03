# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from scrapy.contrib.loader.processor import TakeFirst
import re
from hkjc.items import HorseItem
from datetime import datetime, date
from scrapy import log
'''
horses=N250,P121,S054,P369,S011
'''

RE_VAL  = re.compile(r"^:*\s*")

def tf(values, encoding="utf-8"):
    value = ""
    for v in values:
        if v is not None and v != "":
            value = v
            break
    return value.encode(encoding).strip()



#extend to include vet reports


class HorsesSpider(scrapy.Spider):
    name = "hktrackwork"
    allowed_domains = ["hkjc.com"]
    horse_url = "http://www.hkjc.com/english/racing/Track_Result.asp?txtHorse_BrandNo=%s"

    #or get from a file
    def __init__(self, **kwargs):
        h_str = kwargs.pop("horses", "")
        self.horses = [h for h in [h.strip() for h in h_str.split(",")] if h]

    def parse(self, response):
        horse_code = response.meta.get("code")
        if "No such record" in response.body:
            log.msg("No horse code %s found, skipping" % horse_code)
        try:
            # videos http://www.hkjc.com/english/racing/horse.asp?HorseNo=N250&Option=1#htop
            #horsecolors http://www.hkjc.com/images/RaceColor/N250.gif 30 * 38
            horse_name = tf(response.css(".subsubheader .title_eng_text").xpath("text()").extract()).split("\xc2\xa0")[0].strip()
            meta = dict(HorseCode=horse_code,
                        HorseName=horse_name,
                        Homecountry='HKG', 
                        ImportType=RE_VAL.sub("", tf(response.xpath("//font[contains(text(),'Import') and contains(text(),'Type')]/../following-sibling::td[1]/font/text()").extract())),
                        Owner=tf(response.xpath("//font[text()='Owner']/../following-sibling::td[1]/font/a/text()").extract()),
                        SireName=tf(response.xpath("//font[text()='Sire']/../following-sibling::td[1]/font/a/text()").extract()),
                        DamName=RE_VAL.sub("", tf(response.xpath("//font[text()='Dam']/../following-sibling::td[1]/font/text()").extract())),
                        DamSireName=RE_VAL.sub("", tf(response.xpath("//font[text()=\"Dam's Sire\"]/../following-sibling::td[1]/font/text()").extract())))

            for i, r in enumerate(response.css('.bigborder tr')):
                if i:
                    item = HorseItem(**meta)
                    for j, k in enumerate(('EventDate', 'EventType', 'EventVenue', 'EventDescription', 'Gear')):
                        item[k] = tf(r.xpath("./td[%s]/font/text()" % (j+1)).extract()).replace("\xc2\xa0", " ").strip()
                    item["EventDate"] = datetime.strptime(item["EventDate"], "%d/%m/%Y").date()
                    yield item
        except Exception, e:
            log.msg("Skipping horse code %s because of error: %s" % (horse_code, str(e)))

    def start_requests(self):
        for horse in self.horses:
            yield Request(self.horse_url % horse, meta=dict(code=horse))



