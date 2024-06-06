"""Create daily averages."""

import numpy as np
import pandas as pd

path = "v4/"

meta = pd.read_csv(path + 'meta.csv')

matches = meta['match_id'].unique()

for match_id in matches:
  try:
    df = pd.read_csv(path + 'data/' + str(match_id) + '.csv')
    df['date'] = pd.to_datetime(df['date']).dt.date
    
    # pivot table
    pt = df.groupby(['date', 'id', 'name', 'event_name', 'selection_id'])['odd'].mean().reset_index()
    # sort by date descending
    pt.sort_values(by='date', ascending=False, inplace=True)
    pt.to_csv(path + 'daily/' + str(match_id) + '.csv', index=False)
  except:
    pass
