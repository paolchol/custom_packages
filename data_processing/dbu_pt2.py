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

meta = pd.read_csv('data/metadata_piezometri_ISS.csv', index_col = 'CODICE')
metaold = pd.read_csv('data/ol')