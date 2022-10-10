# -*- coding: utf-8 -*-
"""
DBU: DataBase Unification
Unificazione del dataset Milano1950 con il database unificato DBU-5

Le operazioni necessarie per ottenere meta e head sono state svolte in
Milano1950_struct.py

@author: paolo
"""

# %% Setup

import dataviz as dv
import datawrangling as dw
import geodata as gd
import pandas as pd
import numpy as np

# %% Load Milano1950 meta and data

meta = pd.read_csv('data/Milano1950/meta_Milano1950.csv', index_col = 'CODICE')
head = pd.read_csv('data/Milano1950/head_Milano1950.csv', index_col = 'DATA')
head.index = pd.DatetimeIndex(head.index)

# %% Identify couples of codes

codes_SIF_PP = pd.read_csv('data/general/codes_SIF_PP.csv')
metaDBU = pd.read_csv('data/results/db-unification/meta_DBU-4.csv', index_col = 'CODICE')
metaDBU['CODICE_SIF'] = [f"0{int(idx)}" if not np.isnan(idx) else np.nan for idx in metaDBU['CODICE_SIF']]

#Search by code
# idx = meta.index.isin(codes_SIF_PP['CODICE_SIF'])
sifpp = codes_SIF_PP.loc[codes_SIF_PP['CODICE_SIF'].isin(meta.index), ['CODICE_SIF', 'CODICE_PP']]
sifpp.set_index('CODICE_SIF', inplace = True)

#Search by position
#Transform meta's coordinates: from Monte Mario to WGS84
meta['lat'], meta['lon'] = gd.transf_CRS(meta.loc[:, 'Coord_X'], meta.loc[:, 'Coord_Y'], 'EPSG:3003', 'EPSG:4326', series = True)
db_nrst = gd.find_nearestpoint(meta, metaDBU,
                     id1 = 'CODICE', coord1 = ['lon', 'lat'],
                     id2 = 'CODICE', coord2 = ['lon', 'lat'],
                     reset_index = True)
#Select the points with distance less than 100 meters
db_nrst = db_nrst[db_nrst['dist'] < 100]

#Merge the two code lists
codelst = pd.merge(sifpp, db_nrst.loc[:, ['CODICE', 'CODICE_nrst']], how = 'outer', left_index = True, right_on = 'CODICE')
codelst.reset_index(inplace = True, drop = True)
codelst = dw.join_twocols(codelst, ['CODICE_PP', 'CODICE_nrst'], onlyna = False)
codelst.rename(columns = {'CODICE': 'CODICE_SIF', 'CODICE_PP': 'CODICE_link'}, inplace = True)
codelst.set_index('CODICE_SIF', inplace = True)

# %% Merge metadata

print(sum(metaDBU['CODICE_SIF'].isin(meta.index)))
print(sum(codelst.isin(metaDBU.index).values)[0])
metamerge = dw.mergemeta(metaDBU, meta, link = codelst,
                    firstmerge = dict(left_index = True, right_index = True),
                    secondmerge = dict(left_index = True, right_on = 'CODICE_link',
                                       suffixes = ['_DBU', '_Milano1950']))
metamerge.rename(columns = {'CODICE_link': 'CODICE', 'index': 'CODICE_Milano1950'}, inplace = True)
metamerge.set_index('CODICE', inplace = True)
#Look for additional points which could be merged by searching in 'CODICE_SIF'
metatest = dw.mergemeta(metaDBU, meta, firstmerge = dict(),
                        secondmerge = dict(left_on = 'CODICE_SIF', right_index = True,
                                           suffixes = ['_DBU', '_Milano1950']))
#All the points associated directly throuhg CODICE_SIF had already been
#associated before

metamerge.insert(26, 'z_Milano1950', metamerge['RIFERIMENTO'])
metamerge.insert(3, 'CODICE_FOG', metamerge['PIEZOMETRO'])
todrop = ['RIFERIMENTO', 'Coord_X', 'Coord_Y', 'PIEZOMETRO']
metamerge.drop(columns = todrop, inplace = True)

#join overlapping columns
dw.join_twocols(metamerge, ['INFO', 'UBICAZIONE'], rename = "INFO", onlyna = False, add = True, inplace = True)
dw.join_twocols(metamerge, ['CODICE_SIF', 'CODICE_Milano1950'], inplace = True)
dw.join_twocols(metamerge, ['ORIGINE_DBU', 'ORIGINE_Milano1950'], rename = 'ORIGINE', onlyna = False, add = True, inplace = True)
metamerge = dw.joincolumns(metamerge, '_DBU', '_Milano1950')

metamerge.to_csv('data/results/db-unification/meta_DBU-5_firstmerge.csv')

# %% Merge the time series

headDBU = pd.read_csv('data/results/db-unification/head_DBU-4.csv', index_col = 'DATA')
headDBU.index = pd.DatetimeIndex(headDBU.index)

codelst = codelst.loc[codelst.isin(metamerge.index).values, :]
idx = metamerge['BACINO_WISE'] == 'IT03GWBISSAPTA'
codelst = codelst.loc[codelst['CODICE_link'].isin(metamerge.loc[idx, :].index), :]

codelst.reset_index(drop = False, inplace = True)
codelst.set_index('CODICE_link', inplace = True)
codelst = codelst.squeeze()
sum(codelst.index.isin(headDBU.columns))
headmerge = dw.mergets(headDBU, head, codelst)
sum(codelst.index.isin(headmerge.columns))

#Visualize the result
vis = head[codelst]
vismerge = headmerge[codelst.index]
lab = codelst[codelst.index.isin(headDBU.columns).tolist()].index
visdbu = headDBU[lab]
dv.interactive_TS_visualization(vismerge, file = 'plot/dbu/added_ts_DBU-5_firstmerge.html',
                                title_text = 'Merged time series in DBU-5 (between Milano1950 and DBU-4)')
dv.interactive_TS_visualization(visdbu, file = 'plot/dbu/added_ts_DBU-5_originalTS.html',
                                title_text = 'Original time series in DBU-4 which got then merged')

# %% Identify the groundwater basin of the Milano1950 metadata not merged

#visualize all series not merged in head, to decide which ones not to keep
notmrg = head.loc[:, np.invert(head.columns.isin(codelst))].copy()
dv.interactive_TS_visualization(notmrg, file = 'plot/dbu/added_ts_DBU-5_notmerged.html',
                                 title_text = 'Time series from Milano1950 not merged in first merge')
remove = ['SIF_NA']
notmrg.drop(columns = remove, inplace = True)

#visualize the points left out on a map together with the dbu points
meta_ntmrg = meta.loc[meta.index.isin(notmrg.columns), : ].copy()
meta_ntmrg.reset_index(inplace = True)
meta_ntmrg.drop(columns = ['UBICAZIONE', 'PIEZOMETRO', 'Coord_X', 'Coord_Y', 'RIFERIMENTO', 'COMUNE'], inplace = True)
dbu_show = metaDBU.copy()
dbu_show.reset_index(inplace = True)
drop = dbu_show.columns[np.invert(dbu_show.columns.isin(meta_ntmrg.columns))]
dbu_show.drop(columns = drop, inplace = True)
dbu_show.loc[dbu_show['ORIGINE'].isna(), 'ORIGINE'] = 'DBU'
points = pd.concat([dbu_show, meta_ntmrg])
gd.show_mappoints(points, 'lat', 'lon', color = 'ORIGINE', hover_name = 'CODICE')

#export the points left out as a csv, to then search for the basin code on QGIS
meta_ntmrg.to_csv('database_unification/DBU-5_leftout.csv', index = False)
#join on QGIS
#import the joined df
points = pd.read_csv('database_unification/DBU-5_leftout_joinQGIS.csv')
points.drop(columns = points.columns[np.invert(points.columns.isin(['CODICE', 'COD_PTUA16']))], inplace = True)
points['CODICE'] = [f"0{int(idx)}" if not np.isnan(idx) else np.nan for idx in points['CODICE']]

#create a new df with the informations of points left out, then join with the basin code found
to_insert = meta.loc[meta.index.isin(notmrg.columns), : ].copy()
to_insert = to_insert.loc[np.invert(to_insert.index.isin(metamerge['CODICE_SIF'])), :]
to_insert = pd.merge(to_insert, points, how = 'inner', left_index = True, right_on = 'CODICE')

#merge to_insert with metamerge
to_insert.reset_index(drop = True, inplace = True)
to_insert['Coord_X'], to_insert['Coord_Y'] = gd.transf_CRS(to_insert.loc[:, 'Coord_X'], to_insert.loc[:, 'Coord_Y'], 'EPSG:3003', 'EPSG:32632', series = True)
to_insert.rename(columns = {'COD_PTUA16': 'BACINO_WISE',
                            'CODICE': 'CODICE_SIF',
                            'PIEZOMETRO': 'CODICE',
                            'Coord_X': 'X_WGS84',
                            'Coord_Y': 'Y_WGS84',
                            'UBICAZIONE': 'INFO',
                            'RIFERIMENTO': 'QUOTA_MISU'}, inplace = True)
to_insert['PROVINCIA'] = 'MI'
to_insert['CODICE_FOG'] = to_insert['CODICE']

# to_merge = metamerge.reset_index().copy()
metamerge = pd.merge(metamerge, to_insert, how = 'outer', left_index = True, right_on = 'CODICE')
metamerge = dw.joincolumns(metamerge)
metamerge.set_index('CODICE', inplace = True)

metamerge.to_csv('data/results/db-unification/meta_DBU-5.csv')
