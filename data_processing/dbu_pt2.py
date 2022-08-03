# -*- coding: utf-8 -*-
"""
dbu: DataBase Unification
Unificazione del dataset utilizzato per il PTUA 2003 con il dataset
reso disponibile da ARPA per il PTUA 2022
pt2 Parte 2
Associazione dei piezometri del PTUA2003 a quelli disponibili al PTUA 2022

@author: paolo
"""

# %% Setup

import pandas as pd

# %% Load the metadata

#Metadata dei dati usati nel PTUA 2022
meta = pd.read_csv('data/PTUA2022/metadata_piezometri_ISS.csv', index_col = 'CODICE')

#Metadata dei dati usati nel PTUA 2003
metaold = pd.read_csv('data/PTUA2003/meta_PTUA2003_TICINOADDA.csv', index_col = 'CODICE')
#Il codice SIF ha uno zero davanti
#Aggiungere 0 ai codici in metaold più lunghi di 6 caratteri
metaold.index = [f'0{code}' if len(code)>6 else code for code in metaold.index]

#Database incrociato: contiene associazione tra codici SIF e PP
codes = pd.read_csv('data/general/codes_SIF_PP.csv')

# %% Analisi sui codici

#Codici PTUA2003 presenti nel database incrociato
old1 = metaold.loc[metaold.index.isin(codes['CODICE_SIF']), :]
old2 = metaold.loc[metaold.index.isin(codes['CODICE_PP']), :]
#Codici PTUA2003 presenti nel database PTUA2022
old3 = metaold.loc[metaold.index.isin(meta.index), :]

#Codici PP di old1 presenti nel database PTUA 2022
pp = codes.loc[codes['CODICE_SIF'].isin(old1.index), 'CODICE_PP']
vis = meta.loc[meta.index.isin(pp), :]
#le serie storiche dei piezometri in vis possono essere associate direttamente

# %% Associazione di metadata e serie storiche dei piezometri identificati

#Associazione codice PP a metadata PTUA2003, usando codice SIF
idx = metaold.index.isin(codes['CODICE_SIF'])
sifpp = codes.loc[codes['CODICE_SIF'].isin(metaold.index), ['CODICE_SIF', 'CODICE_PP']]
sifpp.set_index('CODICE_SIF', inplace = True)
metaold_j = pd.merge(metaold, sifpp, how = 'left', left_index = True, right_index = True)
metaold_j.reset_index(level = 'CODICE_SIF', inplace = True)
metaold_j.set_index('CODICE_PP', inplace = True)

merged = pd.merge(meta, metaold_j, how = 'left', left_index = True, right_index = True)
#Associazione metadata PTUA2003 a metadata PTUA2022, usando codice PP


# %% Find the nearest piezometer of meta to the piezometers of metaold

