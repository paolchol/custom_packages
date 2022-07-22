# -*- coding: utf-8 -*-
"""
Collection of custom functions for data visualization

author: paolo
"""

import pandas as pd
from matplotlib import pyplot
import plotly.express as px
from plotly.offline import plot
import matplotlib.pyplot as plt
import numpy as np

def fast_TS_visualization(df):
    pyplot.figure()
    for i, column in enumerate(df.columns, start = 1):
    	pyplot.subplot(len(df.columns), 1, i)
    	pyplot.plot(df.index, df[column].values)
    	pyplot.title(column, y = 0.5, loc = 'right')
    pyplot.show()

def interactive_TS_visualization(df, xlab = 'X', ylab = 'Y', file = 'temp.html'):
    figure = px.line(df)
    figure.update_layout(
        xaxis_title = xlab,
        yaxis_title = ylab,
        legend_title = "Variables"
        )
    plot(figure, filename = file)

def fast_boxplot(df):
    df.boxplot()

# %% Plot SGI

def plot_SGI(series, figsize = (6.4, 3.6), dpi = 500, dropna = True):    
    sgi = series.dropna() if dropna else series
    fig, ax = plt.subplots(figsize = figsize, dpi = dpi)
    sgi.plot(color = "k")
    ax.axhline(0, linestyle="--", color = "k")
    droughts = sgi.to_numpy(copy = True)
    droughts[droughts > 0] = 0
    ax.fill_between(sgi.index, 0, droughts, color = "C0")
    ax.set_title(series.name)

def heatmap_TS(data, row_labels, col_labels, step, ax = None, title = None,
            cbar_kw = {}, cbarlabel = "", white = False, rotate = False,
            labelsize = 8, **kwargs):
    """
    Create a heatmap from a numpy array and two lists of labels.

    Parameters
    ----------
    data
        A 2D numpy array of shape (M, N).
    row_labels
        A list or array of length M with the labels for the rows.
    col_labels
        A list or array of length N with the labels for the columns.
    ax
        A `matplotlib.axes.Axes` instance to which the heatmap is plotted.  If
        not provided, use current axes or create a new one.  Optional.
    cbar_kw
        A dictionary with arguments to `matplotlib.Figure.colorbar`.  Optional.
    cbarlabel
        The label for the colorbar.  Optional.
    **kwargs
        All other arguments are forwarded to `imshow`.
    """

    if not ax:
        ax = plt.gca()

    # Plot the heatmap
    im = ax.imshow(data, **kwargs)
    
    # Create colorbar
    cbar = ax.figure.colorbar(im, ax = ax, **cbar_kw)
    cbar.ax.set_ylabel(cbarlabel, rotation=-90, va = "bottom")

    # Show all ticks and label them with the respective list entries.
    ax.set_xticks(np.arange(0, data.shape[1], step), labels = col_labels)
    ax.set_yticks(np.arange(data.shape[0]), labels = row_labels)
    ax.tick_params(labelsize = labelsize)
    # Let the horizontal axes labeling appear on top.
    # ax.tick_params(top = True, bottom = False,
    #                labeltop = True, labelbottom = False)
    # Rotate the tick labels and set their alignment.
    if rotate:
        plt.setp(ax.get_xticklabels(), rotation = 30, ha = "right",
        rotation_mode = "anchor")

    # Turn spines off and create white grid.
    if white:
        ax.spines[:].set_visible(False)    
        ax.set_xticks(np.arange(data.shape[1]+1)-.5, minor=True)
        ax.set_yticks(np.arange(data.shape[0]+1)-.5, minor=True)
        ax.grid(which="minor", color="w", linestyle='-', linewidth=3)
        ax.tick_params(which="minor", bottom=False, left=False)
    
    if title:
        ax.set_title(title)
    
    return im, cbar

# %% Plot Sen's slope

def plot_sen(df, piezo, db_slope, step = 12, figsize = (6.4, 3.6), dpi = 500):
    fig, ax = plt.subplots(figsize = figsize, dpi = dpi)
    ax.plot(df[piezo].dropna())
    ax.plot(df[piezo].dropna().index, db_slope.loc[piezo, 'intercept'] + db_slope.loc[piezo, 'slope'] * np.array([i for i in range(len(df[piezo].dropna().index))]), 'r-')
    ax.set_xticks(np.arange(0, len(df[piezo].dropna()), step), labels = [df.index[i] for i in np.arange(0, len(df[piezo].dropna()), step)])
    ax.set_title(piezo)
    plt.setp(ax.get_xticklabels(), rotation = 30, ha = "right",
    rotation_mode = "anchor")