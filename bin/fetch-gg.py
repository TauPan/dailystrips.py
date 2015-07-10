#!/usr/bin/env python

# just an experiment, also so I can read girl genius on my tablet more
# comfortably

import os
import sys
import urllib
import lxml.html
import re

GGDATEPAGE = 'http://www.girlgeniusonline.com/comic.php?date='


# I only tested this from 20131028 on
def main(argv):
    startdate = argv[1]
    starturl = "{}{}".format(
        GGDATEPAGE,
        startdate)
    startpage = lxml.html.parse(urllib.urlopen(starturl))
    lastpage = startpage.xpath("//a[@id='toplast']/@href")[0]
    lastdate = re.search("([0-9]{8})$", lastpage).group(1)
    date = startdate
    page = startpage
    while (date <= lastdate):  # FIXME: fix loop condition, this will
                               # never work, because there's no link
                               # on the last page
        # FIXME: Something will fail (404) with an ad on the 20150521 page
        imageurl = page.xpath(
            "/html/body/div[@id='wrapper']"
            "/div[@id='comicarea']/"
            "div[@id='comicrepeat']"
            "/div[@id='comicbody']/a/img/@src")[0]
        print(imageurl)
        with open(os.path.basename(imageurl), 'w') as f:
            f.write(urllib.urlopen(imageurl).read())
        nexturl = page.xpath("//a[@id='topnext']/@href")[0]
        date = re.search("([0-9]{8})$", nexturl).group(0)
        page = lxml.html.parse(urllib.urlopen(nexturl))

if __name__ == "__main__":
    sys.exit(main(sys.argv))
