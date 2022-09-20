# -*- coding: utf-8 -*-

import datawrangling as dw
import geodata as gd
import numpy as np
import pandas as pd



meta = pd.read_csv('data/PTUA2022/metadata_piezometri_ISS.csv', index_col = 'CODICE')
metaold = pd.read_csv('data/PTUA2003/meta_PTUA2003_TICINOADDA.csv', index_col = 'CODICE')
#meta e metaold sono in due sistemi di coordinate differenti
#meta: UTM Z32N - EPSG:32632
#metaold: Monte Mario / Italy zone 1 - EPSG:3003

metaold = metaold[(metaold['x'].notna()) & (metaold['y'].notna())].copy()
out = gd.transf_CRS(metaold.loc[:, 'x'], metaold.loc[:, 'y'], 'EPSG:3003', 'EPSG:4326', series = True)
metaold['lat'], metaold['lon'] = out[0], out[1]

meta = meta[(meta['X_WGS84'].notna()) & (meta['Y_WGS84'].notna())].copy()
out = gd.transf_CRS(meta.loc[:, 'X_WGS84'], meta.loc[:, 'Y_WGS84'], 'EPSG:32632', 'EPSG:4326', series = True)
meta['lat'], meta['lon'] = out[0], out[1]

import time

start = time.time()
db_nrst = gd.find_nearestpoint(metaold, meta,
                     id1 = 'CODICE', coord1 = ['lon', 'lat'],
                     id2 = 'CODICE', coord2 = ['lon', 'lat'],
                     reset_index = True)
end = time.time()
print(f'Find nearest point running time: {round(end-start, 2)} s')
#2.27 s with 267 points vs 200 points

#Keep only points with distance < 100 m
sum(db_nrst['dist'] < 100) #33 points linkable
#export them as csv and visualize them on QGIS
exp = db_nrst[db_nrst['dist'] < 100]
exp.to_csv('./trash/points_100dist.csv', index = False)

#Funziona molto bene!
