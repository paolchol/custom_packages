# -*- coding: utf-8 -*-
"""
Created on Tue Jul 26 13:28:49 2022

@author: paolo
"""

# %% Setup

import pandas as pd
import numpy as np
import dataanalysis as da
import dataviz as dv
import matplotlib.pyplot as plt
from class_SSA import SSA

# %% Load data and metadata

head = pd.read_csv('data/head_IT03GWBISSAPTA.csv', index_col = 'DATA')
meta = pd.read_csv('data/metadata_piezometri_ISS.csv')

# %% Select solid time series, remove outliers and fill missing values

cn = da.CheckNA(head)
filtered, removed = cn.filter_col(20, True)
co = da.CheckOutliers(filtered, False)
head_clean = co.remove(skip = ['PO0120750R2020'])
head_fill = head_clean.interpolate('linear', limit = 14)
#Select only time series with more than 20 years of observation
fvi = pd.DataFrame(head_fill.apply(pd.Series.first_valid_index, axis = 0), columns =  ['start'])
fvi['years'] = pd.to_datetime('2021-12-31') - pd.to_datetime(fvi['start'])
fvi['years'] = [fvi.loc[:, 'years'][i].days/365 for i in range(len(fvi.index))]
head_sel = head_fill[fvi.index[fvi['years'] >= 20]]

# %% Perform the SSA over the time series

import pickle as pkl
import time

start = time.time()
# min([len(head_sel[col].dropna())/2 for col in head_sel.columns])
L = 116 #Window length
dSSA = {}
for col in head_sel.columns:
    dSSA[f"{col}"] = SSA(head_sel[col].dropna(), L)
end = time.time()
print(f'SSA class creation for all the stations \tElapsed time: {round(end - start)} seconds\t{round((end - start)/60)} minutes')

dv.interactive_TS_visualization(head_sel, file = 'plot/analisi/selection_for_SSA.html')

#Save the result
# pkl.dump(dSSA, open('analisi_serie_storiche/SSA_components.p', 'wb'))

#Area without irrigation
#MERATE
col = meta.loc[meta['COMUNE'] == 'MERATE', 'CODICE'].values[0]
L = 116
dv.plot_Wcorr_Wzomm(dSSA[col], col, L)
dv.plot_Wcorr_Wzomm(dSSA[col], col, L, 49)
dv.plot_Wcorr_Wzomm(dSSA[col], col, L, 9)
## Group the first 10 elementary components
F0 = [0]
F1 = [1]
F2 = [2, 3]
F3 = [4]
F4 = [5, 6]
F5 = [7]
F6 = [8, 9]
Fs = [F0, F1, F2, F3, F4, F5, F6]

dv.plot_SSA_results(dSSA[col], Fs, file = f'plot/analisi/SSA/Exploration_SSA_{col}_L{L}.html',
                    title = f'Exploration - {col}', over = [f'F{i}' for i in range(1, 7)],
                    alpha = 0.7)
#Final plot
Fs = [F0, F1, F2]
dv.plot_SSA_results(dSSA[col], Fs, file = f'plot/analisi/SSA/SSA_{col}_L{L}.html',
                    title = f"{col} - {meta.loc[meta['CODICE'] == col, 'COMUNE'].values[0]}",
                    over = ['Periodicità pluri-annuale', 'Periodicità semestrale'],
                    alpha = 0.7, tags = ['Trend', 'Periodicità pluri-annuale', 'Periodicità semestrale'],
                    xaxis_title = 'Data', yaxis_title = 'Livello piezometrico [m.s.l.m]')

# Fs_sel = [F0, F1, F2]
# Noise = slice(4, L)
# dv.plot_SSA_results(dSSA[col], Fs_sel, noise = Noise, label = f'{col} - Decomposed',
#                  file = f'plot/analisi/SSA/SSA_{col}_L{L}.html', final = True)

#Area with irrigation
#BUSTO GAROLFO
col = meta.loc[meta['COMUNE'] == 'BUSTO GAROLFO', 'CODICE'].values[0]
L = 42
ssa = SSA(head_fill[col].dropna(), L)
dv.plot_Wcorr_Wzomm(ssa, col, L)
dv.plot_Wcorr_Wzomm(ssa, col, L, 49)
dv.plot_Wcorr_Wzomm(ssa, col, L, 9)
## Group the first 10 elementary components
F0 = [0]
F1 = [1, 2]
F2 = [3, 4]
Fs = [F0, F1, F2]

dv.plot_SSA_results(ssa, Fs, file = f'plot/analisi/SSA/SSA_{col}_L{L}.html',
                    title = f"{col} - {meta.loc[meta['CODICE'] == col, 'COMUNE'].values[0]}",
                    over = ['Periodicità annuale', 'Periodicità semestrale'],
                    alpha = 0.7, tags = ['Trend', 'Periodicità annuale', 'Periodicità semestrale'],
                    xaxis_title = 'Data', yaxis_title = 'Livello piezometrico [m.s.l.m]')

# %% other operations
#export points for QGIS
tags = meta.loc[meta['CODICE'].isin(head_fill.columns), ['CODICE', 'COMUNE', 'X_WGS84', 'Y_WGS84']]
tags.to_csv('head_fill_SSA.csv')
