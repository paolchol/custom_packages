# -*- coding: utf-8 -*-
"""
dbu: DataBase Unification
Unificazione del dataset utilizzato per il PTUA 2003 con il dataset
reso disponibile da ARPA per il PTUA 2022
pt2: Parte 2
Associazione dei piezometri del PTUA2003 a quelli disponibili al PTUA 2022

@author: paolo
"""

# %% Setup

import pandas as pd
import dataviz as dv
import datawrangling as dw
import geodata as gd

# %% Load the metadata

#Metadata dei dati usati nel PTUA 2022
meta2022 = pd.read_csv('data/PTUA2022/metadata_piezometri_ISS.csv', index_col = 'CODICE')

#Metadata dei dati usati nel PTUA 2003
meta2003 = pd.read_csv('data/PTUA2003/meta_sup_PTUA2003_TICINOADDA.csv', index_col = 'CODICE')

#Database incrociato: contiene associazione tra codici SIF e PP
code_db = pd.read_csv('data/general/codes_SIF_PP.csv')

# %% Associazione di metadata e serie storiche dei piezometri identificati

#Associazione codice PP a metadata PTUA2003, usando codice SIF
idx = meta2003.index.isin(code_db['CODICE_SIF'])
sifpp = code_db.loc[code_db['CODICE_SIF'].isin(meta2003.index), ['CODICE_SIF', 'CODICE_PP']]
sifpp.set_index('CODICE_SIF', inplace = True)
meta2003_j = pd.merge(meta2003, sifpp, how = 'left', left_index = True, right_index = True)
meta2003_j.reset_index(inplace = True)
meta2003_j.rename(columns = {'CODICE': 'CODICE_SIF'}, inplace = True)
meta2003_j.set_index('CODICE_PP', inplace = True)
#Associazione metadata PTUA2003 a metadata PTUA2022, usando codice PP
metamerged = pd.merge(meta2022, meta2003_j['CODICE_SIF'], how = 'left', left_index = True, right_index = True)
metamerged.index.names = ['CODICE']
#Aggiunta della serie storica PTUA2003 alla serie storica PTUA2022 per i piezometri
# individuati con doppio codice
head2022 = pd.read_csv('data/PTUA2022/head_IT03GWBISSAPTA.csv', index_col='DATA')
head2003 = pd.read_csv('data/PTUA2003/head_PTUA2003_TICINOADDA.csv', index_col='DATA')
head2022.index = pd.DatetimeIndex(head2022.index)
head2003.index = pd.DatetimeIndex(head2003.index)

codes = metamerged.loc[metamerged['BACINO_WISE'] == 'IT03GWBISSAPTA', 'CODICE_SIF'].dropna()
headmerge = dw.mergehead(head2022, head2003, codes)

# dv.interactive_TS_visualization(headmerge, 'data', 'livello [m.s.l.m]', file = 'plot/dbu/merged_0805_TS_IT03GWBISSAPTA.html')

sum(meta2003.index.isin(code_db['CODICE_SIF']))
sum(meta2003.index.isin(code_db['CODICE_PP']))

idx = meta2003.index.isin(code_db['CODICE_SIF'])
sifpp = code_db.loc[code_db['CODICE_SIF'].isin(meta2003.index), ['CODICE_SIF', 'CODICE_PP']]
sifpp.set_index('CODICE_SIF', inplace = True)

test = dw.mergemeta(meta2022, meta2003, link = sifpp,
                    firstmerge = dict(left_index = True, right_index = True),
                    secondmerge = dict(left_index = True, right_on = 'CODICE_PP',
                                       suffixes = [None, "_PTUA2003"]))
test.rename(columns = {'CODICE_PP': 'CODICE', 'index': 'CODICE_SIF'}, inplace = True)
#mettere codice come index
test.drop(columns = ['SETTORE', 'STRAT.', 'PROVINCIA_PTUA2003', 'x', 'y', 'COMUNE_PTUA2003'], inplace = True)
#riordinare le colonne

# %% Find the nearest piezometer of meta to the piezometers of meta2003

meta2003 = meta2003[(meta2003['x'].notna()) & (meta2003['y'].notna())].copy()
out = gd.transf_CRS(meta2003.loc[:, 'x'], meta2003.loc[:, 'y'], 'EPSG:3003', 'EPSG:4326', series = True)
meta2003['lat'], meta2003['lon'] = out[0], out[1]

meta2022 = meta2022[(meta2022['X_WGS84'].notna()) & (meta2022['Y_WGS84'].notna())].copy()
out = gd.transf_CRS(meta2022.loc[:, 'X_WGS84'], meta2022.loc[:, 'Y_WGS84'], 'EPSG:32632', 'EPSG:4326', series = True)
meta2022['lat'], meta2022['lon'] = out[0], out[1]

db_nrst = gd.find_nearestpoint(meta2003, meta2022,
                     id1 = 'CODICE', coord1 = ['lon', 'lat'],
                     id2 = 'CODICE', coord2 = ['lon', 'lat'],
                     reset_index = True)

idx = db_nrst.loc[db_nrst['dist'] < 100, 'CODICE']
vis = meta2003.loc[idx, :]
vis['dist'] = db_nrst.loc[db_nrst['CODICE'].isin(idx), 'dist'].values

# %% Validate the results

#Check: "validare" usando i piezometri per cui si sanno già i doppi codici

#Escludere piezometri che in meta2003 hanno FALDA come "profonda" e capire a cosa
#corrispondono i numeri



# %% Altre operazioni

#Visualizzazione dei piezometri associabili direttamente ai dati PTUA2022
import numpy as np
extr = metamerged.loc[np.invert(metamerged['CODICE_SIF'].isna()), :]
extr.to_csv('trash/export/piezo_accoppiati.csv')
