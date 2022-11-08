# -*- coding: utf-8 -*-
"""
Created on Tue Jul 19 22:15:31 2022

@author: paolo
"""

import pandas as pd
import matplotlib.pyplot as plt
import dataviz as dv

sgi_db = pd.read_csv('analisi_serie_storiche/SGI_db.csv', index_col = 'DATA')

sgi_db.index = pd.DatetimeIndex(sgi_db.index)

col_labels = sgi_db.resample('YS').mean().index.year

data = sgi_db.to_numpy().transpose().copy()

fig, ax = plt.subplots(figsize = (6.4, 3.6), dpi = 500)

# ax.imshow(sgi_db.transpose(), aspect = 'auto')

im, cbar = dv.heatmap_TS(data,
                   row_labels = sgi_db.columns, col_labels = col_labels,
                   step = 12,
                   ax = ax, cbarlabel = "SGI",
                   rotate = True,
                   aspect = 'auto',
                   cmap=plt.get_cmap("coolwarm_r", 8))

fig.tight_layout()
plt.show()