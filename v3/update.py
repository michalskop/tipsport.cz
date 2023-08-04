"""Download current odds, v3."""

import datetime
import json
import os
import pandas as pd
import requests

url_root_p = "https://partners.tipsport.cz/"
path = "v3/"

# authentization
# the first part is local, the other takes the values from Github secrets
try:
  # sys.path.append('2022')
  import v3.secret as secret
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
headers = {'Content-Type': 'application/json'}
for i in range(10):
  r = requests.post(url_root_p + 'rest/external/common/v2/session', data=json.dumps(credentials), headers=headers, proxies=proxy_servers)
  cookies = r.cookies
  if r.status_code == 200:
    break
  else:
    r2 = requests.get(url_root_p + 'rest/external/offer/v1/matches', headers=headers, cookies=cookies, proxies=proxy_servers)
    print(r.status_code, r2.status_code)

if r.status_code != 200:
  raise Exception('Could not authenticate, status code {}.'.format(r.status_code))

auth = r.json()
cookies = r.cookies
token = auth['sessionToken']
headers = {'Authorization': "Bearer {}".format(token)}

# 'společenské sázky' - get matches
matches = []
r2 = requests.get(url_root_p + 'rest/external/offer/v1/matches', headers=headers, cookies=cookies, proxies=proxy_servers)
data2 = r2.json()
# json.dump(data2, open(path + 'data2test.json', 'w'))

for match in data2['matches']:
  if match['nameSuperSport'] == 'Společenské sázky':
    matches.append(match)
now = datetime.datetime.now()
# json.dump(matches, open(path + 'matchestest.json', 'w'))
"105903"

matches3 = []
for match in matches:
  params = {
    'idCompetition': match['idCompetition'],
    'allEvents': 'True',
  }
  r3 = requests.get(url_root_p + 'rest/external/offer/v1/matches/' + str(match['id']), params=params, headers=headers, cookies=cookies, proxies=proxy_servers)
  data3 = r3.json()
  try:
    matches3.append(data3['match'])
  except:
    pass
# json.dump(matches3, open(path + 'matches3test.json', 'w'))

# 'společenské sázky' - get odds, read / write
try:
  meta = pd.read_csv(path + 'meta.csv')
except:
  meta = pd.DataFrame()
for match in matches3:
  # break
  match_id = match['id']
  try:
    table = pd.read_csv(path + 'data/' + str(match_id) + '.csv')
  except:
    table = pd.DataFrame()
  
  for et in match['eventTables']:
    # odds
    for box in et['boxes']:
      for cell in box['cells']:
        row = {
          'date': now,
          'id': cell['id'],
          'name': cell['name'],
          'odd': cell['odd'],
          'supername': box['name'],
          'hypername': et['name'],
        }
        table = pd.concat([table, pd.DataFrame([row])])

    table = table.drop_duplicates(subset=['id', 'date', 'name'])
    if len(table) > 0:
      table.to_csv(path + 'data/' + str(match_id) + '.csv', index=False)

    # meta
    meta_row = {
      'date': now,
      'match_id': match_id,
      'match_name': match['name'],
      'match_url': match['matchUrl'],
      'competition_id': match['idCompetition'],
      'competition_name': match['nameCompetition'],
      'sport_id': match['idSport'],
      'sport_name': match['nameSport'],
      'date_closed': datetime.datetime.fromtimestamp(match['dateClosed'] / 1000).isoformat(),
      'event_id': et['id'],
      'event_name': et['name'],
    }
    meta = pd.concat([meta, pd.DataFrame([meta_row])])

meta = meta.drop_duplicates(subset=['match_id', 'event_id', 'date'])
meta.to_csv(path + 'meta.csv', index=False)
