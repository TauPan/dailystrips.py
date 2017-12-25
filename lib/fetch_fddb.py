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
    trs = page.xpath('//p[@id="fddb-myday-printinfo"]/following-sibling::table[1]//tr')
    return {'kcal':
            parse_kcal(trs[0].xpath('.//td[2]/text()')[0]),
            # every following xpath is identical after tr[n], but kcal
            # must really be different or it won't match (kJ would match, though)
            'fat': parse_g(trs[1].xpath('./td[2]//text()')[0]),
            'carbs': parse_g(trs[2].xpath('.//td[2]//text()')[0]),
            'sugar': parse_g(trs[3].xpath('.//td[2]//text()')[0]),
            'protein': parse_g(trs[4].xpath('.//td[2]//text()')[0]),
            'alcohol': parse_g(trs[5].xpath('.//td[2]//text()')[0]),
            'water': parse_liters(trs[6].xpath('.//td[2]//text()')[0]),
            'fibre': parse_g(trs[7].xpath('.//td[2]//text()')[0]),
            'cholesterol': parse_mg(trs[8].xpath('.//td[2]//text()')[0]),
            'BE': parse_german_float(trs[9].xpath('.//td[2]//text()')[0])}


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
    return parse_german_float(re.search('([\d,]+) g', text).group(1))


def parse_mg(text):
    return parse_german_float(re.search('([\d,]+) mg', text).group(1))


def parse_liters(text):
    return parse_german_float(re.search('([\d,]+) Liter', text).group(1))


def parse_german_float(text):
    return float(text.translate(str.maketrans(',', '.')))

if __name__ == "__main__":
    sys.exit(main(sys.argv))
