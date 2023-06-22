"""Create daily averages."""

import numpy as np
import pandas as pd

path = "v3/"

meta = pd.read_csv(path + 'meta.csv')

matches = meta['match_id'].unique()

for match_id in matches:
  try:
    df = pd.read_csv(path + 'data/' + str(match_id) + '.csv')
    df['date'] = pd.to_datetime(df['date']).dt.date
    pt = pd.pivot_table(df, index='date', values='odd', columns=['name'], aggfunc=np.average).reset_index()
    pt.to_csv(path + 'daily/' + str(match_id) + '.csv', index=False)
  except:
    pass
