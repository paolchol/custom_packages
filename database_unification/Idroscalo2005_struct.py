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