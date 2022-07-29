# -*- coding: utf-8 -*-
"""
Mann-Kendall test and Sen's slope analysis on the head observations
Comparison with the results obtained in the past for the same time series

@author: paolo
"""

# %% Setup

import pastas as ps
import pandas as pd
import numpy as np
import dataanalysis as da
import dataviz as dv
import matplotlib.pyplot as plt

# %% Load data and metadata

head = pd.read_csv('data/head_IT03GWBISSAPTA.csv', index_col = 'DATA')
meta = pd.read_csv('data/metadata_piezometri_ISS.csv')

# %% Select solid time series and fill missing values

cn = da.CheckNA(head)
filtered, _ = cn.filter_col(20, True)
co = da.CheckOutliers(filtered, False)
head_clean = co.remove()
head_fill = head_clean.interpolate('linear', limit = 14)

# %% Perform the Mann-Kendall test and calculate the Sen's slope

confidence = 0.95

#To compare with the PTUA2022 results and check that the algorithms
#are working fine, cut the series between 2009 and 2019
head_fill.index = pd.DatetimeIndex(head_fill.index)
idx = head_fill.index.isin(pd.DatetimeIndex(pd.date_range('2009-01-01', '2019-12-31')))
head_fill = head_fill.loc[idx, :]

db_mk = pd.DataFrame(np.zeros((len(head_fill.columns), 3)), columns = ['z','p','tr'], index = head_fill.columns)
db_slope = pd.DataFrame(np.zeros((len(head_fill.columns), 1)), columns = ['slope'], index = head_fill.columns)

for col in head_fill.columns:
    idx = db_mk.index.isin([col])
    db_mk.loc[idx, 'z'], db_mk.loc[idx, 'p'], db_mk.loc[idx, 'tr'] = da.mann_kendall(head_fill[col].dropna(), confidence)
    db_slope[db_slope.index.isin([col])], _, _, _ = da.sen_slope(head_fill[col].dropna())

#Compare with the results from PTUA 2022
meta = pd.read_csv('data/metadata_piezometri.csv', index_col = 'CODICE')
join = pd.merge(db_slope, meta.loc[:, ['SENSSLOPE_M_MESE', 'STATISTICA_MK', 'PVALUE']], left_index = True, right_index = True)
join = pd.merge(join, db_mk, left_index = True, right_index = True)

#The Mann-Kendall results present the same signs but values of the statistic
#differ. The Sen's slope values are instead pretty similar.

# %% Compare two methods of sen's slope computation

confidence = 0.95

import scipy.stats as st

for col in head_fill.columns:
    _, _, tr_type = da.mann_kendall(head_fill[col].dropna(), confidence)
    slope, _, _ = da.sen_slope(head_fill[col].dropna(), confidence, scipy = False)
    slopesc, _, _, _ = st.mstats.theilslopes(head_fill[col].dropna())
    print(f"{col}")
    print(f"Mann-Kendall: {tr_type}")
    print(f"Sen's slope: {slope}")
    print(f"Sen's slope (scipy): {slopesc}")
