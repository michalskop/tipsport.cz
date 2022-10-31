"""Download current odds"""

import datetime
import os
import pandas as pd
import requests
import sys

url_root = "https://m.tipsport.cz/"
path = "2022/"

# authentization
# the first part is local, the other takes the values from Github secrets
try:
  sys.path.append('2022')
  import secret
  os.environ['TIPSPORT_USER'] = secret.TIPSPORT_USER
  os.environ['TIPSPORT_PASSWORD'] = secret.TIPSPORT_PASSWORD
  os.environ['TIPSPORT_PRODUCTID'] = secret.TIPSPORT_PRODUCTID
  os.environ['PROXY_SERVERS'] = secret.PROXY_SERVERS
except:
  pass

# proxy
proxy_servers = {
  'https': os.environ.get('PROXY_SERVERS')
}

# authentization
headers = {'Content-Type': 'application/x-www-form-urlencoded'}
credentials = {
  'username': os.getenv('TIPSPORT_USER'), 
  'password': os.getenv('TIPSPORT_PASSWORD'),
  'productId': os.getenv('TIPSPORT_PRODUCTID')
}

r = requests.post(url_root + 'rest/common/v1/session', data=credentials, headers=headers, proxies=proxy_servers)
auth = r.json()
cookies = r.cookies
token = auth['sessionToken']
headers = {'Authorization': "Bearer {}".format(token)}

# 'společenské sázky' - get matches
r1 = requests.get(url_root + 'rest/external/offer/v1/sports', headers=headers, cookies=cookies, proxies=proxy_servers)
data = r1.json()

matches = []
for category in data['data']['children']:
  for supersport in category['children']:
    if supersport['title'] == 'Společenské sázky':
      for sport in supersport['children']:
        for match in sport['children']:
          item = {
            'sport_title': sport['title'],
            'match_title': match['title'],
            'match_id': match['id']
          }
          matches.append(item)

# get races
races = []
for match in matches:
  r2 = requests.get(url_root + 'rest/external/offer/v2/competitions/{}/matches'.format(match['match_id']), headers=headers, cookies=cookies, proxies=proxy_servers)
  data2 = r2.json()
  for race in data2['matches']:
    item = match.copy()
    item['race_name'] = race['name']
    item['race_id'] = race['id']
    races.append(item)

# get details
events = []
now = datetime.datetime.now().isoformat()
for race in races:
  r3 = requests.get(url_root + 'rest/offer/v2/matches/{}?withOdds=true'.format(race['race_id']), headers=headers, cookies=cookies, proxies=proxy_servers)
  # print(race['race_name'])
  data3 = r3.json()
  datetimeClosed = data3['match']['datetimeClosed']
  for table in data3['match']['eventTables']:
    for box in table['boxes']:
      item = race.copy()
      item['match_close'] = datetimeClosed
      item['event_name'] = table['name']
      item['box_id'] = box['id']
      item['box_name'] = box['name']
      item['cells'] = []
      for cell in box['cells']:
        it = {
          'id': cell['id'],
          'name': cell['name'],
          'odd': cell['odd'],
          'date': now

        }
        item['cells'].append(it)
      events.append(item)


# prepare tables
try:
  meta = pd.read_csv(path + 'meta.csv')
except:
  meta = pd.DataFrame()
for event in events:
  e = event.copy()
  del e['cells']
  if (len(meta.index) == 0) or (meta.loc[meta['box_id'] == e['box_id']].empty):
    meta = meta.append(e, ignore_index=True)
  
  try:
    table = pd.read_csv(path + 'data/' + str(event['box_id']) + '.csv')
  except:
    table = pd.DataFrame()
  for cell in event['cells']:
    table = table.append(cell, ignore_index=True)
  table['id'] = table['id'].astype(int)
  table.to_csv(path + 'data/' + str(event['box_id']) + '.csv', index=False)

ids = ['match_id', 'race_id']
for i in ids:
  meta[i] = meta[i].astype(int)

meta.to_csv(path + 'meta.csv', index=False)


  

meta.to_csv('meta.csv')
