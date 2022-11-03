# -*- coding: utf-8 -*-
"""
Visualizations of the DBU database

@author: paolo
"""
# %% Setup
import dataviz as dv
import datawrangling as dw
import numpy as np
import pandas as pd

# %% Carica dati

meta = pd.read_csv('data/results/db-unification/meta_DBU-COMPLETE.csv', index_col = 'CODICE')
head = pd.read_csv('data/results/db-unification/head_DBU-COMPLETE.csv', index_col = 'DATA')
rprt = pd.read_csv('data/results/db-unification/report_merge_DBU-COMPLETE.csv', index_col = 'CODICE')

# %% Visualizza serie aggiunte e ampliate

idx = meta['ORIGINE'] != 'PTUA2022'
sel = meta.index[idx]
ts = head.loc[:, head.columns.isin(sel)]

#Visualizza con il codice come etichetta
dv.interactive_TS_visualization(ts, xlab = 'Data', ylab = 'Livello piezometrico [m s.l.m.]',
                                file = 'plot/dbu/added_enhanced_DBU-COMPLETE.html',
                                markers = True, title = "Serie aggiunte o ampliate nell'aggregazione dei database - Non processate")
#Visualizza con il comune come etichetta
ts.columns = dw.enum_instances(meta.loc[ts.columns, 'COMUNE'], ['MILANO'])
dv.interactive_TS_visualization(ts, xlab = 'Data', ylab = 'Livello piezometrico [m s.l.m.]',
                                file = 'plot/dbu/added_enhanced_DBU-COMPLETE_COMUNE.html',
                                markers = True, title = "Serie aggiunte o ampliate nell'aggregazione dei database - Non processate")

# %% Visualizza tutto il database

#Visualizza con il comune come etichetta
meta.loc[head.columns, 'COMUNE']
