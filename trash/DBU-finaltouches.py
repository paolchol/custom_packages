# -*- coding: utf-8 -*-
"""
DBU operations after the last merge
Then put this script in the Final operation cell in DBU-COMPLETE

@author: paolo
"""

import pandas as pd

metamerge = pd.read_csv('data/results/db-unification/meta_DBU-COMPLETE.csv', index_col = 'CODICE')
headmerge = pd.read_csv('data/results/db-unification/head_DBU-COMPLETE.csv', index_col = 'DATA')

