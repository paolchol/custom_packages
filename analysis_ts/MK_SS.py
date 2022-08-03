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

import rasterio
from rasterio.plot import show
import geopandas as gpd

#Load the bottom of the hydrogeological basin
base = rasterio.open("data/soggiacenza_base_ISS/soggiacenza.tif")

gdf = meta.loc[meta['CODICE'].isin(db_slope.index), ['CODICE', 'X_WGS84', 'Y_WGS84', 'PROFONDITA']]
coord_list = [(x,y) for x,y in zip(gdf['X_WGS84'] , gdf['Y_WGS84'])]
gdf['value'] = [x for x in base.sample(coord_list)]

file_name = 'data/soggiacenza_base_ISS/soggiacenza.tif'
with rasterio.open(file_name) as src:
     band1 = src.read(1)
     print('Band1 has shape', band1.shape)
     height = band1.shape[0]
     width = band1.shape[1]
     cols, rows = np.meshgrid(np.arange(width), np.arange(height))
     xs, ys = rasterio.transform.xy(src.transform, rows, cols)
     lons= np.array(xs)
     lats = np.array(ys)
     print('lons shape', lons.shape)

#obtain the closest point from the raster to the one in gdf
#obtain the raster value of the closest point
#assign it to the point in the gdf
#compute the saturated height

#Visualize the points overlayed to the raster
#Transform the piezometer metadata in a geodataframe
gdf = meta.loc[meta['CODICE'].isin(db_slope.index), ['CODICE', 'X_WGS84', 'Y_WGS84']]
gdf = gpd.GeoDataFrame(gdf, geometry = gpd.points_from_xy(gdf['X_WGS84'], gdf['Y_WGS84']))
fig, ax = plt.subplots()
# transform rasterio plot to real world coords
extent = [base.bounds[0], base.bounds[2], base.bounds[1], base.bounds[3]]
ax = rasterio.plot.show(base, extent=extent, ax=ax, cmap='pink')
gdf.plot(ax=ax)

# %% Compare two methods of sen's slope computation

confidence = 0.95

import scipy.stats as st

for col in head_fill.columns:
    _, _, tr_type = da.mann_kendall(head_fill[col].dropna(), confidence)
    slope, _, _ = da.sen_slope(head_fill[col].dropna(), confidence, scipy = False)
    slopesc, _, _, _ = st.mstats.theilslopes(head_fill[col].dropna())
    print(f"{col}")
    print(f"Mann-Kendall: {tr_type}")
    print(f"Sen's slope: {slope}")
    print(f"Sen's slope (scipy): {slopesc}")
