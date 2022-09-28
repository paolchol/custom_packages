# -*- coding: utf-8 -*-
"""
dbu: DataBase Unification
Unificazione del dataset utilizzato per il PTUA 2003 con il dataset
reso disponibile da ARPA per il PTUA 2022
pt2: Parte 2
Associazione dei piezometri del PTUA2003 a quelli disponibili al PTUA 2022

@author: paolo
"""

# %% Setup

import dataviz as dv
import datawrangling as dw
import geodata as gd
import numpy as np
import pandas as pd

# %% Load the metadata

#Metadata dei dati usati nel PTUA 2022
meta2022 = pd.read_csv('data/PTUA2022/metadata_piezometri_ISS.csv', index_col = 'CODICE')
#Metadata dei dati usati nel PTUA 2003
meta2003 = pd.read_csv('data/PTUA2003/meta_PTUA2003_TICINOADDA_filtered.csv', index_col = 'CODICE')
#Database incrociato: contiene associazione tra codici SIF e PP
code_db = pd.read_csv('data/general/codes_SIF_PP.csv')

# %% Associate codes from one database to the other

#1. Link meta2003 codes to meta2022 codes through a database containing
#   SIF codes and PP codes
sum(meta2003.index.isin(code_db['CODICE_SIF']))
sum(meta2003.index.isin(code_db['CODICE_PP']))

sum(meta2022.index.isin(code_db['CODICE_PP']))

idx = meta2003.index.isin(code_db['CODICE_SIF'])
sifpp = code_db.loc[code_db['CODICE_SIF'].isin(meta2003.index), ['CODICE_SIF', 'CODICE_PP']]
sifpp.set_index('CODICE_SIF', inplace = True)

#2. Find the piezometers and wells which are less than 100 m apart in the two db
#Change the CRS of both database to lat, lon in WGS84
# meta2003
# remove lines without coordinates
idx = meta2003.loc[:, ['x', 'y']].isna().apply(all, 1)
tool2003 = meta2003.drop(meta2003.index[idx]).copy()
# keep piezo with FALDA in 1, SUPERF.
tool2003 = tool2003.loc[tool2003['FALDA'].isin(['1', np.nan, 'SUPERF.', 'SUPERF. (acquifero locale)']), :]
out = gd.transf_CRS(tool2003.loc[:, 'x'], tool2003.loc[:, 'y'], 'EPSG:3003', 'EPSG:4326', series = True)
tool2003['lat'], tool2003['lon'] = out[0], out[1]
## meta2022
out = gd.transf_CRS(meta2022.loc[:, 'X_WGS84'], meta2022.loc[:, 'Y_WGS84'], 'EPSG:32632', 'EPSG:4326', series = True)
meta2022['lat'], meta2022['lon'] = out[0], out[1]
#Find the nearest point from meta2022 to each point of meta2003
db_nrst = gd.find_nearestpoint(tool2003, meta2022,
                     id1 = 'CODICE', coord1 = ['lon', 'lat'],
                     id2 = 'CODICE', coord2 = ['lon', 'lat'],
                     reset_index = True)
#Select the points with distance less than 100 meters
db_nrst = db_nrst[db_nrst['dist'] < 100]

#3. Join the two code lists
codelst = pd.merge(sifpp, db_nrst.loc[:, ['CODICE', 'CODICE_nrst']], how = 'outer', left_index = True, right_on = 'CODICE')
codelst.reset_index(inplace = True, drop = True)
codelst.loc[np.invert(codelst['CODICE_nrst'].isna()), 'CODICE_PP'] = codelst.loc[np.invert(codelst['CODICE_nrst'].isna()), 'CODICE_nrst']
codelst.drop(columns = 'CODICE_nrst', inplace = True)
codelst.rename(columns = {'CODICE': 'CODICE_PTUA2003', 'CODICE_PP': 'CODICE_link'}, inplace = True)
codelst.set_index('CODICE_PTUA2003', inplace = True)

# %% Merge metadata

sum(codelst.isin(meta2022.index).values)
meta = dw.mergemeta(meta2022, meta2003, link = codelst,
                    firstmerge = dict(left_index = True, right_index = True),
                    secondmerge = dict(left_index = True, right_on = 'CODICE_link',
                                       suffixes = [None, "_PTUA2003"]))
meta.rename(columns = {'CODICE_link': 'CODICE', 'index': 'CODICE_PTUA2003'}, inplace = True)
meta.set_index('CODICE', inplace = True)
meta.drop(columns = ['SETTORE', 'STRAT.', 'PROVINCIA_PTUA2003', 'x', 'y', 'COMUNE_PTUA2003'], inplace = True)
meta.rename(columns = {'z': 'z_PTUA2003', 'INFO': 'INFO_PTUA2003'}, inplace = True)

#Split SIF code from the other PTUA2003 codes
codePTUA = []
codeSIF = []
for code in meta['CODICE_PTUA2003']:
    if isinstance(code, str):
        if code[0:3] == '015':
            codeSIF += [code]
            codePTUA += [np.nan]
        else:
            codeSIF += [np.nan]
            codePTUA += [code]
    else:
        codePTUA += [np.nan]
        codeSIF += [np.nan]
meta['CODICE_PTUA2003'] = codePTUA
meta.insert(0, column = 'CODICE_SIF', value = codeSIF)

meta.to_csv('data/results/db-unification/meta_DBU-1.csv')

# %% Merge the time series

#Merge the PTUA2003 time series to the PTUA2022 time series
# by joining the piezometers which have been associated and considered as the same
head2022 = pd.read_csv('data/PTUA2022/head_IT03GWBISSAPTA.csv', index_col='DATA')
head2003 = pd.read_csv('data/PTUA2003/head_PTUA2003_TICINOADDA_unfiltered.csv', index_col='DATA')
head2022.index = pd.DatetimeIndex(head2022.index)
head2003.index = pd.DatetimeIndex(head2003.index)

codes = meta.loc[meta['BACINO_WISE'] == 'IT03GWBISSAPTA', 'CODICE_PTUA2003'].dropna()
sum(codes.index.isin(head2022.columns))
headmerge = dw.mergets(head2022, head2003, codes)

#visualize the merged datasets
vis = head2003[codes]
vismerge = headmerge[codes.index]
dv.interactive_TS_visualization(vismerge, file = 'plot/dbu/added_ts_PTUA2003PTUA2022.html')
#esempio di piezometro con balzo
meta.loc['PO0151080U0002', :]
meta.loc['PO0151810U0001', :]
#z_PTUA2003 e QUOTA_PC_S sono differenti: da tenere presente in fase di data processing!

headmerge.to_csv('data/results/db-unification/head_DBU-1.csv')
