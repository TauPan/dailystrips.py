#!/usr/bin/env python3

# Fetch my fddb food diary

import datetime
import dateutil.parser
import os
import sys
import urllib.request
import lxml.html
import re

FDDBDATEPAGE = 'http://fddb.info/db/i18n/myday20/?lang=de&q={end}&p={start}'

def main(argv):
    startdate = dateutil.parser.parse(argv[1])
    lastdate = datetime.datetime.now()
    date = startdate
    while (date <= lastdate):
        start = int(date.timestamp())
        end = (date + datetime.timedelta(days=1)).timestamp()
        url = FDDBDATEPAGE.format(
            start=start,
            end=end)
        page = lxml.html.parse(urllib.request.urlopen(url))
        import pdb; pdb.set_trace()
        pass


if __name__ == "__main__":
    sys.exit(main(sys.argv))
