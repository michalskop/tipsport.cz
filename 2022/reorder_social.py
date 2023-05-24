"""Get historical rates from git."""

import datetime
import gspread
import requests
import time
import xmltodict

sheetkey = "1XUz_SZCHG6DOswnzzHpyI7CkBUMnjq904xX3Zarudxo"

gc = gspread.service_account()
sh = gc.open_by_key(sheetkey)
ws = sh.worksheet('kurzy')

r = requests.get('https://ban.tipsport.cz/c/feed.php?feed=1101&pid=10661&sid=12302&tid=2161&bid=3284')

data = {}
main = xmltodict.parse(r.content)

date_data = datetime.datetime.strptime(main['odds']['date'], "%d.%m.%Y %H:%M").isoformat()
date_retrieved = datetime.datetime.fromtimestamp(int(main['odds']['timestamp'])/1000).isoformat()

for competition in main['odds']['competition']:
    for event in competition['match']['event']:
        try:
            for odd in event['odd']:
                data[event['@name'] + ": " + odd['@fullName']] = float(odd['@rate'])
        except:
            nothing = True

headers = ws.get('A1:ZZ1')[0]
column_pointer = len(headers)
row_pointer = ws.row_count


for k in data:
    if k not in headers:
        headers.append(k)

h2c = {}
i = 0
for h in headers:
    h2c[h] = i 
    i += 1

row = [None] * i
for k in data:
    row[h2c[k]] = data[k]

row[0] = date_data
row[1] = date_retrieved

ws.append_row(row)
ws.update('A1', [headers])
time.sleep(1.5)

# subprocess.run(["git", "checkout", 'master'])

# len(main['odds']['competition'])

# len(competition['match'])

# competition['match'].keys()

# event.keys()
# event['@name']
# odd['@fullName']