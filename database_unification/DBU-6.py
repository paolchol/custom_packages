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
meta['lat'], meta['lon'] = gd.transf_CRS(meta.loc[:, 'X_GB'], meta.loc[:, 'Y_GB'], 'EPSG:3003', 'EPSG:4326', series = True)
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

test = dw.mergemeta(metaDBU, meta, link = codelst,
                    firstmerge = dict(left_index = True, right_index = True),
                    secondmerge = dict(left_index = True, right_on = 'CODICE_PP',
                                       suffixes = ['_DBU', '_SSG']))
#no metadata are merged with the associated codes

# %% Evaluate if it can be meaningful to add some series

#visualize series
dv.interactive_TS_visualization(head, markers = True, title = 'Head from SSGiovanni - check',
                                file = 'plot/dbu/exploratory_DBU-6_SSGiovanni.html')
#all the time series can be meaningful to add, hence they will be added

# %% Insert new meta and time series

#obtain the basin in which the points fall in
meta.to_csv('data/SSGiovanni/DBU-6_tojoin.csv')
#join with the basin shapefile in QGIS
#load the joined file
to_insert = pd.read_csv('data/SSGiovanni/DBU-6_joinQGIS.csv', index_col = 'CODICE')
to_insert.reset_index(inplace = True)
to_insert['CODICE'] = [f"0{int(idx)}" if not np.isnan(idx) else np.nan for idx in to_insert['CODICE']]
to_insert.drop(columns = ['NOME_CI', 'SHAPE_AREA', 'TIPOLOGIA'], inplace = True)
to_insert['X_GB'], to_insert['Y_GB'] = gd.transf_CRS(to_insert.loc[:, 'X_GB'], to_insert.loc[:, 'Y_GB'], 'EPSG:3003', 'EPSG:32632', series = True)
to_insert.rename(columns = {'COD_PTUA16': 'BACINO_WISE',
                            'CODICE': 'CODICE_SIF',
                            'COD_LOCALE': 'CODICE',
                            'X_GB': 'X_WGS84',
                            'Y_GB': 'Y_WGS84',
                            'QUOTA': 'QUOTA_MISU',
                            'FILTRO_DA': 'FILTRI_TOP',
                            'FILTRO_A': 'FILTRI_BOT',
                            'PROF': 'PROFONDITA'}, inplace = True)
to_insert = dw.join_twocols(to_insert, ['TIPO', 'COMPARTO'], rename = "INFO", add = True, onlyna = False)
to_insert['PROVINCIA'] = 'MI'
to_insert['COMUNE'] = 'SESTO SAN GIOVANNI'

metamerge = pd.merge(metaDBU, to_insert, how = 'outer', left_index = True, right_on = 'CODICE')
metamerge = dw.joincolumns(metamerge)
metamerge.set_index('CODICE', inplace = True)

#insert the time series
headDBU = pd.read_csv('data/results/db-unification/head_DBU-5.csv', index_col = 'DATA')
headDBU.index = pd.DatetimeIndex(headDBU.index)

idx = metamerge.loc[to_insert['CODICE'], 'BACINO_WISE'] == 'IT03GWBISSAPTA'
codes = to_insert.loc[idx.values, 'CODICE_SIF']
codes.index = to_insert.loc[idx.values, 'CODICE']

headmerge = dw.mergets(headDBU, head, codes)

metamerge.to_csv('data/results/db-unification/meta_DBU-6.csv')
headmerge.to_csv('data/results/db-unification/head_DBU-6.csv')
