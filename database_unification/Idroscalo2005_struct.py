# -*- coding: utf-8 -*-
"""
Idroscalo2005 database rearrangement

- Load the database
- Rearrange it to create a meta and a head

@author: paolo
"""

#%% Setup

import datawrangling as dw
import pandas as pd
import numpy as np

# %% Load

original = pd.read_csv('data/Idroscalo2005/misurazioni livello falda_Idroscalo2005.csv')

# %% Split in meta and data databases

cols = original.columns.to_list()
metacols = cols[0:3] + [cols[-2]]
datacols = [cols[0]] + cols[3:5] + [cols[-1]]
meta = original[metacols].copy()
data = original[datacols].copy()

#meta
meta.drop_duplicates('codice', 'first', inplace = True)
meta.rename(columns = {'Quota rifgerimento [m]': 'z', 'codice': 'CODICE'}, inplace = True)
meta['CODICE'] = [f"0{idx}" for idx in meta['CODICE']]
meta.set_index('CODICE', inplace = True)
meta['ORIGINE'] = 'Idroscalo2005'

#data
data.rename(columns = {'Piezometria [m s.l.m.]': 'head'}, inplace = True)
data['codice'] = [f"0{idx}" for idx in data['codice']]
datacol = [f"{a}-{b}-01" for a, b in zip(data['anno'], data['mese'])]
datacol = pd.to_datetime(datacol, format = "%Y-%m-%d")
data['DATA'] = datacol
data.drop(columns = ['anno', 'mese'], inplace = True)
data.set_index('DATA', inplace = True)
head = data.pivot(columns = 'codice', values = 'head')

meta.to_csv('data/Idroscalo2005/meta_Idroscalo2005.csv')
head.to_csv('data/Idroscalo2005/head_Idroscalo2005.csv')

# %% Lake levels

#rearrange the lake levels dataset so it becomes possible to merge with DBU
lake87 = pd.read_csv('data/Idroscalo2005/quote slm livelli lago.csv')
lake03 = pd.read_csv('data/Idroscalo2005/original/lv_2003_2022.csv')
lake03.columns = ['DATA'] + [f'{y}' for y in range(2003,2023)]

lake = pd.merge(lake03, lake87, how = 'left', left_on = 'DATA', right_on = 'DATA')
lake = dw.joincolumns(lake, col_order = ['DATA'] + [f'{y}' for y in range(1987,2023)])

lake.set_index('DATA', inplace = True)

lake = lake.stack(dropna = False)

months = ['gen', 'feb', 'mar', 'apr', 'mag', 'giu', 'lug', 'ago', 'set', 'ott', 'nov', 'dic']
d = {month: index for index, month in enumerate(months, start = 1) if month}

datecol = []
for date in lake.index:
    if (date[0].split('-')[0] == '29') & (d[date[0].split('-')[1]] == 2):
           lake.drop(date, inplace = True)
    else:
        tool = str(date[0].split('-')[0]) + '-' + str(d[date[0].split('-')[1]]) + '-' + str(date[1])
        datecol += [pd.to_datetime(tool, format = '%d-%m-%Y')]
lake.reset_index(inplace = True, drop = True)
lake.index = datecol
lake.sort_index(inplace = True)
lake.index.names, lake.name = ['DATA'], 'level'

import dataviz as dv
dv.interactive_TS_visualization(lake.resample('MS').mean(), markers = True)

#save the series
lake.to_csv('data/Idroscalo2005/lake_levels_daily.csv')
#resample the series to monthly
lake.resample('MS').mean().to_csv('data/Idroscalo2005/lake_levels_monthly.csv')
