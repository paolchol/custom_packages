"""
DBU: DataBase Unification
Unificazione del dataset CAP con il database unificato DBU-1

Le operazioni necessarie per ottenere meta e head sono state svolte in
CAP_struct.py

@author: paolo
"""

# %% Setup

import datawrangling as dw
import geodata as gd
import pandas as pd
import numpy as np

# %% Load CAP meta and data

meta = pd.read_csv('data/CAP/meta_CAP.csv', index_col = 'CODICE')
head = pd.read_csv('data/CAP/head_CAP.csv', index_col = 'DATA')
head.index = pd.DatetimeIndex(head.index)

# %% Identify couples of codes

codes_SIF_PP = pd.read_csv('data/general/codes_SIF_PP.csv')
metaDBU = pd.read_csv('data/results/db-unification/meta_DBU-1.csv', index_col = 'CODICE')
metaDBU['CODICE_SIF'] = [f"0{int(idx)}" if not np.isnan(idx) else np.nan for idx in metaDBU['CODICE_SIF']]

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
metamerge.drop(columns = ['COMUNE_CAP', 'X', 'Y', 'lat_CAP', 'lon_CAP'], inplace = True)
metamerge.insert(23, 'z_CAP', metamerge['Z'])
metamerge.drop(columns = 'Z', inplace = True)

# metamerge['CODICE_SIF'] = [f"0{int(idx)}" if not np.isnan(idx) else np.nan for idx in metamerge['CODICE_SIF']]
metamerge.rename(columns = {'CODICE_SIF': 'CODICE_SIF_keep', 'index': 'CODICE_SIF_remove'}, inplace = True)
metamerge = dw.joincolumns(metamerge, '_keep', '_remove')
metamerge = dw.join_twocols(metamerge, ['ORIGINE', 'ORIGINE_CAP'], add = True, onlyna = False)

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
