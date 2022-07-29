# -*- coding: utf-8 -*-
"""
Created on Wed Jul 27 12:48:47 2022

@author: paolo
"""

import numpy as np
import pandas as pd
import skgstat as skg
from skgstat import OrdinaryKriging
import matplotlib.pyplot as plt

data = pd.read_csv('spatialization/trials/sample_lr.txt')

V = skg.Variogram(data[['x', 'y']].values, data.z.values, maxlag=90, n_lags=25,
                  model='gaussian', normalize=False)

V.plot()

ok = OrdinaryKriging(V, min_points=5, max_points=20, mode='exact')

xx, yy = np.mgrid[0:99:100j, 0:99:100j]
field = ok.transform(xx.flatten(), yy.flatten()).reshape(xx.shape)
s2 = ok.sigma.reshape(xx.shape)



fig, ax = plt.subplots(figsize = (6.4, 3.6), dpi = 500)
ax.imshow(field)

# %% my data

head = pd.read_csv('data/head_IT03GWBISSAPTA.csv', index_col = 'DATA')
meta = pd.read_csv('data/metadata_piezometri_ISS.csv', index_col = 'CODICE')
import dataanalysis as da
co = da.CheckOutliers(head, False)
head_fill = co.remove(skip = ['PO0120750R2020']).interpolate('linear', limit = 14)

trial = pd.DataFrame(head_fill.loc['2011-01-01', head_fill.columns.isin(meta.index)])
trial['x'] = meta.loc[trial.index, 'X_WGS84'].values
trial['y'] = meta.loc[trial.index, 'Y_WGS84'].values
trial.dropna(inplace=True)
trial.rename(columns = {'2011-01-01': 'z'}, inplace = True)

V2 = skg.Variogram(trial[['x', 'y']].values, trial.z.values)
V2.plot()

#mettere gli estremi dell'area
xx, yy = np.mgrid[0:99:100j, 0:99:100j]
field = ok.transform(xx.flatten(), yy.flatten()).reshape(xx.shape)
s2 = ok.sigma.reshape(xx.shape)

fig, ax = plt.subplots(figsize = (6.4, 3.6), dpi = 500)
ax.imshow(field)