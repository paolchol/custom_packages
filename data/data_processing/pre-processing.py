# -*- coding: utf-8 -*-
"""
Created on Thu Jul 14 16:20:58 2022

@author: paolo
"""

# %% Setup

import pandas as pd
import numpy as np
import dataanalysis as da
import dataviz as dv

# %% Load data and metadata

head = pd.read_csv('data/head_IT03GWBISSAPTA.csv', index_col = 'DATA')
meta = pd.read_csv('data/metadata_piezometri_ISS.csv')

# %% Check for outliers

co = da.CheckOutliers(head)
co.plot()
checkdb = co.output

# %% Check missing data

cn = da.CheckNA(head)
cn.check()
checkdb = cn.output

#Visualize single time series
import matplotlib as plt
plt.pyplot.plot(head[checkdb['ID'][48]])

# %% Handle missing data

#Select time series with less than 50% of missing data on the whole
#time series
filtered, removed = cn.filter_col(50)
#Select time series with less than 20% of missing data from each TS starting
#date
filtered2, removed2 = cn.filter_col(20, True)

dv.interactive_TS_visualization(filtered2, xlab = 'Data', ylab = 'Codice piezometro',
                                file = 'plot/dp/filtered2.html')
dv.interactive_TS_visualization(filtered, xlab = 'Data', ylab = 'Codice piezometro',
                                file = 'plot/dp/filtered.html')

#Check the time series which are not in both the selections
notinfiltered = filtered2.columns[np.invert(pd.Series(filtered2.columns).isin(filtered.columns.values))]
for code in notinfiltered:
    if code in meta['CODICE']:
        da.print_row(meta, meta['CODICE'].values == code)

#Fill missing data: Trials on filtered2

#Linear interpolation
fill_ln = filtered2.interpolate('linear', limit = 12)
dv.interactive_TS_visualization(fill_ln, xlab = 'Data', ylab = 'Codice piezometro',
                                file = 'plot/dp/fill_ln.html')
#From derivatives
fill_dv = filtered2.interpolate('from_derivatives')
dv.interactive_TS_visualization(fill_dv, xlab = 'Data', ylab = 'Codice piezometro',
                                file = 'plot/dp/fill_dv.html')
#12 months moving average
fill_ma = filtered2.fillna(filtered2.rolling(12, 1).mean())
dv.interactive_TS_visualization(fill_ma, xlab = 'Data', ylab = 'Codice piezometro',
                                file = 'plot/dp/fill_ma_12.html')
#6 months moving average + linear interpolation
fill_maln = filtered2.fillna(filtered2.rolling(6, 1).mean()).interpolate('linear', limit = 6)
dv.interactive_TS_visualization(fill_maln, xlab = 'Data', ylab = 'Codice piezometro',
                                file = 'plot/dp/fill_maln.html')

# %% Other checks

#Check if the reference quotas of the piezometer changed in time
#Manual check on the metadata
pqr = head.pivot(index = 'DATA', columns = 'CODICE PUNTO', values = 'Qr [m s.l.m.]')
pqr = pqr.resample('1Y').mean()
for col in pqr.columns:
    print(pqr[col].value_counts())

#Automatic check with discontinuity detection
#To be implemented