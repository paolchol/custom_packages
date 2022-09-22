# -*- coding: utf-8 -*-
"""
dbu: DataBase Unification
Unificazione del dataset utilizzato per il PTUA 2003 con il dataset
reso disponibile da ARPA per il PTUA 2022
pt1: Parte 1
Sistemazione dei database dei piezometri nel bacino Adda-Ticino utilizzati per
il PTUA 2003

@author: paolo
"""

import pandas as pd
import numpy as np
import datawrangling as dw

# %% Controllo sui fogli presenti in LAU REG ticiadd.xls

laureg1 = pd.read_csv('data/PTUA2003/original/LAU_REG_1_CAP_prov_MI.csv')

laureg2 = pd.read_csv('data/PTUA2003/original/LAU_REG_2_TicinoAdda_settore.csv')
print(f"{sum(laureg2['CODICE'].isin(laureg1['CODICE']))} piezometri presenti su {len(laureg2.index)}")
#81 piezometri vanno aggiunti al database in laureg1

laureg3 = pd.read_csv('data/PTUA2003/original/LAU_REG_3_cap.csv')
print(f"{sum(laureg3['codice'].isin(laureg1['CODICE']))} piezometri presenti su {len(laureg3.index)}")
#tutti i piezometri sono presenti

laureg4 = pd.read_csv('data/PTUA2003/original/LAU_REG_4_mivecchi.csv')
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
#Rimuovere codici e caratteri non voluti (trovati con trial and error trasformando in numerico)
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
#Rimuovi colonne vuote
df2.drop(['NOTE', 'PUBBLICO'], axis = 1, inplace = True)
#Rinomina le colonne come df1
df2.rename(columns = {'X_GAUSS-BOAGA': 'x', 'Y_GAUSS-BOAGA': 'y', 'Q': 'z'}, inplace = True)
#Ricerca di codici mancanti o duplicati
sum(df2.loc[:, 'CODICE'].isna()) #nessun codice mancante
sum(df2.duplicated('CODICE')) #14 codici duplicati
#Visualizza tutti i duplicati
vis = pd.concat(g for _, g in df2.groupby("CODICE") if len(g) > 1)
#Rimuovi duplicati
for code in df2.loc[df2.duplicated('CODICE'), 'CODICE']:
    if code in df2.loc[df2.duplicated('CODICE'), 'CODICE'].values: 
        dupl = vis.loc[vis['CODICE'] == code, 'COMUNE']
        s = dupl.to_numpy()
        if (s[0] == s).all():
            #Mantiene l'ultimo duplicato (contenente "CAP" nell'info)
            keep = df2.loc[dupl.index, :].drop_duplicates('CODICE', keep = 'last').index[0]
            df2.drop(dupl.index[dupl.index!= keep], inplace = True)
        else:
            #Aggiunge il numero del settore al codice
            #{codice}-S{settore}
            df2.loc[dupl.index, 'CODICE'] = [f"{df2['CODICE'][i]}-S{df2['SETTORE'][i]}" for i in dupl.index]

#Ottenere il dataset delle serie dati
ts2 = df2.iloc[:, [2] + [x for x in range(10, len(df2.columns))]].copy()
ts2 = ts2.set_index('CODICE').transpose()
ts2.set_index(pd.date_range('2001-01-01', '2003-04-01', freq = 'MS'), inplace = True)
#Rimuovere codici e caratteri non voluti (trovati con trial and error trasformando in numerico)
ts2.replace(['#', '***', 'xxx'], np.nan, inplace = True)
ts2.replace(['ERRORE DI POZZO', 'in manut.', 'manca'], np.nan, inplace = True)
ts2.replace('asciutto', 0, inplace = True)
ts2.replace('194,9 (*)', 194.9, inplace = True)
ts2.replace('194,8 (*)', 194.8, inplace = True)
#Transforma in valori numerici
for i in range(len(ts2.columns)):
    ts2.iloc[:, i] = pd.to_numeric(ts2.iloc[:, i])
#Ottenere il dataset dei metadata
meta2 = df2.iloc[:, [x for x in range(10)]].set_index('CODICE')
#Il database contiente il livello piezometrico, non è necessario fare ulteriori operazioni

# %% Join dei due dataset

#Join di meta1 e meta2
meta = dw.joincolumns(pd.merge(meta1, meta2, how = 'outer', left_index = True, right_index = True))
colorder = ['COMUNE', 'x', 'y', 'z', 'INFO', 'PROVINCIA', 'STRAT.', 'FALDA', 'SETTORE']
meta = meta[colorder]

#Join di ts1 e ts2
idx = [x in ts1.columns for x in ts2.columns]
tool = ts2.drop(ts2.columns[idx], axis = 1)
ts = pd.merge(ts1, tool, how = 'outer', left_index=True, right_index=True)
tool = ts2.loc[:, idx]
ts = pd.merge(ts, tool, how = 'outer', left_index=True, right_index=True)
ts = dw.joincolumns(ts, '_x', '_y')
ts.index.rename('DATA', inplace = True)

#Modifica dei codici SIF
#I codici SIF hanno uno 0 davanti: va aggiunto
meta.index = [f'0{code}' if (len(code)>6) and (code[0] != 'P') else code for code in meta.index]
meta.index.names = ['CODICE']
ts.columns = [f'0{code}' if (len(code)>6) and (code[0] != 'P') else code for code in ts.columns]

# %% Salvataggio dei dataset ottenuti

meta.to_csv('data/PTUA2003/meta_PTUA2003_TICINOADDA_unfiltered.csv')
ts.to_csv('data/PTUA2003/head_PTUA2003_TICINOADDA_unfiltered.csv')

# %% Operazioni sui dataset completi

#Modifica di meta e serie storiche
#Rimozione piezometri senza coordinate
idx = meta.loc[:, ['x', 'y']].isna().apply(all, 1)
meta = meta.drop(meta.index[idx])
ts = ts.loc[:, ts.columns.isin(meta.index)]
#Rimozione piezometri senza quota
idx = meta.loc[:, 'z'].isna()
meta = meta.drop(meta.index[idx])
ts = ts.loc[:, ts.columns.isin(meta.index)]
#Ricerca piezometri con coordinate duplicate
dup1 = meta1.loc[meta1.duplicated(['x', 'y'], keep = False), :]
dup2 = meta2.loc[meta2.duplicated(['x', 'y'], keep = False), :]
dup = meta.loc[meta.duplicated(['x', 'y'], keep = False), :]
#Rimuovi duplicati
keep = meta.loc[meta.duplicated(['x', 'y']), :]
drop = meta.loc[meta.duplicated(['x', 'y'], keep = 'last'), :]
keep.loc[keep['COMUNE'].isin(['MARIANO COMENSE', 'MARCALLO CON CASONE']), 'FALDA'] = '3'
keep = keep.loc[np.invert(keep.duplicated(['x', 'y'])), :]
meta.loc[keep.index, 'FALDA'] = keep['FALDA']
meta.drop(drop.index, inplace = True)
sum(meta.index.duplicated())

#Separazione dei metadati in falda superficiale e profonda
meta_sup = meta.loc[meta['FALDA'].isin(['1', np.nan, 'SUPERF.', 'SUPERF. (acquifero locale)']), :]
meta_otr = meta.loc[np.invert(meta.index.isin(meta_sup.index)), :]

meta_sup.to_csv('data/PTUA2003/meta_sup_PTUA2003_TICINOADDA.csv')
meta_otr.to_csv('data/PTUA2003/meta_other_PTUA2003_TICINOADDA.csv')
