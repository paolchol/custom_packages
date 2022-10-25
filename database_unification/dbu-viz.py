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

idx = meta['ORIGINE'] != 'PTUA2022'
sel = meta.index[idx]

ts = head.loc[:, head.columns.isin(sel)]

dv.interactive_TS_visualization(ts, kwargs)