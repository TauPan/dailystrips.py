#!/usr/bin/env python3

# Fetch my fddb food diary

from contextlib import contextmanager
import datetime
import json
import os
import sys
import requests
import re

import dateutil.parser
import lxml.html


FDDBDATEPAGE = 'http://fddb.info/db/i18n/myday20/?lang=de&q={end}&p={start}'


def main(argv):
    session = login()
    startdate = dateutil.parser.parse(argv[1])
    lastdate = datetime.datetime.now()
    date = startdate
    days = []
    with login() as session:
        while (date <= lastdate):
            start = int(date.timestamp())
            nextdate = date + datetime.timedelta(days=1)
            end = int(nextdate.timestamp())
            url = FDDBDATEPAGE.format(
                start=start,
                end=end)
            content = session.get(url).content
            page = lxml.html.document_fromstring(content)
            calorific = ''.join(page.xpath('//td[span/b="Brennwert"]/following-sibling::td//text()'))
            kcal_total = int(re.search('(\d+) kcal', calorific).group(1))
            foods = scrape_foods(page, date)
            day = dict(
                date=date,
                kcal=kcal_total,
                foods=foods)
            days.append(day)
            date = nextdate
        import pdb; pdb.set_trace()
        pass


def scrape_foods(page, date):
    food_rows = page.xpath('//table[@class="myday-table-std"]//tr')
    foods = []
    for row in food_rows:
        time_el = row.xpath('td[1]/span[@class="mydayshowtime"]/text()')
        if not time_el:
            continue
        time = dateutil.parser.parse(time_el[0], default=date)
        food = row.xpath('td[1]/a')[0]
        food_link = food.attrib['href']
        food_txt = food.text
        kcal = int(re.search('(\d+) kcal', row.xpath('td[3]//text()')[0]).group(1))
        fat = float((re.search('([\d,]+) g', row.xpath('td[4]//text()')[0]).group(1)).translate(str.maketrans(',', '.')))
        carbs = float((re.search('([\d,]+) g', row.xpath('td[5]//text()')[0]).group(1)).translate(str.maketrans(',', '.')))
        protein = float((re.search('([\d,]+) g', row.xpath('td[6]//text()')[0]).group(1)).translate(str.maketrans(',', '.')))
        foods.append(dict(
            time=time,
            food=dict(link=food_link,
                      text=food_txt),
            kcal=kcal,
            fat=fat,
            carbs=carbs,
            protein=protein))
    return foods


@contextmanager
def login():
    loginpage = 'https://fddb.info/db/i18n/account/?lang=de&action=login'
    user_pass = {}
    with open(os.path.expanduser('~/secret/login-fddb.json')) as f:
        user_pass = json.load(f);
    with requests.Session() as session:
        session.post(loginpage,
                     {
                         'loginemailorusername': user_pass['user'],
                         'loginpassword': user_pass['password']
                     });
        yield session

if __name__ == "__main__":
    sys.exit(main(sys.argv))
