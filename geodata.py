# -*- coding: utf-8 -*-
"""
Created on Wed Sep 14 10:16:19 2022

@author: paolo
"""


import matplotlib.pyplot as plt
import numpy as np
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

def find_nearestpoint():
    pass