# -*- coding: utf-8 -*-
"""
DBU: DataBase Unification
Unificazione del dataset Olona con il database unificato DBU-3

Le operazioni necessarie per ottenere meta e head sono state svolte in
Olona_struct.py

@author: paolo
"""

# %% Setup

import dataviz as dv
import datawrangling as dw
import geodata as gd
import pandas as pd
import numpy as np

# %% Load Olona meta and data

meta = pd.read_csv('data/Olona/meta_Olona_filtered.csv', index_col = 'CODICE')
head = pd.read_csv('data/Olona/head_Olona.csv', index_col = 'DATA')
head.index = pd.DatetimeIndex(head.index)

# %% Identify couples of codes

codes_SIF_PP = pd.read_csv('data/general/codes_SIF_PP.csv')
metaDBU = pd.read_csv('data/results/db-unification/meta_DBU-3.csv', index_col = 'CODICE')
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
codelst = dw.join_twocols(codelst, ['CODICE_PP', 'CODICE_nrst'])
codelst.rename(columns = {'CODICE': 'CODICE_Olona', 'CODICE_PP': 'CODICE_link'}, inplace = True)
codelst.set_index('CODICE_Olona', inplace = True)

# %% Merge metadata

print(sum(metaDBU['CODICE_SIF'].isin(meta.index)))
print(sum(codelst.isin(metaDBU.index).values)[0])
metamerge = dw.mergemeta(metaDBU, meta, link = codelst,
                    firstmerge = dict(left_index = True, right_index = True),
                    secondmerge = dict(left_index = True, right_on = 'CODICE_link',
                                       suffixes = ['_DBU', "_Olona"]))
metamerge.rename(columns = {'CODICE_link': 'CODICE', 'index': 'CODICE_Olona'}, inplace = True)
metamerge.set_index('CODICE', inplace = True)

metamerge.insert(25, 'z_Olona', metamerge['Q'])
#CODICE_Olona doesn't provide additional information, thus it's dropped
todrop = ['Q', 'DENOMINAZIONE', 'PUBBLICO', 'STRAT.', 'X', 'Y', 'PROV', 'CODICE_Olona']
metamerge.drop(columns = todrop, inplace = True)

#join overlapping columns
metamerge = dw.joincolumns(metamerge, '_DBU', '_Olona')
metamerge = dw.join_twocols(metamerge, ["INDIRIZZO", "LOCALITA'"], rename = "INFO")
metamerge = dw.join_twocols(metamerge, ["INFO_PTUA2003", "INFO"], rename = "INFO")

metamerge.to_csv('data/results/db-unification/meta_DBU-4.csv')

#%% Merge time series

headDBU = pd.read_csv('data/results/db-unification/head_DBU-3.csv', index_col = 'DATA')
headDBU.index = pd.DatetimeIndex(headDBU.index)

codelst = codelst.loc[codelst.isin(metamerge.index).values, :]
codelst.reset_index(drop = False, inplace = True)
codelst.set_index('CODICE_link', inplace = True)
codelst = codelst.squeeze()
sum(codelst.index.isin(headDBU.columns))
headmerge = dw.mergets(headDBU, head, codelst)

#Visualize the result
vis = head[codelst]
vismerge = headmerge[codelst.index]
visdbu = headDBU[codelst.index]
dv.interactive_TS_visualization(vismerge, file = 'plot/dbu/added_ts_DBU-4.html')

headmerge.to_csv('data/results/db-unification/head_DBU-4.csv')
