# -*- coding: utf-8 -*-
"""
Collection of functions which operate with spatial/georeferenced data

@author: paolo
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
from plotly.offline import plot
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
    
def show_mappoints(df, lat, lon, file = 'temp_map.html', zoom = 5,
                         *, scatter = None, layout = None, traces = None):
    """
    Plots a map with points corresponding to df's rows

    Parameters
    ----------
    df : TYPE
        DESCRIPTION.
    lat : TYPE
        DESCRIPTION.
    lon : TYPE
        DESCRIPTION.
    file : TYPE, optional
        DESCRIPTION. The default is 'temp_map.html'.
    
    **kwargs:
    scatter : dict, optional
        **kwargs for the plotly.express.scatter_mapbox function. Function
        documentation: https://plotly.com/python/reference/scattermapbox/
        The default is None.
    layout : dict, optional
        **kwargs for the fig.update_layout function. The default is None.
    traces : dic, optional
        **kwargs for the fig.update_traces function. The default is None.
    """
    if scatter is None:
        fig = px.scatter_mapbox(df, lat, lon)
    else:
        fig = px.scatter_mapbox(df, lat, lon, **scatter)
    if layout is None:
        ctrlat = df[lat].mean() if isinstance(df[lat], pd.Series) else None
        ctrlon = df[lon].mean() if isinstance(df[lon], pd.Series) else None
        #cercare standard value fi mapbox_center_lat e modificare None
        fig.update_layout(
            mapbox_style = "stamen-terrain",
            mapbox_zoom = zoom,
            mapbox_center_lat = ctrlat, mapbox_center_lon = ctrlon,
            margin = {"r":0,"t":0,"l":0,"b":0}
            )
    else:
        fig.update_layout(**layout)
    if traces is None:
        fig.update_traces(
            marker_size = 20,
            opacity = 0.7
            )
    else:
        fig.update_traces(**traces)
    plot(fig, filename = file)

def show_mappoints_std(df, lat, lon, file = 'temp_map.html', zoom = 6, **kwargs):
    """
    Standardized version of show_mappoints

    Parameters
    ----------
    df : TYPE
        DESCRIPTION.
    lat : TYPE
        DESCRIPTION.
    lon : TYPE
        DESCRIPTION.
    file : TYPE, optional
        DESCRIPTION. The default is 'temp_map.html'.
    **kwargs : TYPE
        DESCRIPTION.
    """
    ctrlat = df[lat].mean() if isinstance(df[lat], pd.Series) else None
    ctrlon = df[lon].mean() if isinstance(df[lon], pd.Series) else None
    fig = px.scatter_mapbox(df, lat, lon, **kwargs)
    fig.update_layout(
        mapbox_style = "stamen-terrain",
        mapbox_zoom = zoom,
        mapbox_center_lat = ctrlat, mapbox_center_lon = ctrlon,
        margin = {"r":0,"t":0,"l":0,"b":0}
        )
    fig.update_traces(
        marker_size = 20,
        opacity = 0.7
        )
    plot(fig, filename = file)

# %% Operations on coordinates

def transf_CRS(x, y, frm, to, series = False, **kwargs):
    """
    Transforms coordinates from one CRS to another

    Parameters
    ----------
    x : scalar or array
        x coordinate (latitude).
    y : scalar or array
        y coordinate (longitude).
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
        When transforming to WGS84:
         - out[0] contains the LATITUDE or X
         - out[1] contains the LONGITUDE or Y
    """
    if series:
        x = x.reset_index(drop = True).to_numpy()
        y = y.reset_index(drop = True).to_numpy()
    trs = pyproj.Transformer.from_crs(frm, to)
    out = trs.transform(x, y, **kwargs)
    return out

# %% Find nearest things

def find_nearestrastercell(raster, point):
    
    
            
    pass

def find_nearestpoint(df1, df2, id1 = 'CODE', coord1 = ['lon', 'lat'],
                       id2 = 'CODE', coord2 = ['lon', 'lat'],
                       reset_index = False, change_CRS = False, ellps = 'WGS84',
                       **kwargs):
    """
    Obtains the nearest point from df2 relative to each point in df1. Returns
    a dataframe gatheirng this information

    Parameters
    ----------
    df1 : pandas.DataFrame
        Dataframe containing the id and coordinates of the points to be
        associated to the nearest point present in df2.
    df2 : pandas.DataFrame
        Dataframe containing the id and coordinates of the points in which to
        search for the nearest point to each one from df1.
    id1, id2 : str, optional
        Column label of the dataframes' column containing the points' ids.
        The default is 'CODE'.
    coord1, coord2 : list of str, optional
        Column labels of the dataframes' column containing the points'
        coordinates. The default is ['lon', 'lat'].
    reset_index : bool, optional
        True: reset the index of the dataframes provided (only inside the function).
        Useful if you have the ids in the df index but you don't want to change
        the original df. The default is False.
    change_CRS : bool, optional
        True: changes the CRS of the coordinates. Needs also informations
        about the CRS transformation, to be provided as **kwargs.
        The default is False.
    ellps : str, optional
        Ellipsoid definition to be passed to pyproj.Geod. The default is 'WGS84'.
    **kwargs : TYPE
        Arguments compatible with gd.transf_CRS() and pyproj.Transformer.transform.

    Returns
    -------
    dbout : pandas.DataFrame
        Dataframe containing the ids and coordinates of all the points in df1
        along with the ids and coordinates of the nearest point from df2. The
        last column ('dist') contains the distance between the points, in meters.
    """
    if reset_index:
        df1 = df1.copy().reset_index()
        df2 = df2.copy().reset_index()
    if change_CRS:
        out = transf_CRS(df1.loc[:, coord1[0]], df1.loc[:, coord1[1]], series = True, **kwargs)
        df1.loc[:, coord1[0]], df1.loc[:, coord1[1]] = out[1], out[0]
        out = transf_CRS(df2.loc[:, coord2[0]], df2.loc[:, coord2[0]], series = True, **kwargs)
        df2.loc[:, coord2[0]], df2.loc[:, coord2[1]] = out[1], out[0]
    
    dbout = df1.loc[:, [id1, coord1[0], coord1[1]]].copy()
    nrstcol = [f'{id2}_nrst', f'{coord2[0]}_nrst', f'{coord2[1]}_nrst']
    dbout[nrstcol[0]], dbout[nrstcol[1]], dbout[nrstcol[2]] = [np.nan, np.nan, np.nan]
    dbout['dist'] = np.nan
    geod = pyproj.Geod(ellps = ellps)#, **kwargs)
    
    for p in df1.loc[:, [id1, coord1[0], coord1[1]]].iterrows():
        dist = []
        for a in df2.loc[:, [id2, coord2[0], coord2[1]]].iterrows():
            _, _, d = geod.inv(p[1][coord1[0]], p[1][coord1[1]], a[1][coord2[0]], a[1][coord2[1]])
            dist.append(d) #d: distance in meters
        idx = dist.index(min(dist))        
        lst = iter([id2, coord2[0], coord2[1]])
        for col in nrstcol:
            dbout.loc[dbout[id1] == p[1][id1], col] = df2.iloc[idx, :][next(lst)]
        dbout.loc[dbout[id1] == p[1][id1], 'dist'] = dist[idx]
    return dbout
