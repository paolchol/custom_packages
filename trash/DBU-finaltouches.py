# -*- coding: utf-8 -*-
"""
DBU operations after the last merge
Then put this script in the Final operation cell in DBU-COMPLETE

@author: paolo
"""

import datawrangling as dw
import numpy as np
import pandas as pd

def datecol_arrange(datecol):
    dates = []
    for date in datecol:
        if date == date:
            s = date.split('/')
            s.reverse()
            dates += ['-'.join(s)]
        else:
            dates += [np.nan]
    return dates

metamerge = pd.read_csv('data/results/db-unification/meta_DBU-COMPLETE.csv', index_col = 'CODICE')
headmerge = pd.read_csv('data/results/db-unification/head_DBU-COMPLETE.csv', index_col = 'DATA')

tool = metamerge.copy()
tool['DATA_INIZIO'] = datecol_arrange(tool['DATA_INIZIO'])

df = pd.DataFrame(headmerge.columns, columns = ['CODICE'])
df['DATA_INIZIO'] = [headmerge[col].first_valid_index() for col in headmerge.columns]
df['DATA_FINE'] = [headmerge[col].last_valid_index() for col in headmerge.columns]
df.set_index('CODICE', inplace = True)

test = pd.merge(tool, df, how = 'left', left_index = True, right_index = True)

#Check
old = pd.to_datetime(test['DATA_INIZIO_x'], format = '%Y-%m-%d')
new = pd.to_datetime(test['DATA_INIZIO_y'], format = '%Y-%m-%d')
delta = new - old
delta = delta[pd.notnull(delta)]
delta = [dt.days for dt in delta]
delta = [dt for dt in delta if dt < 0]
print(f"Numero di serie che hanno avuto un incremento di dati: {len(delta)}")
print(f"Incremento medio di dati: {round(abs(sum(delta)/len(delta))/365, 2)} anni")

test = dw.join_twocols(test, ['DATA_INIZIO_x', 'DATA_INIZIO_y'], rename = 'DATA_INIZIO', onlyna = False)

cols = test.columns.to_list()
nc = cols[0:6] + [cols[30]] + cols[6:8] + cols[21:23] + cols[8:21] + cols[23:30]
test = test[nc]

test.rename(columns = {'X_WGS84': 'X', 'Y_WGS84': 'Y'}, inplace = True)
dw.join_twocols(test, ['NOTE', 'INFO'], rename = 'INFO', onlyna = False, add = True, inplace = True)

code_db = pd.read_csv('data/general/codes_SIF_PP.csv')

idx = metamerge.index[metamerge.index.isin(code_db['CODICE_PP'])]
tt = metamerge.loc[idx, 'CODICE_SIF']
code_db.set_index('CODICE_PP', inplace = True)
tt2 = code_db.loc[idx, 'CODICE_SIF']

#merge mergemeta con tt2, poi fare join cols con onlyna = False
