# -*- coding: utf-8 -*-
"""
Possible operations on meta and head datasets
"""

import numpy as np
import pandas as pd

meta = pd.read_csv('data/PTUA2003/meta_PTUA2003_TICINOADDA_unfiltered.csv', index_col = 'CODICE')
head = pd.read_csv('data/PTUA2003/head_PTUA2003_TICINOADDA_unfiltered.csv', index_col = 'DATA')

# %% Dataset modifications

#Rimozione piezometri senza coordinate
idx = meta.loc[:, ['x', 'y']].isna().apply(all, 1)
meta = meta.drop(meta.index[idx])
head = head.loc[:, head.columns.isin(meta.index)]
#Rimozione piezometri senza quota
idx = meta.loc[:, 'z'].isna()
meta = meta.drop(meta.index[idx])
head = head.loc[:, ts.columns.isin(meta.index)]

#Senza modificare meta
#Rimozione piezometri senza coordinate

# meta2003 = meta2003[sum(meta2003['x'].isna()) & (meta2003['y'].notna())].copy()

idx = np.invert(meta.loc[:, ['x', 'y']].isna().apply(all, 1))
head = head[[col for col in meta.loc[idx, :].index if (col in head.columns)]]
#Rimozione piezometri senza quota
idx = np.invert(meta.loc[:, 'z'].isna())
head = head[[col for col in meta.loc[idx, :].index if (col in head.columns)]]

#Separazione dei metadati in falda superficiale e profonda
meta_sup = meta.loc[meta['FALDA'].isin(['1', np.nan, 'SUPERF.', 'SUPERF. (acquifero locale)']), :]
meta_otr = meta.loc[np.invert(meta.index.isin(meta_sup.index)), :]

meta_sup.to_csv('data/PTUA2003/meta_sup_PTUA2003_TICINOADDA.csv')
meta_otr.to_csv('data/PTUA2003/meta_other_PTUA2003_TICINOADDA.csv')

# %% Altre operazioni

#Visualizzazione dei piezometri associabili direttamente ai dati PTUA2022
import numpy as np
extr = metamerged.loc[np.invert(metamerged['CODICE_SIF'].isna()), :]
extr.to_csv('trash/export/piezo_accoppiati.csv')
