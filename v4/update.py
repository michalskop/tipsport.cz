"""Download current odds, v4."""

import datetime
import json
import os
import pandas as pd
import requests

url_root_p = "https://partners.tipsport.cz/"
path = "v4/"

# authentization
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
# proxy_servers = {
#   'https': os.environ.get('PROXY_SERVERS')
# }

# authentization
headers = {'Content-Type': 'application/x-www-form-urlencoded'}
credentials = {
  'username': os.getenv('TIPSPORT_USER'), 
  'password': os.getenv('TIPSPORT_PASSWORD'),
  'productId': os.getenv('TIPSPORT_PRODUCTID')
}
headers = {'Content-Type': 'application/json'}
for i in range(10):
  r = requests.post(url_root_p + 'rest/external/common/v2/session', data=json.dumps(credentials), headers=headers)
  cookies = r.cookies
  if r.status_code == 200:
    break
  else:
    r2 = requests.get(url_root_p + 'rest/external/offer/v1/matches', headers=headers, cookies=cookies)
    print(r.status_code, r2.status_code)

if r.status_code != 200:
  raise Exception('Could not authenticate, status code {}.'.format(r.status_code))

auth = r.json()
cookies = r.cookies
token = auth['sessionToken']
headers = {'Authorization': "Bearer {}".format(token)}

# set now
now = datetime.datetime.now()
# 'společenské sázky' - get matches
r = requests.get(url_root_p + 'rest/external/offer/v1/matches?allEvents=true&idSuperSport=25', headers=headers, cookies=cookies)
data = r.json()

# if meta file does not exist, create it
try:
  dfmeta = pd.read_csv(path + 'meta.csv')
except:
  dfmeta = pd.DataFrame()

for match in data['matches']:
  match_data = []
  # if match data is not in meta, add it, column match_id may not exist
  if 'match_id' not in dfmeta.columns or dfmeta[dfmeta['match_id'] == match['id']].empty:
    metaitem = {
      'date': now,
      'match_id': match['id'],
      'match_name': match['name'],
      'match_url': match['matchUrl'],
      'competition_id': match['idCompetition'],
      'competion_name': match['nameCompetition'],
      'sport_id': match['idSport'],
      'sport_name': match['nameSport'],
      'date_closed': match['datetimeClosed'],
    }
    dfmeta = pd.concat([dfmeta, pd.DataFrame([metaitem])])
  # else update the date
  else:
    dfmeta.loc[dfmeta['match_id'] == match['id'], 'date'] = now
  # save the meta data
  dfmeta.to_csv(path + 'meta.csv', index=False)

  for event in match['events']:
    for opp in event['opps']:
      item = {
        'date': now,
        'id': opp['id'],
        'name': opp['name'],
        'odd': opp['odd'],
        'event_name': event['name'],
        'selection_id': event['mySelectionId']
      }
      match_data.append(item)
  # try if the match file exists
  try:
    df = pd.read_csv(path + "data/" + str(match['id']) + '.csv')
  except:
    df = pd.DataFrame()
  # concatenate the new data
  df = pd.concat([df, pd.DataFrame(match_data)])
  # save the data
  df['date'] = pd.to_datetime(df['date'])
  df.sort_values(by=['date', 'id'], ascending=[False, True], inplace=True)
  # convert date into iso format in GMT
  df['date'] = df['date'].dt.strftime('%Y-%m-%dT%H:%M:%S')

  df.to_csv(path + "data/" + str(match['id']) + '.csv', index=False)

