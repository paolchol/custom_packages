# -*- coding: utf-8 -*-
"""
Complete processing of the head dataset, with visualization of result

@author: paolo
"""

import pandas as pd
import dataanalysis as da

head = pd.read_csv('data/head_IT03GWBISSAPTA.csv', index_col = 'DATA')
meta = pd.read_csv('data/metadata_piezometri_ISS.csv')

cn = da.CheckNA(head)
filtered, removed = cn.filter_col(20, True)
co = da.CheckOutliers(filtered, False)
# checkdb = co.output
head_clean = co.remove()
head_fill = head_clean.interpolate('linear', limit = 14)

import dataviz as dv
dv.interactive_TS_visualization(head_fill)
