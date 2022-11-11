# -*- coding: utf-8 -*-
"""
Rearrangement of the PTUA2022 dataset in a more easily usable dataset

Creation of a time series files structured as:
    - columns: piezometers and wells, identified by their code
    - rows: date (monthly)

author: paolo
"""

# %% Setup

import numpy as np
import pandas as pd

# %% Obtain a monthly dataset of the total head for each piezometer

#Load the basin's piezometer dataset
fname = 'data/PTUA2022/original/IT03GWBISSAPTA.csv'
df = pd.read_csv(fname)
#Set the data format
df['DATA'] = pd.to_datetime(df['DATA'], format = '%d/%m/%Y')
#Define a date/piezometer database
head = df.pivot(index = 'DATA', columns = 'CODICE PUNTO', values = 'PIEZOMETRIA [m s.l.m.]')
#Set the database to monthly
head = head.resample("1MS").mean()

head.to_csv('data/PTUA2022/head_IT03GWBISSAPTA.csv')

# %% Obtain the piezometer metadata of the GW basin considered 

#Load the full metadata dataset
meta = pd.read_csv('data/PTUA2022/metadata_piezometri_ISS.csv')
meta['ORIGINE'] = 'PTUA2022'
#correct "DATA_INIZIO"
meta['DATA_INIZIO'] = [head[col].first_valid_index() if col in head.columns else np.nan for col in meta['CODICE']]

meta.to_csv('data/PTUA2022/meta_PTUA2022.csv', index = False)

# %% Visualize the time series

import dataviz as dv
import datawrangling as dw

# D = 5
# s, e = 0, 0
# for n in range(round(len(head.columns)/D)-1):
#     e = s + D if s + D < len(head.columns) else len(head.columns)-1
#     dv.fast_TS_visualization(head.iloc[:, s:e])
#     print(s, e)
#     s = e + 1

head = head.loc[:, head.columns.isin(meta['CODICE'])]
head.columns = dw.enum_instances(meta.set_index('CODICE').loc[head.columns, 'COMUNE'], ['MILANO', 'MONZA', 'CERNUSCO LOMBARDONE', 'SESTO SAN GIOVANNI'])
dv.interactive_TS_visualization(head, 'date', 'total head', markers = True, file = 'plot/db/original_TS_IT03GWBISSAPTA.html',
                                title = 'Database di partenza - Origine: PTUA2022')

# %% Visualize histogram

import dataanalysis as da
import matplotlib.pyplot as plt

#calcolare numero e percentuale di serie storiche aggiunte
# grafico a barre/istogramma: lunghezza delle serie in anni

meta['DATA_FINE'] = [head[col].last_valid_index() if col in head.columns else np.nan for col in meta['CODICE']]
meta.set_index('CODICE', inplace = True)
tool = meta.loc[meta['BACINO_WISE'] == 'IT03GWBISSAPTA', ['DATA_INIZIO', 'DATA_FINE']].copy()
tool['delta'] = pd.to_datetime(tool['DATA_FINE']) - pd.to_datetime(tool['DATA_INIZIO'])
tool['delta'] = [x.days/365 for x in tool['delta']]

cna = da.CheckNA(head)
cna.check()
tool = tool.merge(cna.output, how = 'left', left_index = True, right_on = 'ID')
tool['delta_corr'] = tool['delta'] * (100 - tool['perc_NA'])/100
tool.drop(columns = ['DATA_INIZIO', 'DATA_FINE', 'perc_NA'], inplace = True)
tool.set_index('ID', inplace = True)
tool.index.names = ['CODICE']

#Set the resolution 
dv.set_res(500)

labels = ['Lunghezza apparente', 'Lunghezza reale']
#Lunghezza apparente = Fine - Inizio
#Lunghezza reale: (Fine - Inizio) x Percentuale dati presenti

plt.hist(tool, bins = 'auto', histtype = 'barstacked',
         label = labels, color = ['tab:blue', 'tab:olive'])
plt.xlabel('Quantità di dati nella serie storica [anni]')#, {'fontname': 'Arial'})
plt.ylabel('Numero di serie storiche')
plt.title('Ripartizione delle serie storiche in base alla loro popolazione')
plt.ylim([0,22.5])
plt.text(12.5, 17.5, f"Numero di serie storiche: {tool.shape[0]}")
plt.legend(loc = 'upper right')
plt.savefig('plot/dbu/hist_PTUA2022.png')
plt.show()

#Visualizzazione alternativa:
fig = plt.figure()
ax = plt.subplot(111)
ax.hist(tool, bins = 'auto', histtype = 'barstacked',
         label = labels, color = ['tab:blue', 'tab:olive'])
box = ax.get_position()
ax.set_position([box.x0, box.y0 + box.height * 0.1,
                 box.width, box.height * 0.9])
ax.legend(loc='upper center', bbox_to_anchor = (0.5, 1.1),
          fancybox = False, shadow = True, ncol = 2)
fig.layout(title = 'Ripartizione delle serie storiche in base alla loro popolazione')

plt.show()

# %% Possible operations on meta

#To extract only the metadata of the considered basin
basin = fname.split('.')[0].split('/')[-1]
meta_sel = meta.loc[meta['BACINO_WISE'] == basin, :]
