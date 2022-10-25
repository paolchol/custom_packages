# -*- coding: utf-8 -*-
"""
Visualizations of the DBU database

@author: paolo
"""

import dataviz as dv
import datawrangling as dw
import numpy as np
import pandas as pd

meta = pd.read_csv('data/results/db-unification/meta_DBU-COMPLETE.csv', index_col = 'CODICE')
head = pd.read_csv('data/results/db-unification/head_DBU-COMPLETE.csv', index_col = 'DATA')
rprt = pd.read_csv('data/results/db-unification/report_merge_DBU-COMPLETE.csv', index_col = 'CODICE')

# visualizza serie aggiunte o ampliate

idx = meta['ORIGINE'] != 'PTUA2022'
sel = meta.index[idx]

ts = head.loc[:, head.columns.isin(sel)]

dv.interactive_TS_visualization(ts, xlab = 'Data', ylab = 'Livello piezometrico [m s.l.m.]',
                                file = 'plot/dbu/added_enhanced_DBU-COMPLETE.html',
                                markers = True, title = "Serie aggiunte o ampliate nell'aggregazione dei database")

ts.columns = meta.loc[ts.columns, 'COMUNE']

check = []
new = []
i = 1
for lab in ts.columns:
    if lab in check:
        new += [f'{lab}{i}']

test = [x for x in ts.columns if x == 'MILANO']
test = [f"{x}{i}" for i, x in enumerate(test, 1)]

dv.interactive_TS_visualization(ts, xlab = 'Data', ylab = 'Livello piezometrico [m s.l.m.]',
                                file = 'plot/dbu/added_enhanced_DBU-COMPLETE_COMUNE.html',
                                markers = True, title = "Serie aggiunte o ampliate nell'aggregazione dei database\n - Comuni")
