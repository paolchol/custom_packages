# -*- coding: utf-8 -*-
"""
DBU: DataBase Unification
Unificazione del dataset Milano1950 con il database unificato DBU-5

Le operazioni necessarie per ottenere meta e head sono state svolte in
Milano1950_struct.py

@author: paolo
"""

# %% Setup

import dataviz as dv
import datawrangling as dw
import geodata as gd
import pandas as pd
import numpy as np

# %% Load Olona meta and data

meta = pd.read_csv('data/Olona/meta_Olona_filtered.csv', index_col = 'CODICE')
head = pd.read_csv('data/Olona/head_Olona.csv', index_col = 'DATA')
head.index = pd.DatetimeIndex(head.index)
