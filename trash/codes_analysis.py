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
