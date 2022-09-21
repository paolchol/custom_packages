# -*- coding: utf-8 -*-
"""
Possible operations on meta and head datasets
"""

import numpy as np
import pandas as pd

meta = pd.read_csv('data/PTUA2003/meta_PTUA2003_TICINOADDA_unfiltered.csv', index_col = 'CODICE')
head = pd.read_csv('data/PTUA2003/head_PTUA2003_TICINOADDA_unfiltered.csv', index_col = 'DATA')

# %% Dataset modifications

#Senza modificare meta
#Rimozione piezometri senza coordinate
idx = np.invert(meta.loc[:, ['x', 'y']].isna().apply(all, 1))
head = head[[col for col in meta.loc[idx, :].index if (col in head.columns)]]
#Rimozione piezometri senza quota
idx = np.invert(meta.loc[:, 'z'].isna())
head = head[[col for col in meta.loc[idx, :].index if (col in head.columns)]]
