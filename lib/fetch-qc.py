#!/usr/bin/env python3

"""Fetch Questionable Content Strips

Start from number given on command line until the most recent one, into
the current directory

"""

import lxml.html
import requests
import os
import sys

BASEURL = 'http://www.questionablecontent.net'

def main(argv):  # pragma: no cover
    startnumber = int(argv[1])
    number = startnumber
    page = True
    with requests.Session() as session:
        while (page): ## FIXME: we need to check the status
            print(number)
            page = page_for_number(number, session)
            imageurl = '{BASEURL}/{path}'.format(
                BASEURL=BASEURL,
                path=page.xpath(
                    '//img[@id="strip"]/@src')[0])
            print(imageurl)
            with open(os.path.basename(imageurl), 'wb') as f:
                f.write(session.get(imageurl).content)
            number += 1


def page_for_number(number, session):
    url = url_for_number(number)
    content = session.get(url).content
    page = lxml.html.document_fromstring(content)
    return page


def url_for_number(number):
    url_format = '{BASEURL}/view.php?comic={number}'
    url = url_format.format(BASEURL=BASEURL, number=number)
    return url

if __name__ == "__main__":
    sys.exit(main(sys.argv))
