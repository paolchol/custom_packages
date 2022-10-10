# -*- coding: utf-8 -*-
"""
Milano1950 database rearrangement

- Load Serie_storiche_Milano_1950.csv
- Structure the database in a meta and head files

@author: paolo
"""

#%% Setup

import datawrangling as dw
import pandas as pd
import numpy as np

# %% Load

original = pd.read_csv('data/Milano1950/Serie_storiche_Milano_1950.csv')

# %% Split in meta and data dataframes

cols = original.columns.to_list()
metacols = cols[0:5] + [cols[8]]
datacols = [cols[0]] + [cols[5]] + [cols[9]]
meta = original[metacols].copy()
data = original[datacols].copy()

#meta
meta.drop_duplicates('Codice_SIF', inplace = True)
meta['Codice_SIF'] = [f"0{int(idx)}" if not np.isnan(idx) else np.nan for idx in meta['Codice_SIF']]
meta.loc[meta['Codice_SIF'].isna(), 'Codice_SIF'] = 'SIF_NA'
meta.reset_index(drop = True, inplace = True)
meta.set_index('Codice_SIF', inplace = True)
meta.index.names = ['CODICE']
meta['COMUNE'] = 'MILANO'
meta['ORIGINE'] = 'FOG'

#data
data['Codice_SIF'] = [f"0{int(idx)}" if not np.isnan(idx) else np.nan for idx in data['Codice_SIF']]
data.loc[data['Codice_SIF'].isna(), 'Codice_SIF'] = 'SIF_NA'
data.set_index('Codice_SIF', inplace = True)
stdf = dw.stackedDF(data, 'daterows', datecol = 'DATA MISURA')
data = stdf.rearrange(index_label = 'DATA', setdate = True,
                      dateargs = dict(format = "%d/%m/%Y"),
                      pivotargs = dict(columns = 'Codice_SIF', values = 'PIEZOMETRIA'))

meta.to_csv('data/Milano1950/meta_Milano1950.csv')
data.to_csv('data/Milano1950/head_Milano1950.csv')