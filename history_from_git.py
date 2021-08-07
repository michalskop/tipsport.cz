"""Get historical rates from git."""

import datetime
import gspread
import subprocess
import time
import xmltodict

sheetkey = "1XUz_SZCHG6DOswnzzHpyI7CkBUMnjq904xX3Zarudxo"

gc = gspread.service_account()
sh = gc.open_by_key(sheetkey)
ws = sh.worksheet('kurzy')

proc = subprocess.run(["git", "log", "--oneline"], stdout=subprocess.PIPE)

output = subprocess.check_output(["git", "log", "--oneline"], text=True)

raw_rows = output.split('\n')

hashes = []
for row in raw_rows:
    it = row.split(' ')
    if (len(it) > 1) and (it[1] == 'Latest'):
        hashes.append(it[0])

hashes.reverse()

kk = 1
for hash in hashes:
    subprocess.run(["git", "checkout", hash])
    with open("../social.xml") as fin:
        xmlb = fin.read()
        xml = (bytes(xmlb, encoding='utf8'))

    data = {}
    main = xmltodict.parse(xml)

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
    
    kk += 1
    # if kk == 3:
    #     break



subprocess.run(["git", "checkout", 'master'])

# len(main['odds']['competition'])

# len(competition['match'])

# competition['match'].keys()

# event.keys()
# event['@name']
# odd['@fullName']