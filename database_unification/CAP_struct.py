# -*- coding: utf-8 -*-
"""
DBU-2 construction

- Load Soggiacenza_CAP.xls
- Structure the dataase in a meta and head files
- Identify the codes couples between DBU-1 and the obtained metaCAP
- Visualize the coupled piezometers on plotly
- Create DBU-2

@author: paolo
"""

#%% Setup

import datawrangling as dw
import geodata as gd
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
meta.set_index('sif', inplace = True)
meta.index = [f"0{idx}" for idx in meta.index]
meta.index.names = ['CODICE']

#data db arrangment
data[data == 0] = np.nan
data.set_index('sif', inplace = True)
data.index = [f"0{idx}" for idx in data.index]
d = {month: index for index, month in enumerate(months, start = 1) if month}
stdf = dw.stackedDF(data, 'ANNO', d)
data = stdf.rearrange()

#data is not head already, it needs to be calculated from the Z field in meta
head = data.copy()
for col in head.columns:
    head[col] = meta.loc[col, 'Z'] - head[col]

#export as meta and head
meta.to_csv('data/CAP/meta_CAP.csv')
head.to_csv('data/CAP/head_CAP.csv')

# %% Identify couples of codes

codes_SIF_PP = pd.read_csv('data/general/codes_SIF_PP.csv')
metaDBU = pd.read_csv('data/results/db-unification/meta_DBU-1.csv', index_col = 'CODICE')

#Search by code
idx = meta.index.isin(codes_SIF_PP['CODICE_SIF'])
sifpp = codes_SIF_PP.loc[codes_SIF_PP['CODICE_SIF'].isin(meta.index), ['CODICE_SIF', 'CODICE_PP']]
sifpp.set_index('CODICE_SIF', inplace = True)

#Search by position
#Transform meta's coordinates: from Monte Mario to WGS84
meta['lat'], meta['lon'] = gd.transf_CRS(meta.loc[:, 'X'], meta.loc[:, 'Y'], 'EPSG:3003', 'EPSG:4326', series = True)
db_nrst = gd.find_nearestpoint(meta, metaDBU,
                     id1 = 'CODICE', coord1 = ['lon', 'lat'],
                     id2 = 'CODICE', coord2 = ['lon', 'lat'],
                     reset_index = True)
#Select the points with distance less than 100 meters
db_nrst = db_nrst[db_nrst['dist'] < 100]

db_nrst.to_csv('data/CAP/test_pos.csv')

#Merge the two code lists
codelst = pd.merge(sifpp, db_nrst.loc[:, ['CODICE', 'CODICE_nrst']], how = 'outer', left_index = True, right_on = 'CODICE')
codelst.reset_index(inplace = True, drop = True)
codelst.loc[np.invert(codelst['CODICE_nrst'].isna()), 'CODICE_PP'] = codelst.loc[np.invert(codelst['CODICE_nrst'].isna()), 'CODICE_nrst']
codelst.drop(columns = 'CODICE_nrst', inplace = True)
codelst.rename(columns = {'CODICE': 'CODICE_SIF', 'CODICE_PP': 'CODICE_link'}, inplace = True)
codelst.set_index('CODICE_SIF', inplace = True)

# %% Merge metadata

sum(codelst.isin(metaDBU.index).values)
metamerge = dw.mergemeta(metaDBU, meta, link = codelst,
                    firstmerge = dict(left_index = True, right_index = True),
                    secondmerge = dict(left_index = True, right_on = 'CODICE_link',
                                       suffixes = [None, "_CAP"]))
metamerge.rename(columns = {'CODICE_link': 'CODICE'}, inplace = True)
metamerge.set_index('CODICE', inplace = True)
metamerge.drop(columns = ['COMUNE_CAP', 'X', 'Y'], inplace = True)
metamerge.rename(columns = {'Z': 'z_CAP'}, inplace = True)

metamerge['CODICE_SIF'] = [f"0{int(idx)}" if not np.isnan(idx) else np.nan for idx in metamerge['CODICE_SIF']]
metamerge.rename(columns = {'CODICE_SIF': 'CODICE_SIF_keep', 'index': 'CODICE_SIF_remove'}, inplace = True)
metamerge = dw.joincolumns(metamerge, '_keep', '_remove')

metamerge.to_csv('data/results/db-unification/meta_DBU-2.csv')

# %% Merge the time series

headDBU = pd.read_csv('data/results/db-unification/head_DBU-1.csv', index_col='DATA')
headDBU.index = pd.DatetimeIndex(headDBU.index)

idx = (metamerge['CODICE_SIF'].isin(meta.index)) & (metamerge['BACINO_WISE'] == 'IT03GWBISSAPTA')
codes = metamerge.loc[idx, 'CODICE_SIF']
#no codes from CAP are present in IT03GWBISSAPTA
#no need to perform a merge in this condition
#head_DBU-1 is just saved as head_DBU-2

headDBU.to_csv('data/results/db-unification/head_DBU-2.csv')















