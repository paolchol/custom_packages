# -*- coding: utf-8 -*-
"""
Created on Wed Sep 14 10:16:19 2022

@author: paolo
"""


import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyproj
import rasterio

# %% Visualization

def plot_raster(raster, values = None):
    if values is None:
        v = raster.read()
        values = np.reshape(v, (v.shape[0]*v.shape[1], v.shape[2]))
        print('ok')
    fig, ax = plt.subplots(1, 1)
    base = plt.imshow(values)
    image = rasterio.plot.show(raster, ax = ax)
    fig.colorbar(base, ax = ax)
    plt.show()

# %% Operations on coordinates

def transf_CRS(x, y, frm, to, series = False, **kwargs):
    """
    Transforms coordinates from one CRS to another

    Parameters
    ----------
    x : scalar or array
        x coordinate (longitude).
    y : scalar or array
        y coordinate (latitude).
    frm : Any
        The CRS of the coordinates provided.
        It can be in any format to indicate the CRS used in pyproj.Trasformer.from_crs.
        Example: 'EPSG:4326'
    to : Any
        The CRS in which to transform the coordinates provided.
        It can be in any format to indicate the CRS used in pyproj.Trasformer.from_crs.
        Example: 'EPSG:4326'.
    series : bool, optional
        If True, x and y are treated as pandas.Series and transformed into arrays.
        The default is False.

    Returns
    -------
    out : tuple
        out[0] contains the LATITUDE
        out[1] contains the LONGITUDE

    """
    if series:
        x = x.reset_index(drop = True).to_numpy()
        y = y.reset_index(drop = True).to_numpy()
    trs = pyproj.Transformer.from_crs(frm, to)
    out = trs.transform(x, y, **kwargs)
    return out
    

# %% Find nearest things

def find_nearestrastercell(raster, point):
    x0, y0 = raster.bounds[0], raster.bounds[1] #lower left x, y ; upper right x, y
    x1, y1 = raster.bounds[2], raster.bounds[3]
    
    if point.x < x0:
        pass
    elif point.x > x0:
        pass
    
    
    point.x
    point.y
        
    pass

def find_nearestpoint(db1, db2, id1 = 'CODE', coord1 = ['lon', 'lat'],
                       id2 = 'CODE', coord2 = ['lon', 'lat'],
                       reset_index = False, change_CRS = False, ellps = 'WGS84',
                       **kwargs):
    """
    Obtains the nearest point from db2 relative to each point in db1. Returns
    a dataframe gatheirng this information

    Parameters
    ----------
    db1 : TYPE
        DESCRIPTION.
    db2 : TYPE
        DESCRIPTION.
    id1 : TYPE, optional
        DESCRIPTION. The default is 'CODE'.
    coord1 : TYPE, optional
        DESCRIPTION. The default is ['lon', 'lat'].
    id2 : TYPE, optional
        DESCRIPTION. The default is 'CODE'.
    coord2 : TYPE, optional
        DESCRIPTION. The default is ['lon', 'lat'].
    reset_index : TYPE, optional
        DESCRIPTION. The default is False.
    change_CRS : TYPE, optional
        DESCRIPTION. The default is False.
    ellps : TYPE, optional
        DESCRIPTION. The default is 'WGS84'.
    **kwargs : TYPE
        DESCRIPTION.

    Returns
    -------
    dbout : TYPE
        DESCRIPTION.

    """
    
    if reset_index:
        db1 = db1.copy().reset_index()
        db2 = db2.copy().reset_index()
    if change_CRS:
        out = transf_CRS(db1.loc[:, coord1[0]], db1.loc[:, coord1[1]], series = True, **kwargs)
        db1.loc[:, coord1[0]], db1.loc[:, coord1[1]] = out[1], out[0]
        out = transf_CRS(db2.loc[:, coord2[0]], db2.loc[:, coord2[0]], series = True, **kwargs)
        db2.loc[:, coord2[0]], db2.loc[:, coord2[1]] = out[1], out[0]
    
    dbout = db1.loc[:, [id1, coord1[0], coord1[1]]].copy()
    nrstcol = [f'{id2}_nrst', f'{coord2[0]}_nrst', f'{coord2[1]}_nrst']
    dbout[nrstcol[0]], dbout[nrstcol[1]], dbout[nrstcol[2]] = [np.nan, np.nan, np.nan]
    dbout['dist'] = np.nan
    geod = pyproj.Geod(ellps = ellps)#, **kwargs)
    
    for p in db1.loc[:, [id1, coord1[0], coord1[1]]].iterrows():
        dist = []
        for a in db2.loc[:, [id2, coord2[0], coord2[1]]].iterrows():
            _, _, d = geod.inv(p[1][coord1[0]], p[1][coord1[1]], a[1][coord2[0]], a[1][coord2[1]])
            dist.append(d) #d: distance in meters
        idx = dist.index(min(dist))        
        lst = iter([id2, coord2[0], coord2[1]])
        for col in nrstcol:
            dbout.loc[dbout[id1] == p[1][id1], col] = db2.iloc[idx, :][next(lst)]
        dbout.loc[dbout[id1] == p[1][id1], 'dist'] = dist[idx]
    return dbout











