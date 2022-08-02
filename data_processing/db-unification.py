# -*- coding: utf-8 -*-
"""
Unificazione del dataset utilizzato per il PTUA 2003 con il dataset
reso disponibile da ARPA per il PTUA 2022

@author: paolo
"""

import pandas as pd
import numpy as np

# %% Controllo sui fogli presenti in LAU REG ticiadd.xls

laureg1 = pd.read_csv('data/old_head_dataset/original/LAU_REG_1_CAP_prov_MI.csv')

laureg2 = pd.read_csv('data/old_head_dataset/original/LAU_REG_2_TicinoAdda_settore.csv')
print(f"{sum(laureg2['CODICE'].isin(laureg1['CODICE']))} piezometri presenti su {len(laureg2.index)}")
#81 piezometri vanno aggiunti al database in laureg1

laureg3 = pd.read_csv('data/old_head_dataset/original/LAU_REG_3_cap.csv')
print(f"{sum(laureg3['codice'].isin(laureg1['CODICE']))} piezometri presenti su {len(laureg3.index)}")
#tutti i piezometri sono presenti

laureg4 = pd.read_csv('data/old_head_dataset/original/LAU_REG_4_mivecchi.csv')
print(f"{sum(laureg4['codice'].isin(laureg1['CODICE']))} piezometri presenti su {len(laureg4.index)}")
#tutti i piezometri sono presenti

#Load the old dataset
#head = pd.read_csv('data/head_IT03GWBISSAPTA.csv', index_col='DATA')
# %% Operazioni sul primo dataset

#Prima pulizia del dataset
df1 = laureg1.copy()
df1['COMUNE'] = [laureg1['COMUNE'][i].split()[0].upper().replace('_', ' ') for i in range(len(laureg1['COMUNE']))]
df1.insert(5, 'INFO', [' '.join(laureg1['COMUNE'][i].split()[1:]) for i in range(len(laureg1['COMUNE']))])
#Visualizza tutti i duplicati
vis = pd.concat(g for _, g in df1.groupby("CODICE") if len(g) > 1)
#Rimuovi i duplicati effettivi (stesso comune/posizione)
df1.drop(159, inplace = True)
#Aggiungere "D" all'inizio del codice ai codici duplicati che hanno diverso comune/posizione
df1.loc[df1.duplicated('CODICE'), 'CODICE'] = 'D' + df1.loc[df1.duplicated('CODICE'), 'CODICE'].values
#Riempire i buchi nei nomi dei codici con "codice_mancante_i" dove i è un numero progressivo
cond, i = [df1.loc[:, 'CODICE'].isna()][0], 1
for idx in cond.index:
    if cond[idx]:
        df1.loc[idx, 'CODICE'] = f'codice_mancante_{i}'
        i += 1

#Ottenere il dataset delle serie dati
ts1 = df1.iloc[:, [0] + [x for x in range(6, len(df1.columns))]].copy()
ts1 = ts1.set_index('CODICE').transpose()
ts1.set_index(pd.date_range('1996-01-01', '2003-01-01', freq = 'MS'), inplace = True)
#Rimuovere codici e caratteri non voluti
ts1.replace(' -', np.nan, inplace = True)
ts1.replace(' ', np.nan, inplace = True)
ts1.replace('asciutto', '9999', inplace = True) #sostituisce asciutto con 9999, così che il livello risulti poi negativo
ts1.replace(',', '.', inplace = True)
ts1.replace('* 12,2', 12.2, inplace = True)
#Transforma in valori numerici
for i in range(len(ts1.columns)):
    ts1.iloc[:, i] = pd.to_numeric(ts1.iloc[:, i])
#Ottenere il dataset dei metadata
meta1 = df1.iloc[:, [x for x in range(6)]].set_index('CODICE')
meta1.replace('-', np.nan, inplace = True)
meta1.replace(' ', np.nan, inplace = True)
meta1['z'] = pd.to_numeric(meta1.loc[:, 'z'])
#Il database contiente la soggiacenza
#Ottenere il livello (differenza tra quota z e soggiacenza)
for col in ts1.columns:
    if np.isnan(meta1.loc[col, 'z']):
         print(col, ' ', meta1.loc[col, 'COMUNE'], ' non ha quota assegnata')
    ts1[col] = meta1.loc[col, 'z'] - ts1[col]
ts1[ts1 < 0] = 0 #sostituisce i livelli negativi con 0 (condizione "asciutto")

# %% Operazioni sul secondo dataset

#Prima pulizia del dataset
df2 = laureg2.copy()
df2 = df2.iloc[:, 0:df2.columns.get_loc('apr-03')+1]
df2['COMUNE'] = [laureg2['COMUNE'][i].split('-')[0].upper() for i in range(len(laureg2['COMUNE']))]

df2['COMUNE'] = [df2['COMUNE'][i].rstrip() for i in range(len(df2['COMUNE']))]

df2['INFO'] = [f"{laureg2['INFO'][i]} {' '.join(laureg2['COMUNE'][i].split('-')[1:])}" for i in range(len(laureg2['COMUNE']))]
# sum(df2.loc[:, 'CODICE'].isna()) #nessun codice mancante

# df2['CODICE'] = df2['CODICE'].astype("string")

sum(df2.duplicated('CODICE')) #14 codici duplicati
#Visualizza tutti i duplicati

vis = pd.concat(g for _, g in df2.groupby("CODICE") if len(g) > 1)
#Rimuovi duplicati
for code in df2.loc[df2.duplicated('CODICE'), 'CODICE']:
    dupl = vis.loc[vis['CODICE'] == code, 'COMUNE']
    s = dupl.to_numpy()
    if (s[0] == s).all():
        #rimuovi l'indice corrispondente alla prima riga da df2
        pass
    else:
        #aggiungi il numero del settore al codice
        #{codice}-S{settore}
        pass
        


#rendere i nomi delle colonne uguali a quelli di df1

# %% Salva i risultati

#Salva il riult
# ts1.to_csv('data/old_head_dataset/head_old_TICINOADDA.csv')
# meta1.to_csv('data/old_head_dataset/meta_old_TICINOADDA.csv')


# %% join df1 e df2

df = pd.join(df1, df2)
