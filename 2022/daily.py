"""Create daily averages."""

import numpy as np
import pandas as pd

path = "2022/"

meta = pd.read_csv(path + 'meta.csv')

for i, row in meta.iterrows():
    df = pd.read_csv(path + 'data/' + row['box_id'] + '.csv')
    df['date'] = pd.to_datetime(df['date']).dt.date
    pt = pd.pivot_table(df, index='date', values='odd', columns=['name'], aggfunc=np.average).reset_index()
    pt.to_csv(path + 'daily/' + row['box_id'] + '.csv', index=False)