# -*- coding: utf-8 -*-
"""
Created on Thu Jul 28 13:43:56 2022

@author: paolo
"""

import pandas as pd

sgi = pd.read_csv('analisi_serie_storiche/res_SGI.csv', index_col='DATA')
meta = pd.read_csv('data/metadata_piezometri_ISS.csv')

sgisel = pd.DataFrame(sgi.loc['2011-09-01', :])
sgisel.rename(columns = {'2011-09-01': 'z'}, inplace = True)
sgisel = sgisel.loc[sgisel.index.isin(meta['CODICE'])]
sgisel['x'] = meta.loc[meta['CODICE'].isin(sgisel.index), 'X_WGS84'].values
sgisel['y'] = meta.loc[meta['CODICE'].isin(sgisel.index), 'Y_WGS84'].values

sgisel.dropna().to_csv('sgi2011_ok.csv')

sgisel = pd.DataFrame(sgi.loc['2018-10-01', :])
sgisel.rename(columns = {'2018-10-01': 'z'}, inplace = True)
sgisel = sgisel.loc[sgisel.index.isin(meta['CODICE'])]
sgisel['x'] = meta.loc[meta['CODICE'].isin(sgisel.index), 'X_WGS84'].values
sgisel['y'] = meta.loc[meta['CODICE'].isin(sgisel.index), 'Y_WGS84'].values

sgisel.dropna().to_csv('sgi2018.csv')
