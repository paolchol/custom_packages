"""
DBU: DataBase Unification
Unificazione del dataset CAP con il database unificato DBU-1

Le operazioni necessarie per ottenere meta e head sono state svolte in
CAP_struct.py

@author: paolo
"""

# %% Setup

import dataanalysis as da
import dataviz as dv
import datawrangling as dw
import geodata as gd
import pandas as pd
import numpy as np

# %% Load CAP meta and data

meta = pd.read_csv('data/CAP/meta_CAP.csv', index_col = 'CODICE')
meta.index = [f"0{int(idx)}" if not np.isnan(idx) else np.nan for idx in meta.index]
meta.index.names = ['CODICE']
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

metamerge.rename(columns = {'CODICE_SIF': 'CODICE_SIF_keep', 'index': 'CODICE_SIF_remove'}, inplace = True)
metamerge = dw.joincolumns(metamerge, '_keep', '_remove')
metamerge = dw.join_twocols(metamerge, ['ORIGINE', 'ORIGINE_CAP'], add = True, onlyna = False)

metamerge.to_csv('data/results/db-unification/meta_DBU-2_firstmerge.csv')

# %% Merge the time series

headDBU = pd.read_csv('data/results/db-unification/head_DBU-1.csv', index_col='DATA')
headDBU.index = pd.DatetimeIndex(headDBU.index)

idx = (metamerge['CODICE_SIF'].isin(meta.index)) & (metamerge['BACINO_WISE'] == 'IT03GWBISSAPTA')
codes = metamerge.loc[idx, 'CODICE_SIF']
#no codes from CAP are present in IT03GWBISSAPTA
#no need to perform a merge in this condition

#head_DBU-1 is just saved as head_DBU-2
headDBU.to_csv('data/results/db-unification/head_DBU-2.csv')

# %% Analyse the metadata not merged, identify points worth to be merged

leftout = meta.loc[np.invert(meta.index.isin(metamerge['CODICE_SIF'])), :].copy()
dv.interactive_TS_visualization(head[leftout.index], markers = True, file = 'plot/dbu/exploratory_DBU-2_CAPleftout.html')

#identify the time series worth adding to DBU
#visualize series which respect some conditions
sel = da.ts_sel_date(head, leftout.index, '01-01-1990', '01-01-2010')
dv.interactive_TS_visualization(head[sel], markers = True,
                                file = 'plot/dbu/exploratory_DBU-2_CAPselection_1990.html',
                                title = 'Time series starting before 1990 and ending after 2010')

sel = da.ts_sel_date(head, leftout.index, delta = 20*365)
dv.interactive_TS_visualization(head[sel], markers = True,
                                file = 'plot/dbu/exploratory_DBU-2_CAPselection_20yrs.html',
                                title = 'Time series with at least 20 years')
#insert in DBU the ones selected by placing delta = 20

# %% Update metamerge

#export meta
sel = da.ts_sel_date(head, leftout.index, delta = 20*365)
leftout.loc[sel, :].to_csv('data/CAP/DBU-2_tojoin.csv')
#join in QGIS with the basin
#load and insert needed informations
to_insert = pd.read_csv('data/CAP/DBU-2_joinQGIS_PROV.csv')
to_insert['CODICE'] = [f"0{int(idx)}" if not np.isnan(idx) else np.nan for idx in to_insert['CODICE']]
to_insert.drop(columns = ['NOME_CI', 'SHAPE_AREA'], inplace = True)
to_insert['X'], to_insert['Y'] = gd.transf_CRS(to_insert.loc[:, 'X'], to_insert.loc[:, 'Y'], 'EPSG:3003', 'EPSG:32632', series = True)
to_insert.rename(columns = {'COD_PTUA16': 'BACINO_WISE',
                            'CODICE': 'CODICE_SIF',
                            'X': 'X_WGS84',
                            'Y': 'Y_WGS84',
                            'Z': 'QUOTA_MISU',
                            'SIGLA': 'PROVINCIA'}, inplace = True)
to_insert['CODICE'] = [f"CAP-{idx}" for idx in to_insert['CODICE_SIF']]
to_insert['z_CAP'] = to_insert['QUOTA_MISU']
#join with metamerge
metamerge = pd.merge(metamerge, to_insert, how = 'outer', left_index = True, right_on = 'CODICE')
metamerge = dw.joincolumns(metamerge)
metamerge.set_index('CODICE', inplace = True)

metamerge.to_csv('data/results/db-unification/meta_DBU-2.csv')

#no new points fall in IT03GWBISSAPTA, so no time series can be added to the
#time series database
