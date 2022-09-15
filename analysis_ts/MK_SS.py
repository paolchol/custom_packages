# -*- coding: utf-8 -*-
"""
Mann-Kendall test and Sen's slope analysis on the head observations

@author: paolo
"""

# %% Setup

import pandas as pd
import numpy as np
import dataanalysis as da
import dataviz as dv
import matplotlib.pyplot as plt

# %% Load data and metadata

head = pd.read_csv('data/PTUA2022/head_IT03GWBISSAPTA.csv', index_col = 'DATA')
meta = pd.read_csv('data/PTUA2022/metadata_piezometri_ISS.csv')

# %% Select solid time series, remove outliers and fill missing values

cn = da.CheckNA(head)
filtered, removed = cn.filter_col(20, True)
co = da.CheckOutliers(filtered, False)
head_clean = co.remove(skip = ['PO0120750R2020'])
head_fill = head_clean.interpolate('linear', limit = 14)

# %% Perform the Mann-Kendall test and calculate the Sen's slope

confidence = 0.95

db_mk = pd.DataFrame(np.zeros((len(head_fill.columns), 3)), columns = ['z','p','tr'], index = head_fill.columns)
db_slope = pd.DataFrame(np.zeros((len(head_fill.columns), 2)), columns = ['slope', 'intercept'], index = head_fill.columns)

for col in head_fill.columns:
    idx = db_mk.index.isin([col])
    db_mk.loc[idx, 'z'], db_mk.loc[idx, 'p'], db_mk.loc[idx, 'tr'] = da.mann_kendall(head_fill[col].dropna(), confidence)
    db_slope.loc[col, :][0], db_slope.loc[col, :][1], _, _ = da.sen_slope(head_fill[col].dropna())

# db_mk.to_csv('analisi_serie_storiche/res_MK.csv')
# db_slope.to_csv('analisi_serie_storiche/res_sslope.csv')

# %% Calculate a 5-year step Mann-Kendall/Sen's slope

step = 5*12 #5 years * 12 months/year
confidence = 0.95
db_stepmk = da.step_trend(head_fill, step, 'mk', confidence = confidence)
db_stepss = da.step_trend(head_fill, step)

#Visualize a heatmap showing the variation of the sen's slope
fig, ax = plt.subplots(figsize = (6.4, 3.6), dpi = 500)
dv.heatmap_TS(db_stepss, db_stepss.index, db_stepss.columns, step = 1,
               ax = ax, cbarlabel = "Sen's slope (5 year step)",
              rotate = True, aspect = 'auto',
              cmap = plt.get_cmap("viridis_r", 5),
              title = "Sen's slope computed for 5-year steps")
fig.tight_layout()
plt.show()

#For a specific time series
#MERATE
col = meta.loc[meta['COMUNE'] == 'MERATE', 'CODICE'].values[0]
dv.plot_step_sen(head_fill, col, figsize = (6.4, 3.6), dpi = 500)

# %% Visualize the slope overlayed to the time series

for piezo in db_slope.index:
    dv.plot_sen(head_fill, piezo, db_slope)

#For a specific time series
#MERATE
col = meta.loc[meta['COMUNE'] == 'MERATE', 'CODICE'].values[0]
dv.plot_sen(head_fill, col, db_slope)
db_mk.loc[col, :]

#BUSTO GAROLFO
col = meta.loc[meta['COMUNE'] == 'BUSTO GAROLFO', 'CODICE'].values[0]
dv.plot_sen(head_fill, col, db_slope)
db_mk.loc[col, :]

# %% Obtain the Sen's slope as a % of the water table

import geopandas as gpd
import numpy as np
import rasterio

#Load the bottom of the hydrogeological basin
base = rasterio.open("data/soggiacenza_base_ISS/soggiacenza.tif")

#Sample the raster with the osservation points' coordinates (opc)
opc = meta.loc[meta['CODICE'].isin(db_slope.index), ['CODICE', 'X_WGS84', 'Y_WGS84']]
opc.reset_index(drop = True, inplace = True)
coord_list = [(x,y) for x,y in zip(opc['X_WGS84'] , opc['Y_WGS84'])]
opc['value'] = [x for x in base.sample(coord_list)]
opc['value'] = opc.apply(lambda x: x['value'][0], axis = 1)
opc.loc[np.where(opc['value'] < 0)[0], 'value'] = np.nan

#Obtain the bottom also for observation points otside the raster boundaries
# - Gather the nearest value on the non-na raster

#Compute the saturated height

#Normalize sen's slope relatively to the saturated height


# %% Visualize geodata

import geodata as gd
import matplotlib.pyplot as plt

#Visualize the raster (labeling NA values as np.nan)
b = base.read()
bres = np.reshape(b, (b.shape[0]*b.shape[1], b.shape[2]))
bres[bres < 0] = np.nan
gd.plot_raster(base, bres)

#Visualize the points overlayed to the raster
#Transform the piezometer metadata in a geodataframe
opc = meta.loc[meta['CODICE'].isin(db_slope.index), ['CODICE', 'X_WGS84', 'Y_WGS84']]
opc = gpd.GeoDataFrame(opc, geometry = gpd.points_from_xy(opc['X_WGS84'], opc['Y_WGS84']))
fig, ax = plt.subplots()
# transform rasterio plot to real world coords
extent = [base.bounds[0], base.bounds[2], base.bounds[1], base.bounds[3]]
ax = rasterio.plot.show(base, extent=extent, ax=ax, cmap='pink')
opc.plot(ax=ax)

