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

# head.to_csv('data/head_IT03GWBISSAPTA.csv')

# %% Obtain the piezometer metadata of the GW basin considered 

#Load the full metadata dataset
meta = pd.read_csv('data/metadata_piezometri_ISS.csv')
#To extract only the metadata of the considered basin
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

dv.interactive_TS_visualization(head, 'date', 'total head', file = 'plot/db/original_TS_IT03GWBISSAPTA.html')
