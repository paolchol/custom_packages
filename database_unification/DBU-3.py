# -*- coding: utf-8 -*-
"""
DBU: DataBase Unification
Unificazione del dataset Idroscalo2005 con il database unificato DBU-3

Le operazioni necessarie per ottenere meta e head sono state svolte in
Idroscalo2005_struct.py

@author: paolo
"""

# %% Setup

import dataviz as dv
import datawrangling as dw
import geodata as gd
import pandas as pd
import numpy as np

# %% Load Idroscalo2005 meta and data

meta = pd.read_csv('data/Idroscalo2005/meta_Idroscalo2005.csv', index_col = 'CODICE')
head = pd.read_csv('data/Idroscalo2005/head_Idroscalo2005.csv', index_col = 'DATA')

meta.index = [f"0{idx}" for idx in meta.index]
meta.index.names = ['CODICE']
head.index = pd.DatetimeIndex(head.index)

# %% Identify couples of codes

codes_SIF_PP = pd.read_csv('data/general/codes_SIF_PP.csv')
metaDBU = pd.read_csv('data/results/db-unification/meta_DBU-2.csv', index_col = 'CODICE')
metaDBU['CODICE_SIF'] = [f"0{int(idx)}" if not np.isnan(idx) else np.nan for idx in metaDBU['CODICE_SIF']]

#Search by code
idx = meta.index.isin(codes_SIF_PP['CODICE_SIF'])
sifpp = codes_SIF_PP.loc[codes_SIF_PP['CODICE_SIF'].isin(meta.index), ['CODICE_SIF', 'CODICE_PP']]
sifpp.set_index('CODICE_SIF', inplace = True)

#Search by position
#Transform meta's coordinates: from Monte Mario to WGS84
meta['lat'], meta['lon'] = gd.transf_CRS(meta.loc[:, 'x'], meta.loc[:, 'y'], 'EPSG:3003', 'EPSG:4326', series = True)
db_nrst = gd.find_nearestpoint(meta, metaDBU,
                     id1 = 'CODICE', coord1 = ['lon', 'lat'],
                     id2 = 'CODICE', coord2 = ['lon', 'lat'],
                     reset_index = True)
#Select the points with distance less than 100 meters
db_nrst = db_nrst[db_nrst['dist'] < 100]

#Merge the two code lists
codelst = pd.merge(sifpp, db_nrst.loc[:, ['CODICE', 'CODICE_nrst']], how = 'outer', left_index = True, right_on = 'CODICE')
codelst.reset_index(inplace = True, drop = True)
codelst.loc[np.invert(codelst['CODICE_nrst'].isna()), 'CODICE_PP'] = codelst.loc[np.invert(codelst['CODICE_nrst'].isna()), 'CODICE_nrst']
codelst.drop(columns = 'CODICE_nrst', inplace = True)
codelst.rename(columns = {'CODICE': 'CODICE_SIF', 'CODICE_PP': 'CODICE_link'}, inplace = True)
codelst.set_index('CODICE_SIF', inplace = True)

# %% Merge metadata

print(sum(metaDBU['CODICE_SIF'].isin(meta.index)))
print(sum(codelst.isin(metaDBU.index).values)[0])
metamerge = dw.mergemeta(metaDBU, meta, link = codelst,
                    firstmerge = dict(left_index = True, right_index = True),
                    secondmerge = dict(left_index = True, right_on = 'CODICE_link',
                                       suffixes = [None, "_I2005"]))
metamerge.rename(columns = {'CODICE_link': 'CODICE', 'index': 'CODICE_SIF_I2005'}, inplace = True)
metamerge.set_index('CODICE', inplace = True)

metamerge.insert(24, 'z_I2005', metamerge['z'])
metamerge.drop(columns = ['z', 'x', 'y', 'lat_I2005', 'lon_I2005'], inplace = True)
metamerge = dw.join_twocols(metamerge, ['ORIGINE', 'ORIGINE_I2005'], add = True, onlyna = False)
metamerge = dw.join_twocols(metamerge, ['CODICE_SIF', 'CODICE_SIF_I2005'])
metamerge = dw.joincolumns(metamerge, '_dbu', '_I2005')

metamerge.to_csv('data/results/db-unification/meta_DBU-3.csv')

# %% Merge time series

headDBU = pd.read_csv('data/results/db-unification/head_DBU-2.csv', index_col='DATA')
headDBU.index = pd.DatetimeIndex(headDBU.index)

idx = (metamerge['CODICE_SIF'].isin(meta.index)) & (metamerge['BACINO_WISE'] == 'IT03GWBISSAPTA')
codes = metamerge.loc[idx, 'CODICE_SIF']
headmerge = dw.mergets(headDBU, head, codes)

#Visualize the result
vis = head[codes]
vismerge = headmerge[codes.index]
visdbu = headDBU[codes.index]
dv.interactive_TS_visualization(vismerge, file = 'plot/dbu/added_ts_DBU-3.html')

headmerge.to_csv('data/results/db-unification/head_DBU-3.csv')
