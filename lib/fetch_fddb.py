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


def main(argv):
    session = login()
    startdate = dateutil.parser.parse(argv[1])
    lastdate = datetime.datetime.now()
    date = startdate
    days = []
    with login() as session:
        while (date <= lastdate):
            page = page_for_date(date, session)
            day = scrape_day(page, date)
            days.append(day)
            date = next_day(date)
        import pdb; pdb.set_trace()
        pass


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


def page_for_date(date, session):
    url = url_for_day(date)
    content = session.get(url).content
    page = lxml.html.document_fromstring(content)
    return page


def url_for_day(date):
    fddb_date_page_format = 'http://fddb.info/db/i18n/myday20/?lang=de&q={end}&p={start}'
    nextdate = next_day(date)
    start = int(date.timestamp())
    end = int(nextdate.timestamp())
    url = fddb_date_page_format.format(start=start, end=end)
    return url


def scrape_day(page, date):
    foods = scrape_foods(page, date)
    day = dict(
        date=date,
        total=scrape_total(page),
        foods=foods)
    return day


def scrape_total(page):
    calorific = ''.join(page.xpath('//td[span/b="Brennwert"]/following-sibling::td//text()'))
    return {'kcal': parse_kcal(calorific)}


def next_day(date):
    return date + datetime.timedelta(days=1)

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
        kcal = parse_kcal(row.xpath('td[3]//text()')[0])
        fat = parse_g(row.xpath('td[4]//text()')[0])
        carbs = parse_g(row.xpath('td[5]//text()')[0])
        protein = parse_g(row.xpath('td[6]//text()')[0])
        foods.append(dict(
            time=time,
            food=dict(link=food_link,
                      text=food_txt),
            kcal=kcal,
            fat=fat,
            carbs=carbs,
            protein=protein))
    return foods


def parse_kcal(text):
    return int(re.search('(\d+) kcal', text).group(1))


def parse_g(text):
    return float((re.search('([\d,]+) g', text).group(1)).translate(str.maketrans(',', '.')))

if __name__ == "__main__":
    sys.exit(main(sys.argv))
