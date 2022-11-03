# -*- coding: utf-8 -*-
"""
Rearrangement of the PTUA2022 dataset in a more easily usable dataset

Creation of a time series files structured as:
    - columns: piezometers and wells, identified by their code
    - rows: date (monthly)

author: paolo
"""

# %% Setup

import numpy as np
import pandas as pd

# %% Obtain a monthly dataset of the total head for each piezometer

#Load the basin's piezometer dataset
fname = 'data/PTUA2022/original/IT03GWBISSAPTA.csv'
df = pd.read_csv(fname)
#Set the data format
df['DATA'] = pd.to_datetime(df['DATA'], format = '%d/%m/%Y')
#Define a date/piezometer database
head = df.pivot(index = 'DATA', columns = 'CODICE PUNTO', values = 'PIEZOMETRIA [m s.l.m.]')
#Set the database to monthly
head = head.resample("1MS").mean()

head.to_csv('data/PTUA2022/head_IT03GWBISSAPTA.csv')

# %% Obtain the piezometer metadata of the GW basin considered 

#Load the full metadata dataset
meta = pd.read_csv('data/PTUA2022/metadata_piezometri_ISS.csv')
meta['ORIGINE'] = 'PTUA2022'
#correct "DATA_INIZIO"
meta['DATA_INIZIO'] = [head[col].first_valid_index() if col in head.columns else np.nan for col in meta['CODICE']]
# meta['DATA_FINE'] = [head[col].last_valid_index() if col in head.columns else np.nan for col in meta['CODICE']]

meta.to_csv('data/PTUA2022/meta_PTUA2022.csv', index = False)

# %% Visualize the time series

import dataviz as dv

# D = 5
# s, e = 0, 0
# for n in range(round(len(head.columns)/D)-1):
#     e = s + D if s + D < len(head.columns) else len(head.columns)-1
#     dv.fast_TS_visualization(head.iloc[:, s:e])
#     print(s, e)
#     s = e + 1

dv.interactive_TS_visualization(head, 'date', 'total head', markers = True, file = 'plot/db/original_TS_IT03GWBISSAPTA.html',
                                title = 'Database di partenza - Origine: PTUA2022')

# %% Possible operations on meta

#To extract only the metadata of the considered basin
basin = fname.split('.')[0].split('/')[-1]
meta_sel = meta.loc[meta['BACINO_WISE'] == basin, :]
