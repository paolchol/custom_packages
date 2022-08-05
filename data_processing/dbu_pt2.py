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

# %% Load the metadata

#Metadata dei dati usati nel PTUA 2022
meta = pd.read_csv('data/PTUA2022/metadata_piezometri_ISS.csv', index_col = 'CODICE')

#Metadata dei dati usati nel PTUA 2003
metaold = pd.read_csv('data/PTUA2003/meta_PTUA2003_TICINOADDA.csv', index_col = 'CODICE')

#Database incrociato: contiene associazione tra codici SIF e PP
code_db = pd.read_csv('data/general/code_db_SIF_PP.csv')

# %% Analisi sui codici

#Codici PTUA2003 presenti nel database incrociato
old1 = metaold.loc[metaold.index.isin(code_db['CODICE_SIF']), :]
old2 = metaold.loc[metaold.index.isin(code_db['CODICE_PP']), :]
#Codici PTUA2003 presenti nel database PTUA2022
old3 = metaold.loc[metaold.index.isin(meta.index), :]

#Codici PP di old1 presenti nel database PTUA 2022
pp = code_db.loc[code_db['CODICE_SIF'].isin(old1.index), 'CODICE_PP']
vis = meta.loc[meta.index.isin(pp), :]
#le serie storiche dei piezometri in vis possono essere associate direttamente

# %% Associazione di metadata e serie storiche dei piezometri identificati

#Associazione codice PP a metadata PTUA2003, usando codice SIF
idx = metaold.index.isin(code_db['CODICE_SIF'])
sifpp = code_db.loc[code_db['CODICE_SIF'].isin(metaold.index), ['CODICE_SIF', 'CODICE_PP']]
sifpp.set_index('CODICE_SIF', inplace = True)
metaold_j = pd.merge(metaold, sifpp, how = 'left', left_index = True, right_index = True)
metaold_j.reset_index(inplace = True)
metaold_j.rename(columns = {'CODICE': 'CODICE_SIF'}, inplace = True)
metaold_j.set_index('CODICE_PP', inplace = True)
#Associazione metadata PTUA2003 a metadata PTUA2022, usando codice PP
metamerged = pd.merge(meta, metaold_j['CODICE_SIF'], how = 'left', left_index = True, right_index = True)
metamerged.index.names = ['CODICE']
#Aggiunta della serie storica PTUA2003 alla serie storica PTUA2022 per i piezometri
# individuati con doppio codice
head2022 = pd.read_csv('data/PTUA2022/head_IT03GWBISSAPTA.csv', index_col='DATA')
head2003 = pd.read_csv('data/PTUA2003/head_PTUA2003_TICINOADDA.csv', index_col='DATA')
head2022.index = pd.DatetimeIndex(head2022.index)
head2003.index = pd.DatetimeIndex(head2003.index)

codes = metamerged.loc[metamerged['BACINO_WISE'] == 'IT03GWBISSAPTA', 'CODICE_SIF'].dropna()
headmerge = dw.mergehead(head2022, head2003, codes)

dv.interactive_TS_visualization(headmerge, 'data', 'livello [m.s.l.m]', file = 'plot/dbu/merged_0805_TS_IT03GWBISSAPTA.html')
# %% Find the nearest piezometer of meta to the piezometers of metaold

#Check: "validare" usando i piezometri per cui si sanno già i doppi codici
#modificare da.find_nearest_point()
#Escludere piezometri che in metaold hanno FALDA come "profonda" e capire a cosa
#corrispondono i numeri

# %% Altre operazioni

#Visualizzazione dei piezometri associabili direttamente ai dati PTUA2022
import numpy as np
extr = metamerged.loc[np.invert(metamerged['CODICE_SIF'].isna()), :]
extr.to_csv('trash/export/piezo_accoppiati.csv')
