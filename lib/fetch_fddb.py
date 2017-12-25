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


def main(argv):  # pragma: no cover
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
def login():  # pragma: no cover
    loginpage = 'https://fddb.info/db/i18n/account/?lang=de&action=login'
    password_file = '~/secret/login-fddb.json'
    user_pass = {}
    with open(os.path.expanduser(password_file)) as f:
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
    url_format = 'http://fddb.info/db/i18n/myday20/?lang=de&q={end}&p={start}'
    nextdate = next_day(date)
    start = int(date.timestamp())
    end = int(nextdate.timestamp())
    url = url_format.format(start=start, end=end)
    return url


def scrape_day(page, date):
    foods = scrape_foods(page, date)
    day = dict(
        date=date,
        total=scrape_total(page),
        foods=foods)
    return day


def scrape_total(page):
    nutr_trs = page.xpath(
        '//p[@id="fddb-myday-printinfo"]/following-sibling::table[1]//tr')

    def nutr(index, path='./td[2]//text()'):
        return nutr_trs[index].xpath(path)[0]

    vit_trs = page.xpath(
        '//h3[.="Vitamine"]/following-sibling::table[1]//tr')

    def vit(index, path='./td[2]//text()'):
        return vit_trs[index].xpath(path)[0]

    min_trs = page.xpath(
        '//h3[.="Mineralstoffe"]/following-sibling::table[1]//tr')

    def min(index, path='./td[2]//text()'):
        return min_trs[index].xpath(path)[0]

    ret = enumerate_parse_extract(
        parse_g, nutr,
        ['kcal', parse_kcal, nutr, './/td[2]/text()'],
        'fat', 'carbs', 'sugar', 'protein', 'alcohol',
        ['water', parse_liters],
        'fibre',
        ['cholesterol', parse_mg],
        ['BE', parse_german_float]
    )

    ret ['vitamins'] = enumerate_parse_extract(
        parse_mg, vit,
        'C', 'A', 'D', 'E', 'B1', 'B2', 'B6',
        ['B12', parse_ug])
    ret ['minerals'] = enumerate_parse_extract(
        parse_mg, min,
        ['salt', parse_g],
        'iron', 'zinc', 'magnesium', 'manganese',
        'fluoride', 'chloride', 'copper', 'potassium',
        'calcium', 'phosphor', 'sulfur', 'iodine')
    return ret


def enumerate_parse_extract(parse_default, extract_default, *lst):
    ret = {}
    for i, it in enumerate(lst):
        extract = extract_default
        parse = parse_default
        if it is None:
            continue
        if type(it) == str:
            key = it
            args = []
        else:
            key, *args = it
        if args:
            parse = args.pop(0)
        if args:
            extract = args.pop(0)
        ret[key] = parse(extract(i, *args))
    return ret


def next_day(date):
    return date + datetime.timedelta(days=1)

def scrape_foods(page, date):

    def time_on_date(str):
        return dateutil.parser.parse(str, default=date)

    def split_food(food):
        return {
            'time': time_on_date(
                food.xpath(
                    'span[@class="mydayshowtime"]/text()')[0]),
            'link': food.xpath('a')[0].attrib['href'],
            'text': food.xpath('a')[0].text }


    food_rows = page.xpath('//table[@class="myday-table-std"]//tr')
    foods = []
    for row in food_rows:
        try:
            tds = row.xpath('td')

            def tot(index, path='.//text()'):
                return tds[index].xpath(path)[0]

            ret = enumerate_parse_extract(
                parse_g,
                tot,
                ['food', split_food, tot, '.'],
                None,
                ['kcal', parse_kcal],
                'fat', 'carbs', 'protein')
            ret['time'] = ret['food']['time']
            del ret['food']['time']
            foods.append(ret)
        except IndexError as e:
            continue
    return foods


def parse_kcal(text):
    return int(re.search('(\d+) kcal', text).group(1))


def parse_g(text):
    return parse_german_float(re.search('([\d,]+) g', text).group(1))


def parse_mg(text):
    return parse_german_float(re.search('([\d,]+) mg', text).group(1))

def parse_ug(text):
    return parse_german_float(re.search('([\d,]+) μg', text).group(1))
    # character: μ (displayed as μ) (codepoint 956, #o1674, #x3bc)
    # this is different from the µ character on my keyboard:
    # character: µ (displayed as µ) (codepoint 181, #o265, #xb5)

def parse_liters(text):
    return parse_german_float(re.search('([\d,]+) Liter', text).group(1))


def parse_german_float(text):
    return float(text.translate(str.maketrans(',', '.')))

if __name__ == "__main__":  # pragma: no cover
    sys.exit(main(sys.argv))
