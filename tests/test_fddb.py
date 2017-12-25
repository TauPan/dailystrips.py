import datetime
from unittest import mock
import os

import lxml.html

from lib import fetch_fddb as fddb

def test_page_for_date():
    session = mock.Mock()
    body_text = 'Test for (1980, 1, 1)'
    content = '<html><body>{}</body></html>'.format(body_text)
    session.get.return_value.content = content
    page = fddb.page_for_date(datetime.datetime(1980, 1, 1), session)
    session.get.assert_called_with(
        'http://fddb.info/db/i18n/myday20/?lang=de&q=315615600&p=315529200')
    assert page.xpath('//body//text()')[0] == body_text

def test_url_for_day():
    assert (
        fddb.url_for_day(datetime.datetime(1980, 1, 1))
        == 'http://fddb.info/db/i18n/myday20/?lang=de&q=315615600&p=315529200')


def test_scrape_day():
    content = ''
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           'Detailansicht - 2017-06-02 - Fddb.html'),
              'rb') as f:
        content = f.read()
    page = lxml.html.document_fromstring(content)
    date = datetime.datetime(2017, 6, 2)
    ret = fddb.scrape_day(page, date)
    assert ret['date'] == date
    total = ret['total']
    assert total['kcal'] == 1747
    assert total['fat'] == 51.6
    assert total['carbs'] == 189.5
    assert total['sugar'] == 72.3
    assert total['protein'] == 95.2
    assert total['alcohol'] == 12.2
    assert total['water'] == 1
    assert total['fibre'] == 31.3
    assert total['cholesterol'] == 58
    assert total['BE'] == 15.8
    vitamins = total['vitamins']
    assert vitamins['C'] == 6.3
    assert vitamins['A'] == 0
    assert vitamins['D'] == 0
    assert vitamins['E'] == 0.2
    assert vitamins['B1'] == 0.4679
    assert vitamins['B2'] == 0.3
    assert vitamins['B6'] == 8.7
    assert vitamins['B12'] == 4.6
    food0 = ret['foods'][0]
    assert food0['time'] == datetime.datetime(2017, 6, 2, 23, 30)
    assert food0['food']['link'] == 'http://fddb.info/db/de/lebensmittel/brauerei_beck_becks_bier_pils/index.html'
    assert food0['food']['text'] == 'kleine Flasche Beck\'s Bier, Pils'
    assert food0['kcal'] == 125
    assert food0['fat'] == 0
    assert food0['carbs'] == 7.3
    assert food0['protein'] == 1.2
