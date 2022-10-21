# -*- coding: utf-8 -*-
"""
trial for find_nearestcell

@author: paolo
"""



import pandas as pd
import geodata as gd
import geopandas as gpd
import numpy as np
import rasterio

#Load the bottom of the hydrogeological basin
base = rasterio.open("data/soggiacenza_base_ISS/soggiacenza.tif")
meta = pd.read_csv('data/results/db-unification/meta_DBU-COMPLETE.csv', index_col = 'CODICE')

b = base.read()
bres = np.reshape(b, (b.shape[0]*b.shape[1], b.shape[2]))
bres[bres < 0] = np.nan
gd.plot_raster(base, bres)

test = bres[~np.isnan(bres)]

x = np.array([[1,2],[2,3],[3,4]])
mask = [False, False, True]

for row in range(bres.shape[0]):
    



#Sample the raster with the osservation points' coordinates (opc)
# opc = meta.loc[meta['CODICE'].isin(db_slope.index), ['CODICE', 'X_WGS84', 'Y_WGS84']]

opc = meta[['CODICE', 'X_WGS84', 'Y_WGS84']]

opc.reset_index(drop = True, inplace = True)
coord_list = [(x,y) for x,y in zip(opc['X_WGS84'] , opc['Y_WGS84'])]
opc['value'] = [x for x in base.sample(coord_list)]
opc['value'] = opc.apply(lambda x: x['value'][0], axis = 1)
opc.loc[np.where(opc['value'] < 0)[0], 'value'] = np.nan


