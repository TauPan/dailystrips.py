#!/usr/bin/env python3
import csv
import json
import sys

import dateutil.parser

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
    total_base_rows = list(days[0]['total'].keys() - ['vitamins', 'minerals'])
    total_rows = ['date'] + (
        total_base_rows
        + list(days[0]['total']['vitamins'].keys())
        + list(days[0]['total']['minerals'].keys()))
    food_base_rows = list(days[0]['foods'][0].keys() - ['food'])
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
                + [total['vitamins'][k] for k in total['vitamins'].keys()]
                + [total['minerals'][k] for k in total['minerals'].keys()])
            for food in day['foods']:
                dc.writerow(
                    [food['food']['time'],
                     food['food']['text'],
                     food['food']['link']]
                    + [food[k]
                       for k in food_base_rows])

if __name__ == "__main__":  # pragma: no cover
    sys.exit(main(sys.argv))
