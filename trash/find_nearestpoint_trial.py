# -*- coding: utf-8 -*-

import datawrangling as dw
import geodata as gd
import numpy as np
import pandas as pd
import time

meta2022 = pd.read_csv('data/PTUA2022/metadata_piezometri_ISS.csv', index_col = 'CODICE')
meta2003 = pd.read_csv('data/PTUA2003/meta_sup_PTUA2003_TICINOADDA.csv', index_col = 'CODICE')
#meta2022 e meta2003 sono in due sistemi di coordinate differenti
#meta2022: UTM Z32N - EPSG:32632
#meta2003: Monte Mario / Italy zone 1 - EPSG:3003

meta2003 = meta2003[(meta2003['x'].notna()) & (meta2003['y'].notna())].copy()
out = gd.transf_CRS(meta2003.loc[:, 'x'], meta2003.loc[:, 'y'], 'EPSG:3003', 'EPSG:4326', series = True)
meta2003['lat'], meta2003['lon'] = out[0], out[1]

meta2022 = meta2022[(meta2022['X_WGS84'].notna()) & (meta2022['Y_WGS84'].notna())].copy()
out = gd.transf_CRS(meta2022.loc[:, 'X_WGS84'], meta2022.loc[:, 'Y_WGS84'], 'EPSG:32632', 'EPSG:4326', series = True)
meta2022['lat'], meta2022['lon'] = out[0], out[1]

start = time.time()
db_nrst = gd.find_nearestpoint(meta2003, meta2022,
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

exp = db_nrst[db_nrst['dist'] < 500]
exp.to_csv('./trash/points_500dist.csv', index = False)

#Funziona molto bene!
#Le distanze sono calcolate perfettamente (controllo effettuato su Earth e QGIS)

# %% Validate the spatial analysis results
idx = db_nrst.loc[db_nrst['dist'] < 100, 'CODICE']
vis = meta2003.loc[idx, :]
vis['dist'] = db_nrst.loc[db_nrst['CODICE'].isin(idx), 'dist'].values


#Check: "validare" l procedura spaziale usando i piezometri per cui si sanno già i doppi codici

#Escludere piezometri che in meta2003 hanno FALDA come "profonda" e capire a cosa
#corrispondono i numeri