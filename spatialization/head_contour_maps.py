# -*- coding: utf-8 -*-
"""
Created on Tue Jul 26 18:22:15 2022

@author: paolo
"""

# %% Setup

import pandas as pd
import numpy as np
import dataanalysis as da
import dataviz as dv
import matplotlib.pyplot as plt
from class_SSA import SSA

# %% Load data and metadata

head = pd.read_csv('data/head_IT03GWBISSAPTA.csv', index_col = 'DATA')
meta = pd.read_csv('data/metadata_piezometri_ISS.csv', index_col = 'CODICE')

# %% Remove outliers

co = da.CheckOutliers(head, False)
head_fill = co.remove(skip = ['PO0120750R2020']).interpolate('linear', limit = 14)

trial = pd.DataFrame(head_fill.loc['2011-01-01', head_fill.columns.isin(meta.index)])
trial['x'] = meta.loc[trial.index, 'X_WGS84'].values
trial['y'] = meta.loc[trial.index, 'Y_WGS84'].values
