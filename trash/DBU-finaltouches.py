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

tool['CODICE_SIF'] = [f"0{int(idx)}" if not np.isnan(idx) else np.nan for idx in tool['CODICE_SIF']]
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
nc = cols[0:7] + [cols[31]] + cols[7:9] + cols[22:24] + cols[9:22] + cols[24:31]
test = test[nc]

test.rename(columns = {'X_WGS84': 'X', 'Y_WGS84': 'Y'}, inplace = True)
dw.join_twocols(test, ['NOTE', 'INFO'], rename = 'INFO', onlyna = False, add = True, inplace = True)

code_db = pd.read_csv('data/general/codes_SIF_PP.csv')

idx = test.index[test.index.isin(code_db['CODICE_PP'])]
code_db.set_index('CODICE_PP', inplace = True)
codes = code_db.loc[idx, 'CODICE_SIF']

test = pd.merge(test, codes, how = 'left', left_index = True, right_index = True)
test = dw.joincolumns(test)

idx = [code for code in test.index if code[0] != 'P']
codes = code_db.loc[code_db.loc[:, 'CODICE_SIF'].isin(test.loc[idx, 'CODICE_SIF']), 'CODICE_SIF']
idx = [pp for pp in codes.index if pp[0] == 'P']
codes = pd.DataFrame(codes[idx])
codes.reset_index(drop = False, inplace = True)

test.reset_index(drop = False, inplace = True)
t = pd.merge(test, pd.DataFrame(codes), how = 'left', left_on = 'CODICE_SIF', right_on = 'CODICE_SIF')
t = dw.join_twocols(t, ['CODICE', 'CODICE_PP'], onlyna = False)
