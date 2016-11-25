# scrapes odds from tipsport.cz and updates github datapackages

import csv
import datapackage #v0.8.3
import datetime
import json
import git
import os
import requests

import tipsport_cz_scraper_utils as utils
import settings

data_path = "data/"  # from this script to data

# repo settings
# repo = git.Repo(settings.git_dir)
# git_ssh_identity_file = settings.ssh_file
# o = repo.remotes.origin
# git_ssh_cmd = 'ssh -i %s' % git_ssh_identity_file

for fdir in settings.tipsport_dirs:
    dat = utils.scrape_races(fdir)
    date = datetime.datetime.utcnow().isoformat()
    for row in dat:
        data = utils.scrape_race(row)
        # load or create datapackage
        try:
            # load datapackage
            datapackage_url = settings.project_url + data_path + row['matchId']  +"/datapackage.json"
            dp = datapackage.DataPackage(datapackage_url)
        except:
            # create datapackage
            dp = datapackage.DataPackage()
            urldp = settings.project_url + "datapackage_prepared.json"
            rdp = requests.get(urldp)
            prepared = rdp.json()
            dp.descriptor['identifier'] = row['matchId']
            dp.descriptor['name'] = "tisport_cz_" + row['matchId']
            dp.descriptor['title'] = row['title'] + " - odds from tipsport.cz"
            dp.descriptor['description'] = "Scraped odds from tipsport.cz for: " + row['title']
            for k in prepared:
                dp.descriptor[k] = prepared[k]
            if not os.path.exists(settings.git_dir + data_path + row['matchId']):
                os.makedirs(settings.git_dir + data_path + row['matchId'])
            with open(settings.git_dir + data_path + row['matchId'] +'/datapackage.json', 'w') as fout:
                fout.write(dp.to_json())
            # repo.git.add(settings.git_dir + data_path + group['identifier']  +'/datapackage.json')
            with open(settings.git_dir + data_path + row['matchId'] +'/odds.csv',"w") as fout:
                header = []
                for resource in dp.resources:
                    if resource.descriptor['name'] == 'odds':
                        for field in resource.descriptor['schema']['fields']:
                            header.append(field['name'])
                dw = csv.DictWriter(fout,header)
                dw.writeheader()
            # repo.git.add(settings.git_dir + data_path + group['identifier']  +'/odds.csv')

        with open(settings.git_dir + data_path + row['matchId']  +'/odds.csv',"a") as fout:
            header = []
            attributes = ['date','title','odds','date_bet','identifier']
            for resource in dp.resources:
                if resource.descriptor['name'] == 'odds':
                    for field in resource.descriptor['schema']['fields']:
                        header.append(field['name'])
            dw = csv.DictWriter(fout,header)
            for ro in data:
                if ro['identifier'] == row['matchId']:
                    for bet in ro['rows']:
                        item = {
                            'date': date,
                            'title': bet['title'],
                            'odds': bet['odds'],
                            'date_bet': bet['date_bet'],
                            'identifier': bet['identifier'],
                        }
                        dw.writerow(item)

        # repo.git.add(settings.git_dir + data_path + group['identifier']  +'/odds.csv')

# with repo.git.custom_environment(GIT_COMMITTER_NAME=settings.bot_name, GIT_COMMITTER_EMAIL=settings.bot_email):
#     repo.git.commit(message="happily updating data %s groups of bets" % (total_groups), author="%s <%s>" % (settings.bot_name, settings.bot_email))
# with repo.git.custom_environment(GIT_SSH_COMMAND=git_ssh_cmd):
#     o.push()
