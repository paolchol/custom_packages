# -*- coding: utf-8 -*-
"""
CAP database rearrangement

- Load Soggiacenza_CAP.xls
- Structure the database in a meta and head files

@author: paolo
"""

#%% Setup

import datawrangling as dw
import pandas as pd
import numpy as np

# %% Load

original = pd.read_csv('data/CAP/Soggiacenza_CAP.csv')

#arrange the columns in a meaningful order
cols = original.columns.to_list()
cols = [cols[4]] + cols[0:4] + cols[5:11] + cols[12:14] + [cols[11]] + cols[15:17] + [cols[14]] + cols[17:]

# %% Split in meta and data databases

months = cols[13:]
metacols = cols[0:13]
datacols = ['sif', 'ANNO'] + months
meta = original[metacols].copy()
data = original[datacols].copy()

#meta db arrangment
meta.drop_duplicates('sif', 'last', inplace = True) #last: to maintain the informations in "INDIRIZZO_" and "INDIRIZZO"
meta.drop(columns = ['ID1', 'ANNO', 'codice', 'N_POZZO', 'N_POZZO_TX', 'INDIRIZZO_'], inplace = True)
meta.rename(columns = {'ORIGINE_DA': 'ORIGINE'}, inplace = True)
meta['ORIGINE'] = 'CAP'
meta.set_index('sif', inplace = True)
meta.index = [f"0{idx}" for idx in meta.index]
meta.index.names = ['CODICE']

#data db arrangment
data[data == 0] = np.nan
data.set_index('sif', inplace = True)
data.index = [f"0{idx}" for idx in data.index]
d = {month: index for index, month in enumerate(months, start = 1) if month}
stdf = dw.stackedDF(data, d = d, yearcol = 'ANNO')
data = stdf.rearrange(index_label = 'DATA', dateargs = {}, pivotargs = {})

#data is not head already, it needs to be calculated from the Z field in meta
head = data.copy()
for col in head.columns:
    head[col] = meta.loc[col, 'Z'] - head[col]

#export as meta and head
meta.to_csv('data/CAP/meta_CAP.csv')
head.to_csv('data/CAP/head_CAP.csv')
