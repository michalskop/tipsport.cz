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
    # v3.1 vs 3.0
    if 'supername' in df.columns:
      df['new_name'] = df['hypername'].fillna('') + ' - ' + df['supername'].fillna('') + ': ' + df['name']
      df['new_supername'] = df['hypername'].fillna('') + ' - ' + df['supername'].fillna('')
      new_supernames = df['new_supername'].unique()
      if len(new_supernames) > 2: # v3.0 + v3.1
        pt = pd.pivot_table(df, index='date', values='odd', columns=['new_name'], aggfunc=np.average).reset_index()
      else:
        pt = pd.pivot_table(df, index='date', values='odd', columns=['name'], aggfunc=np.average).reset_index()
    # v3.0
    else:
      pt = pd.pivot_table(df, index='date', values='odd', columns=['name'], aggfunc=np.average).reset_index()
    pt.to_csv(path + 'daily/' + str(match_id) + '.csv', index=False)
  except:
    pass
