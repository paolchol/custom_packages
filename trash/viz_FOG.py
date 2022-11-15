# -*- coding: utf-8 -*-
"""
Created on Tue Nov 15 17:18:22 2022

@author: paolo
"""

import dataviz as dv
import numpy as np
import pandas as pd

meta = pd.read_csv('data/results/db-unification/meta_DBU-COMPLETE.csv', index_col = 'CODICE')
meta['CODICE_SIF'] = [f"0{int(idx)}" if not np.isnan(idx) else np.nan for idx in meta['CODICE_SIF']]
ts = pd.read_csv('data/results/db-unification/headcorr_DBU-COMPLETE.csv', index_col = 'DATA')

sel = meta.loc[['FOG' in string for string in meta['ORIGINE']], :]
tssel = ts.loc[:, sel.index[sel.index.isin(ts.columns)]]
tssel.columns = meta.loc[tssel.columns, 'CODICE_FOG']

dv.interactive_TS_visualization(tssel)

ogmeta = pd.read_csv('data/Milano1950/meta_Milano1950.csv', index_col = 'CODICE')
oghead = pd.read_csv('data/Milano1950/head_Milano1950.csv', index_col = 'DATA')

tool = oghead.loc[:, ogmeta.loc[ogmeta['PIEZOMETRO'] == 'FOG4'].index]
tool = pd.merge(tool, ts.loc[:, meta.loc[meta['CODICE_FOG'] == 'FOG4', :].index], left_index = True, right_index = True)

dv.interactive_TS_visualization(tool, markers = True)

#dal 2002 al 2007 inserire i dati presi direttamente dalla serie originale