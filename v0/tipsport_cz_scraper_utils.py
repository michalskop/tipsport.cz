from lxml import html, etree
import re
import requests

import settings

def scrape_race(match):
    url = settings.tipsport_url + settings.tipsport_endpoint
    r = requests.post(url,data={"matchId":match['matchId']})
    data = []
    if r.status_code == 200:
        group = {'identifier': match['matchId']}
        domtree = html.fromstring(r.text)
        trs = domtree.xpath('//tbody/tr')
        date_bet = trs[1].xpath('td/span')[0].text.strip('()')
        rows = []
        for trn in range(2,len(trs)):
            tr = trs[trn]
            item = {}
            try:
                item['title'] = tr.xpath('td')[1].text.strip()
                item['identifier'] = tr.xpath('td/span')[0].text.strip()
                item['odds'] =  tr.xpath('td/a')[0].text.strip()
                item['date_bet'] = date_bet
                rows.append(item)
            except:
                nothing = None
        group['rows'] = rows
        data.append(group)
    return data

def scrape_races(fdir):
    url = settings.tipsport_url2 + fdir
    r = requests.get(url)
    data = []
    if r.status_code == 200:
        domtree = html.fromstring(r.text)
        table = domtree.xpath('//table[@class="tblOdds"]')[0]
        trs = table.xpath('tr[@id="oddViewMain0"]')
        for tr in trs:
            item = {}
            item['title'] = tr.xpath('td/a/span')[0].text.strip().strip(':')
            item['matchId'] = tr.xpath('td/a/span/@data-m')[0]
            data.append(item)
    return data

if __name__ == "__main__":
    # test:
    dat = scrape_races('spolecenske-sazky-25')
    for row in dat:
        data = scrape_race(row)
        print(data)
