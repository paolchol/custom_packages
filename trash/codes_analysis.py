# -*- coding: utf-8 -*-
"""
Piezometers and wells codes analysis

@author: paolo
"""

import pandas as pd

# %% Load the metadata

#Metadata dei dati usati nel PTUA 2022
meta2022 = pd.read_csv('data/PTUA2022/metadata_piezometri_ISS.csv', index_col = 'CODICE')

#Metadata dei dati usati nel PTUA 2003
meta2003 = pd.read_csv('data/PTUA2003/meta_sup_PTUA2003_TICINOADDA.csv', index_col = 'CODICE')

#Database incrociato: contiene associazione tra codici SIF e PP
code_db = pd.read_csv('data/general/codes_SIF_PP.csv')

# %% Analisi sui codici

#Codici PTUA2003 presenti nel database incrociato
old1 = meta2003.loc[meta2003.index.isin(code_db['CODICE_SIF']), :]
old2 = meta2003.loc[meta2003.index.isin(code_db['CODICE_PP']), :]
#Codici PTUA2003 presenti nel database PTUA2022
old3 = meta2003.loc[meta2003.index.isin(meta2022['CODICE']), :]

#Codici PP di old1 presenti nel database PTUA 2022
pp = code_db.loc[code_db['CODICE_SIF'].isin(old1.index), 'CODICE_PP']
linked = meta2022.loc[meta2022.index.isin(pp), :]
#le serie storiche dei piezometri in linked possono essere associate direttamente

# %% Merge di meta, metodo vecchio

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
