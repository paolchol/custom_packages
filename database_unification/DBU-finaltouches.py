# -*- coding: utf-8 -*-
"""
DBU operations after the last merge
Then put this script in the Final operation cell in DBU-COMPLETE

@author: paolo
"""

import datawrangling as dw
import numpy as np
import pandas as pd

metamerge = pd.read_csv('data/results/db-unification/meta_DBU-COMPLETE.csv', index_col = 'CODICE')
headmerge = pd.read_csv('data/results/db-unification/head_DBU-COMPLETE.csv', index_col = 'DATA')
rprtmerge = pd.read_csv('data/results/db-unification/report_merge_DBU-COMPLETE.csv', index_col = 'CODICE')

metamerge['CODICE_SIF'] = [f"0{int(idx)}" if not np.isnan(idx) else np.nan for idx in metamerge['CODICE_SIF']]
metamerge['DATA_INIZIO'] = dw.datecol_arrange(metamerge['DATA_INIZIO'])

df = pd.DataFrame(headmerge.columns, columns = ['CODICE'])
df['DATA_INIZIO'] = [headmerge[col].first_valid_index() for col in headmerge.columns]
df['DATA_FINE'] = [headmerge[col].last_valid_index() for col in headmerge.columns]
df.set_index('CODICE', inplace = True)

metamerge = pd.merge(metamerge, df, how = 'left', left_index = True, right_index = True)

#Check
old = pd.to_datetime(metamerge['DATA_INIZIO_x'], format = '%Y-%m-%d')
new = pd.to_datetime(metamerge['DATA_INIZIO_y'], format = '%Y-%m-%d')
delta = new - old
delta = delta[pd.notnull(delta)]
delta = [dt.days for dt in delta]
delta = [dt for dt in delta if dt != 0]

metamerge = dw.join_twocols(metamerge, ['DATA_INIZIO_x', 'DATA_INIZIO_y'], rename = 'DATA_INIZIO', onlyna = False)

cols = metamerge.columns.to_list()
nc = cols[0:7] + [cols[31]] + cols[7:9] + cols[22:24] + cols[9:22] + cols[24:31]
metamerge = metamerge[nc]

metamerge.rename(columns = {'X_WGS84': 'X', 'Y_WGS84': 'Y'}, inplace = True)
dw.join_twocols(metamerge, ['NOTE', 'INFO'], rename = 'INFO', onlyna = False, add = True, inplace = True)

code_db = pd.read_csv('data/general/codes_SIF_PP.csv')

idx = metamerge.index[metamerge.index.isin(code_db['CODICE_PP'])]
code_db.set_index('CODICE_PP', inplace = True)
codes = code_db.loc[idx, 'CODICE_SIF']

metamerge = pd.merge(metamerge, codes, how = 'left', left_index = True, right_index = True)
metamerge = dw.joincolumns(metamerge)

idx = [code for code in metamerge.index if code[0] != 'P']
codes = code_db.loc[code_db.loc[:, 'CODICE_SIF'].isin(metamerge.loc[idx, 'CODICE_SIF']), 'CODICE_SIF']
idx = [pp for pp in codes.index if pp[0] == 'P']
codes = pd.DataFrame(codes[idx])
codes.reset_index(drop = False, inplace = True)

metamerge.reset_index(drop = False, inplace = True)
metamerge = pd.merge(metamerge, pd.DataFrame(codes), how = 'left', left_on = 'CODICE_SIF', right_on = 'CODICE_SIF')
#change the code also in report
metamerge.set_index('CODICE', inplace = True)
idx = metamerge.loc[rprtmerge.index, 'CODICE_PP'].notna()
rprtmerge.reset_index(drop = False, inplace = True)
rprtmerge.loc[idx.values, 'CODICE'] = metamerge.loc[rprtmerge['CODICE'], 'CODICE_PP'][idx].values
rprtmerge.set_index('CODICE', inplace = True)
#merge the two code columns
metamerge.reset_index(drop = False, inplace = True)
metamerge = dw.join_twocols(metamerge, ['CODICE', 'CODICE_PP'], onlyna = False)

#print
print(f"Numero totale di serie aggregate o aggiunte al database: {rprtmerge.shape[0]}")
print(f"Numero di serie che hanno avuto un allungamento della serie storica: {len(delta)}")
print(f"Numero di serie aggiunte ex-novo: {len([code for code in rprtmerge.index if code[0] != 'P'])}")
print(f"Incremento medio di dati: {round(abs(sum(delta)/len(delta))/365, 2)} anni")

# %% trials

#prova: ripartizione dell'origine dei dati per serie aggiunte e aggiornate
# import matplotlib.pyplot as plt
# plt.hist(rprtmerge['tag'])
# plt.show()