# -*- coding: utf-8 -*-
"""
DBU-2 construction

- Load Soggiacenza_CAP.xls
- Structure the dataase in a meta and head files
- Identify the codes couples between DBU-1 and the obtained metaCAP
- Visualize the coupled piezometers on plotly
- Create DBU-2

@author: paolo
"""

#%% Setup

import pandas as pd
import numpy as np
import datawrangling as dw

# %% Load

original = pd.read_csv('data/CAP/Soggiacenza_CAP.csv')

#split in metadata and data databases
cols = original.columns.to_list()
months = [cols[11]] + cols[14:]
metacols = cols[0:2] + cols[3:11] + cols[12:14]
datacols = ['sif', 'ANNO'] + months
meta = original[metacols].copy()
data = original[datacols].copy()

#meta db arrangment
meta.drop_duplicates('sif', 'last', inplace = True) #last: to maintain the informations in "INDIRIZZO_" and "INDIRIZZO"
meta.drop(columns = ['ID1', 'codice', 'N_POZZO', 'N_POZZO_TX', 'ORIGINE_DA', 'INDIRIZZO_'], inplace = True)
meta.set_index('sif', inplace = True)

#data db arrangment
data[data == 0] = np.nan
data.set_index('sif', inplace = True)
d = {month: index for index, month in enumerate(months, start = 1) if month}


#metti lo zero davanti a data.index!


from datawrangling import stackedDF
f = stackedDF(data, 'ANNO', d)
s = f.rearrange()
