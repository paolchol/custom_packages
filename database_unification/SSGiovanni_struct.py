# -*- coding: utf-8 -*-
"""
SSGiovanni database rearrangement

- Load the original files from SSGiovanni folder
- Structure the database in a meta and head files

@author: paolo
"""

#%% Setup

import datawrangling as dw
import pandas as pd
import numpy as np

# %% Load

meta = pd.read_csv('data/SSGiovanni/meta_original.csv')
data = pd.read_csv('data/SSGiovanni/data_original.csv')

# %% Obtain meta and data in the standard format

#complete meta with SIF codes
codes = data.drop_duplicates('SIF', keep = 'last').drop(columns = data.iloc[:, 2:].columns.to_list()).copy()
codes.iloc[5:, 1] = ['UN.PS.001', 'UN.PS.003']
meta.set_index('Nome', inplace = True)
meta = pd.merge(meta, codes, left_index = True, right_on = 'COD_LOC')
meta.set_index('SIF', inplace = True)
meta.index = [f"0{int(idx)}" if not np.isnan(idx) else np.nan for idx in meta.index]
meta.index.names = ['CODICE']
meta['ORIGINE'] = 'SSGiovanni'

#rearrange data
data.drop(columns = 'COD_LOC', inplace = True)
data.set_index('SIF', inplace = True)
data.index = [f"0{int(idx)}" if not np.isnan(idx) else np.nan for idx in data.index]
data.index.names = ['CODICE_SIF']
stdf = dw.stackedDF(data, 'daterows', datecol = 'DATA')
data = stdf.rearrange(index_label = 'DATA', setdate = True,
                      dateargs = dict(format = "%d/%m/%Y"),
                      pivotargs = dict(columns = 'CODICE_SIF', values = 'Livello piezometrico (m slm)'))

# %% Save only meta and data relative to PS code

# XX.PP codes are not in the superficial acquifer, export only the ones with
# PS in the code
idx = [code.split('.')[1] == 'PS' for code in meta['COD_LOC']]
meta = meta.loc[idx, :]
data = data.loc[:, data.columns.isin(meta.index)]

meta.to_csv('data/SSGiovanni/meta_SSGiovanni.csv')
data.to_csv('data/SSGiovanni/head_SSGiovanni.csv')