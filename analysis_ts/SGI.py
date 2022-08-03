# -*- coding: utf-8 -*-
"""
SGI computation on the basin's head time series

@author: paolo
"""

# %% Setup

import pastas as ps
import pandas as pd
import numpy as np
import dataanalysis as da
import dataviz as dv
import matplotlib.pyplot as plt

# %% Load data and metadata

head = pd.read_csv('data/PTUA2022/head_IT03GWBISSAPTA.csv', index_col = 'DATA')
meta = pd.read_csv('data/PTUA2022/metadata_piezometri_ISS.csv')

# %% Select solid time series and fill missing values

cn = da.CheckNA(head)
filtered, removed = cn.filter_col(20, True)
co = da.CheckOutliers(filtered, False)
head_clean = co.remove(skip = ['PO0120750R2020'])
head_fill = head_clean.interpolate('linear', limit = 14)

# %% Compute the SGI for each well/piezometer

head_fill.index = pd.DatetimeIndex(head_fill.index)
sgi_db = head_fill.copy()
for col in head_fill.columns:
    idx = np.invert(head_fill[col].isna())
    sgi_db.loc[idx, col] = ps.stats.sgi(head_fill[col].dropna())

# sgi_db.to_csv('data/results/analysis_ts/res_SGI.csv')

# %% Visualize the SGI

#Single SGI plot
dv.plot_SGI(sgi_db.iloc[:, 4])
#Plot all
for col in sgi_db.columns:
    dv.plot_SGI(sgi_db[col])

#Heatmap visualization of the whole SGI db
col_labels = sgi_db.resample('YS').mean().index.year
fig, ax = plt.subplots(figsize = (6.4, 3.6), dpi = 500)
im, cbar = dv.heatmap_TS(sgi_db.to_numpy().transpose().copy(),
                   row_labels = sgi_db.columns, col_labels = col_labels,
                   step = 12, ax = ax, cbarlabel = "SGI",
                   rotate = True, aspect = 'auto',
                   cmap = plt.get_cmap("coolwarm_r", 8))
fig.tight_layout()
plt.show()

#Order the piezometers from north to south
y = meta.loc[meta['CODICE'].isin(sgi_db.columns), ['CODICE', 'Y_WGS84']]
y.sort_values(by = 'Y_WGS84', ascending = False, inplace = True)
sorter = y['CODICE'].tolist()
col_labels = sgi_db.resample('YS').mean().index.year
fig, ax = plt.subplots(figsize = (6.4, 3.6), dpi = 500)
im, cbar = dv.heatmap_TS(sgi_db[sorter].to_numpy().transpose().copy(),
                   row_labels = sgi_db[sorter].columns, col_labels = col_labels,
                   step = 12, ax = ax, cbarlabel = "SGI",
                   rotate = True, aspect = 'auto',
                   cmap = plt.get_cmap("coolwarm_r", 8))
fig.tight_layout()
plt.show()

#Plot showing the municipality instead of the code
y = meta.loc[meta['CODICE'].isin(sgi_db.columns), ['CODICE', 'Y_WGS84']]
y.sort_values(by = 'Y_WGS84', ascending = False, inplace = True)
sorter = y['CODICE'].tolist()
col_labels = sgi_db.resample('YS').mean().index.year
tags = meta.loc[meta['CODICE'].isin(sgi_db.columns), ['CODICE', 'COMUNE']]
tags.index = tags['CODICE']
fig, ax = plt.subplots(figsize = (6.4, 3.6), dpi = 500)
im, cbar = dv.heatmap_TS(sgi_db[sorter].to_numpy().transpose().copy(),
                   row_labels = tags.loc[sorter, 'COMUNE'], col_labels = col_labels,
                   step = 12, ax = ax, cbarlabel = "SGI",
                   rotate = True, aspect = 'auto',
                   cmap = plt.get_cmap("coolwarm_r", 8))
fig.tight_layout()
plt.show()


# %% Trial: yearly SGI

# Yearly mean of SGI
sgi_y = sgi_db.resample('YS').mean()
#It doesn't really mean anything