#!/usr/bin/env python3
import csv
import json
import sys

import dateutil.parser

ORDER = [
    'date',
    'kcal',
    'carbs',
    'sugar',
    'protein',
    'fat',
    'alcohol',
    'fibre',
    'BE',
    'water',
    'cholesterol',
    'D',
    'C',
    'B1',
    'A',
    'E',
    'B6',
    'B12',
    'B2',
    'iodine',
    'sulfur',
    'manganese',
    'iron',
    'copper',
    'chloride',
    'salt',
    'zinc',
    'calcium',
    'fluoride',
    'potassium',
    'phosphor',
    'magnesium']

def orderkeys(dct):
    keys = dct.keys()
    return [k for k in ORDER if k in keys]

def main(argv):  # pragma: no cover
    infile = argv[1]
    with open(infile) as f:
        days = json.load(f)
    firstdate = dateutil.parser.parse(days[0]['date'])
    lastdate = dateutil.parser.parse(days[-1]['date'])
    total_outfile = 'fddb-totals-{}--{}.csv'.format(
        firstdate.isoformat(),
        lastdate.isoformat())
    days_outfile = 'fddb-days-{}--{}.csv'.format(
        firstdate.isoformat(),
        lastdate.isoformat())
    total_base_rows = orderkeys(days[0]['total'])
    vitamins_rows = orderkeys(days[0]['total']['vitamins'])
    minerals_rows = orderkeys(days[0]['total']['minerals'])
    total_rows = ['date'] + (
        total_base_rows
        + vitamins_rows
        + minerals_rows)
    food_base_rows = orderkeys(days[0]['foods'][0])
    food_rows = (['time']
                 + ['food_name', 'food_link']
                 + food_base_rows)
    with open(total_outfile, 'w', newline='') as tf,\
         open(days_outfile, 'w', newline='') as df:
        tc = csv.writer(tf)
        dc = csv.writer(df)
        tc.writerow(total_rows)
        dc.writerow(food_rows)
        for day in days:
            total = day['total']
            tc.writerow(
                [day['date']]
                + [total[k] for k in total_base_rows]
                + [total['vitamins'][k] for k in vitamins_rows]
                + [total['minerals'][k] for k in minerals_rows])
            for food in day['foods']:
                dc.writerow(
                    [food['food']['time'],
                     food['food']['text'],
                     food['food']['link']]
                    + [food[k]
                       for k in food_base_rows])

if __name__ == "__main__":  # pragma: no cover
    sys.exit(main(sys.argv))
