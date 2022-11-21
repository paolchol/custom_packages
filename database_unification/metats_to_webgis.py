# -*- coding: utf-8 -*-
"""
Trials to test class join_metats saved in datawrangling

@author: paolo
"""

# %% Setup, load

import datawrangling as dw
import geodata as gd
import numpy as np
import pandas as pd

meta = pd.read_csv('data/results/db-unification/meta_DBU-COMPLETE.csv', index_col = 'CODICE')
meta['CODICE_SIF'] = [f"0{int(idx)}" if not np.isnan(idx) else np.nan for idx in meta['CODICE_SIF']]
head = pd.read_csv('data/results/db-unification/head_DBU-COMPLETE.csv', index_col = 'DATA')
headcorr = pd.read_csv('data/results/db-unification/headcorr_DBU-COMPLETE.csv', index_col = 'DATA')

meta.reset_index(drop = False, inplace = True)

# %% Trasforma in formato WebGIS

metafields = ['gid','id_punto','id_originale','id_ente',
            'tipo_punto','id_acquifero','id_hydros','presenza_strat',
            'stratigrafia_pdf','istat_comune','istat_prov',
            'x_sr1','y_sr1','x_sr2','y_sr2','quota_testa_tubo',
            'nota_coordinate','quota_piano_campagna',
            'fonte_quota_piano_campagna','indirizzo_punto',
            'ente_gestore','proprieta'	,'indirizzo_proprieta']
metacouples = {
    'id_punto': 'CODICE',
    'id_ente': 'CODICE_SIF',
    'tipo_punto': 'TIPO',
    'istat_comune': 'COMUNE',
    'istat_prov': 'PROVINCIA',
    'x_sr2': 'X',
    'y_sr2': 'Y',
    'quota_testa_tubo': 'QUOTA_MISU',
    'quota_piano_campagna': 'QUOTA_PC_S',
    'fonte': 'ORIGINE',
    'bacino_idro': 'BACINO_WISE',
    'note': 'INFO'   
    }
#dizionario, associa alle etichette anfields etichette in meta
#se una etichetta di anfields non è presente, lasciare la colonna in anagrafica vuota

tsfields = ['gid','id_punto','fkid','data','codice_campagna',
            'secco','prodotto','spessore_prodotto','quota_falda','soggiacenza',
            'quota_ref','riferimento_soggiacenza','fonte','note']
tscouples = {
    'id_punto': 'CODICE',
    'quota_ref': 'QUOTA_MISU',
    'fonte': 'ORIGINE'    
    }
#dizionario, associa alle etichette pzfields etichette in meta
stacklab = ['data', 'id_punto', 'quota_falda']
#etichette per il database dopo lo "stack"

j = dw.arrange_metats(meta, head, 'CODICE')
an, dpz = j.to_webgis(metafields, metacouples, tsfields, tscouples, 'id_punto',
                      ['gid', 'fkid'], stacklab)

#dati da inserire a posteriori
#anagrafica
# - x_sr1, y_sr1
an['x_sr1'], an['y_sr1'] = gd.transf_CRS(an['x_sr2'], an['y_sr2'], 'EPSG:32632', 'EPSG:3003', series = True)

#dati_piez
# - secco
# - riferimento_soggiacenza
dpz['secco'] = 'no'
dpz['riferimento_soggiacenza'] = 'non noto'

#serie storiche corrette
jcorr = dw.arrange_metats(meta, headcorr, 'CODICE')
_, dpzcorr = jcorr.to_webgis(metafields, metacouples, tsfields, tscouples,
                             'id_punto', ['gid', 'fkid'], stacklab)
dpzcorr['secco'] = 'no'
dpzcorr['riferimento_soggiacenza'] = 'non noto'

# %% Esporta

an.to_csv('data/results/webgis/anagrafica_punti.csv', index = False)
dpz.to_csv('data/results/webgis/dati_piez_nonusare.csv', index = False)
dpzcorr.to_csv('data/results/webgis/dati_piez.csv', index = False)