# -*- coding: utf-8 -*-
"""
DBU: DataBase Unification
Unificazione del dataset Milano1950 con il database unificato DBU-6

Le operazioni necessarie per ottenere meta e head sono state svolte in
SSGiovanni_struct.py

@author: paolo
"""

# %% Setup

import dataviz as dv
import datawrangling as dw
import geodata as gd
import pandas as pd
import numpy as np

# %% Load Milano1950 meta and data

meta = pd.read_csv('data/SSGiovanni/meta_SSGiovanni.csv', index_col = 'CODICE')
head = pd.read_csv('data/SSGiovanni/head_SSGiovanni.csv', index_col = 'DATA')
meta.index = [f"0{int(idx)}" if not np.isnan(idx) else np.nan for idx in meta.index]
meta.index.names = ['CODICE']
head.index = pd.DatetimeIndex(head.index)

# %% Identify couples of codes

codes_SIF_PP = pd.read_csv('data/general/codes_SIF_PP.csv')
metaDBU = pd.read_csv('data/results/db-unification/meta_DBU-5.csv', index_col = 'CODICE')
metaDBU['CODICE_SIF'] = [f"0{int(idx)}" if not np.isnan(idx) else np.nan for idx in metaDBU['CODICE_SIF']]

#Search by code
# idx = meta.index.isin(codes_SIF_PP['CODICE_SIF'])
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

#no points are at a lower distance than 100 m. so the only codes available are
#the ones from the code database
codelst = sifpp

# %% Merge metadata

metamerge = dw.mergemeta(metaDBU, meta, link = codelst,
                    firstmerge = dict(left_index = True, right_index = True),
                    secondmerge = dict(left_index = True, right_on = 'CODICE_PP',
                                       suffixes = ['_DBU', '_SSG']))
#no metadata are merged
#evaluate if it can be meaningful to add some series

dv.interactive_TS_visualization(head, markers = True, title = 'Head from SSGiovanni - check')

headDBU = pd.read_csv('data/results/db-unification/head_DBU-5.csv', index_col = 'DATA')
headDBU.index = pd.DatetimeIndex(headDBU.index)
dv.interactive_TS_visualization(headDBU[metaDBU.loc[metaDBU['COMUNE'].isin(['OSNAGO', 'MEZZAGO']), :].index], markers = True)
