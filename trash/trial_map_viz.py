# -*- coding: utf-8 -*-
"""
Visualization trials of the dataset

@author: paolo
"""

import dataviz as dv
import geodata as gd
import numpy as np
import pandas as pd


metaDBU = pd.read_csv('data/results/db-unification/meta_DBU-5.csv', index_col = 'CODICE')
metaDBU['CODICE_SIF'] = [f"0{int(idx)}" if not np.isnan(idx) else np.nan for idx in metaDBU['CODICE_SIF']]

viz = metaDBU.loc[metaDBU['BACINO_WISE'] == 'IT03GWBISSAPTA', :].copy().reset_index()
viz.loc[viz['ORIGINE'].isna(), 'ORIGINE'] = 'PTUA2022'

gd.show_mappoints(viz, 'lat', 'lon', file = 'trash/viz_trial.html', color = 'ORIGINE', hover_name = 'CODICE')


#calcolare numero e percentuale di serie storiche aggiunte

headDBU = pd.read_csv('data/results/db-unification/head_DBU-5.csv', index_col = 'DATA')
headDBU.index = pd.DatetimeIndex(headDBU.index)
dv.interactive_TS_visualization(headDBU[metaDBU.loc[metaDBU['COMUNE'].isin(['OSNAGO', 'MEZZAGO']), :].index], markers = True)
