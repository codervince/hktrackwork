# hktrackwork

##WHATS DONE
* results data
* sectionals data
* dividend data
* in race image -> filesystem
* in race image UN SHA'd
* run from CSV list

##WHATS TO DO

* Add update function
..* add deltadate arg
..* do not yield if date < deltadate

*Videos (separate)
..* in race image -> DB 
* video playlist- > filesystem
* video playlist -> .ts -> DB
* get today's list of runners run against HORSES

*The Controller will:
..1 are results uptodate? -deltadate
..2 are raceday uptodate? -deltadate
..3 trackwork and vet
..4 stats module
..5 output 

'''python

3. Yielding only object after some date. 

This is the code from horses2.py file

            for i, r in enumerate(response.css('.bigborder tr')):
                if i:
                    item = Horses2Item(**meta)
                    for j, k in enumerate(('EventDate', 'EventType', 'EventVenue', 'EventDescription', 'Gear')):
                        item[k] = tf(r.xpath("./td[%s]/font/text()" % (j+1)).extract()).replace("\xc2\xa0", " ").strip()
                    item["EventDate"] = datetime.strptime(item["EventDate"], "%d/%m/%Y").date()
                    yield item'''