# -*- coding: utf-8 -*-
"""
Visualizations of the DBU database

@author: paolo
"""
# %% Setup

import dataanalysis as da
import dataviz as dv
import datawrangling as dw
import geodata as gd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# %% Carica dati

meta = pd.read_csv('data/results/db-unification/meta_DBU-COMPLETE.csv', index_col = 'CODICE')
meta['CODICE_SIF'] = [f"0{int(idx)}" if not np.isnan(idx) else np.nan for idx in meta['CODICE_SIF']]
head = pd.read_csv('data/results/db-unification/head_DBU-COMPLETE.csv', index_col = 'DATA')
rprt = pd.read_csv('data/results/db-unification/report_merge_DBU-COMPLETE.csv', index_col = 'CODICE')

# %% Visualizza serie aggiunte e ampliate

idx = meta['ORIGINE'] != 'PTUA2022'
sel = meta.index[idx]
ts = head.loc[:, head.columns.isin(sel)]

#Visualizza con il codice come etichetta
dv.interactive_TS_visualization(ts, xlab = 'Data', ylab = 'Livello piezometrico [m s.l.m.]',
                                file = 'plot/dbu/added_enhanced_DBU-COMPLETE.html',
                                markers = True, title = "Serie aggiunte o ampliate nell'aggregazione dei database - Non processate")
#Visualizza con il comune come etichetta
ts.columns = dw.enum_instances(meta.loc[ts.columns, 'COMUNE'], ['MILANO']) #dai valore univoco ai comuni
dv.interactive_TS_visualization(ts, xlab = 'Data', ylab = 'Livello piezometrico [m s.l.m.]',
                                file = 'plot/dbu/added_enhanced_DBU-COMPLETE_COMUNE.html',
                                markers = True, title = "Serie aggiunte o ampliate nell'aggregazione dei database - Non processate")

# %% Visualizza tutto il database

#Visualizza con il comune come etichetta
meta.loc[head.columns, 'COMUNE']

#Visualizza il database dopo averlo pre-processato
#--pre-processing

#--visualizzazione

# %% Mappa

viz = meta.loc[meta['BACINO_WISE'] == 'IT03GWBISSAPTA', :].copy().reset_index()

gd.show_mappoints(meta.reset_index(), 'lat', 'lon',
                  file = 'plot/dbu/map_DBU-COMPLETE.html',
                  scatter = dict(color = 'ORIGINE',
                                 hover_name = 'CODICE'),
                  
                  layout = dict(mapbox_style = "stamen-terrain",
                                mapbox_zoom = 7,
                                mapbox_center_lat = meta['lat'].mean(), mapbox_center_lon = meta['lon'].mean(),
                                margin = {"r":0,"t":0,"l":0,"b":0}),
                  
                  traces = dict(marker_size = 20,
                                opacity = 0.7,
                                ids = ['CODICE', 'COMUNE']
                                )
                  )

# %% Istogramma con lunghezza serie

#calcolare numero e percentuale di serie storiche aggiunte
# grafico a barre/istogramma: lunghezza delle serie in anni

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
plt.text(40, 22, f"Numero di serie storiche: {tool.shape[0]}")
plt.legend(loc = 'upper right')
plt.savefig('plot/dbu/hist_lunghezza.png')
plt.show()

#Visualizzazione alternativa:
fig = plt.figure()
ax = plt.subplot(111)
ax.hist(tool, bins = 'auto', histtype = 'barstacked',
         label = labels)
box = ax.get_position()
ax.set_position([box.x0, box.y0 + box.height * 0.1,
                 box.width, box.height * 0.9])
ax.legend(loc='upper center', bbox_to_anchor = (0.5, 1.1),
          fancybox = False, shadow = True, ncol = 2)

plt.show()

# %% Visualizza serie singole

# Ricerca per comune
comuni = ['OSNAGO', 'MEZZAGO']
dv.interactive_TS_visualization(head[meta.loc[meta['COMUNE'].isin(comuni), :].index], markers = True)

# %% Trials

#Map
gd.show_mappoints_std(viz, 'lat', 'lon', zoom = 9, file = 'trash/viz_trial.html', color = 'ORIGINE', hover_name = 'CODICE')

gd.show_mappoints(viz, 'lat', 'lon',
                        file = 'trash/viz_trial_.html',
                        scatter = dict(color = 'ORIGINE',
                                       hover_name = 'CODICE'),
                        
                        layout = dict(mapbox_style = "stamen-terrain",
                                      mapbox_zoom = 9,
                                      mapbox_center_lat = viz['lat'].mean(), mapbox_center_lon = viz['lon'].mean(),
                                      margin = {"r":0,"t":0,"l":0,"b":0}),
                        
                        traces = dict(marker_size = 20,
                                      opacity = 0.7
                                      # ,
                                      # hovertext = 'COMUNE'
                                      )
                        )
