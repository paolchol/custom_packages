# -*- coding: utf-8 -*-
"""
Starting from the available datasets, construction of 
a database as defined in #link to draw.io

author: paolo
"""

# %% Setup

import pandas as pd

# %% Obtain a monthly dataset of the total head for each piezometer

#Load the basin's piezometer dataset
fname = 'data/IT03GWBISSAPTA.csv'
df = pd.read_csv(fname)
#Set the data format
df['DATA'] = pd.to_datetime(df['DATA'], format = '%d/%m/%Y')
#Define a date/piezometer database
head = df.pivot(index = 'DATA', columns = 'CODICE PUNTO', values = 'PIEZOMETRIA [m s.l.m.]')
#Set the database to monthly
head = head.resample("1MS").mean()

# %% Obtain the piezometer metadata of the GW basin considered 

#Load the full metadata dataset
meta = pd.read_csv('data/metadata_piezometri_ISS.csv')
basin = fname.split('.')[0].split('/')[1]
meta_sel = meta.loc[meta['BACINO_WISE'] == basin, :]

# %% Visualize the time series

import dataviz as dv

D = 5
s, e = 0, 0
for n in range(round(len(head.columns)/D)-1):
    e = s + D if s + D < len(head.columns) else len(head.columns)-1
    dv.fast_TS_visualization(head.iloc[:, s:e])
    print(s, e)
    s = e + 1

dv.interactive_TS_visualization(head, 'date', 'total head')

# %% Check for outliers

import dataanalysis as da

co = da.CheckOutliers(head)
co.plot()
checkdb = co.output

# %% Check missing data

cn = da.CheckNA(head)
cn.check()
checkdb = cn.output

import matplotlib as plt
plt.pyplot.plot(head[checkdb['ID'][48]])

# %% Handle missing data

#Select time series with less than 50% of missing data on the whole
#time series
filtered, removed = cn.filter_col(50)
#Select time series with less than 20% of missing data from each TS starting
#date
filtered2, removed2 = cn.filter_col(20, True)

dv.interactive_TS_visualization(filtered2, xlab = 'Date',
                                ylab = 'Codice piezometro',
                                file = 'plot/filtered2.html')
dv.interactive_TS_visualization(filtered, xlab = 'Date',
                                ylab = 'Codice piezometro',
                                file = 'plot/filtered.html')

filtered2.loc['ID', :].isin(filtered['ID'])

import numpy as np

filtered2.columns[np.invert(pd.Series(filtered2.columns).isin(filtered.columns.values))]

#filtered2 mantiene serie più consistenti e utilizzabili

t = meta.loc[meta['CODICE'] == 'PO0120750R2020', :]
print(t)
#cercare come stampare su console il contenuto di una riga di database in modo
#che sia facilmente leggibile

#Fill missing data


# %% Checks

#Check if the reference quotas of the piezometer changed in time
pqr = df.pivot(index = 'DATA', columns = 'CODICE PUNTO', values = 'Qr [m s.l.m.]')
pqr = pqr.resample('1Y').mean()
for col in pqr.columns:
    print(pqr[col].value_counts())
