# -*- coding: utf-8 -*-
"""
Collection of custom functions for data visualization

author: paolo
"""

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
from plotly.offline import plot

# %% Set plot resolution

def set_res(res):
    matplotlib.rcParams['figure.dpi'] = res

# %% General plot

def fast_boxplot(df):
    df.boxplot()

def fast_TS_visualization(df):
    plt.figure()
    for i, column in enumerate(df.columns, start = 1):
        plt.subplot(len(df.columns), 1, i)
        plt.plot(df.index, df[column].values)
        plt.title(column, y = 0.5, loc = 'right')
    plt.show()

def interactive_TS_visualization(df, xlab = 'X', ylab = 'Y', file = 'temp.html',
                                 plottype = 'line', legend_title = "Variables",
                                 markers = False, ret = False, **kwargs):
    if plottype == 'line':
        figure = px.line(df, markers = markers)
    else:
        figure = px.scatter(df)
    figure.update_layout(
        xaxis_title = xlab,
        yaxis_title = ylab,
        legend_title = legend_title,
        **kwargs
        )
    if ret:
        return figure
    else:
        plot(figure, filename = file)

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
    data : numpy.ndarray
        A 2D numpy array of shape (M, N).
    row_labels : list or array of str
        A list or array of length M with the labels for the rows.
    col_labels : list or array of str
        A list or array of length N with the labels for the columns.
    ax : matplotlib.axes.Axes, optional
        A `matplotlib.axes.Axes` instance to which the heatmap is plotted.  If
        not provided, use current axes or create a new one. The default is None.
        
    title :    
    
    cbar_kw : dict, optional
        A dictionary with arguments to `matplotlib.Figure.colorbar`.
    cbarlabel : str, optional
        The label for the colorbar. The deafult is "".
        
    white :
        
    rotate :
    
    labelsize : 
       
    
    **kwargs :
        All other arguments are forwarded to `imshow`.
    """

    if ax is None:
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
    
    if title is not None:
        ax.set_title(title)
    
    return im, cbar

# %% Plot Sen's slope

def plot_sen(df, piezo, db_slope, pltstep = 12, figsize = (6.4, 3.6), dpi = 500):
    fig, ax = plt.subplots(figsize = figsize, dpi = dpi)
    ax.plot(df[piezo].dropna())
    ax.plot(df[piezo].dropna().index, db_slope.loc[piezo, 'intercept'] + db_slope.loc[piezo, 'slope'] * np.array([i for i in range(len(df[piezo].dropna().index))]), 'r-')
    ax.set_xticks(np.arange(0, len(df[piezo].dropna()), pltstep), labels = [df[piezo].dropna().index[i] for i in np.arange(0, len(df[piezo].dropna()), pltstep)])
    ax.set_title(piezo)
    plt.setp(ax.get_xticklabels(), rotation = 30, ha = "right",
    rotation_mode = "anchor")
    
def plot_step_sen(df, piezo, step = 5*12, pltstep = 12, **kwargs):
    import dataanalysis as da
    
    series = df[piezo].dropna()
    fig, ax = plt.subplots(**kwargs)
    ax.plot(series)
    start, end = 0, 0
    for n in range(round(len(series)/step)):
        end = step*(n+1) if step*(n+1) < len(series) else len(series)
        m, q, _, _ = da.sen_slope(series[start:end])
        ax.plot(series[start:end].index, q + m*np.array([i for i in range(len(series[start:end].index))]), 'r-')
        start = end    
    ax.set_xticks(np.arange(0, len(series), pltstep), labels = [series.index[i] for i in np.arange(0, len(series), pltstep)])
    ax.set_title(piezo)
    plt.setp(ax.get_xticklabels(), rotation = 30, ha = "right",
    rotation_mode = "anchor")

# %% SSA supporting functions

def plot_Wcorr_Wzomm(SSA_object, name, L, num = 0):
    if(num == 0):
        SSA_object.plot_wcorr()
        plt.title(f"W-Correlation for {name} - window size {L}")
    else:
        SSA_object.plot_wcorr(max = num)
        plt.title(f"W-Correlation for {name} - window size {L} \n- Zoomed at the first {num + 1} components")

def plot_SSA_results(SSA_object, Fs, noise = None, file = 'SSA_temp.html',
                     tags = None, alpha = 1, over = None,
                     # final = False,
                     # label = 'SSA results', 
                     # xlab = "Date", ylab = "Water table level [MAMSL]",
                     **kwargs):
    
    #import plotly.graph_objs as go
    
    df = pd.DataFrame({'Original': SSA_object.orig_TS.values})
    df.index = SSA_object.orig_TS.index
    if noise:
        df['Noise'] = SSA_object.reconstruct(noise).values
    if tags:
        for i, F in enumerate(Fs):
            tag = tags[i]
            df[tag] = SSA_object.reconstruct(F).values
    else:
        for i, F in enumerate(Fs):
            tag = f'F{i}'
            df[tag] = SSA_object.reconstruct(F).values
    if over:
        for o in over:
            df[o] = df[o] + df['Original'].mean()        
    # if final: 
    #     names = ['Trend', 'Periodicity']
    #     for i, F in enumerate(Fs):
    #         name = names[i]
    #         df[name] = SSA_object.reconstruct(F).values
    # else:
    #     for i, F in enumerate(Fs):
    #         name = f'F{i}'
    #         df[name] = SSA_object.reconstruct(F).values
    #Would be nicer to have the original series with a bit of transparency
    #Also to add labels to the axis and a title
    # plt.title(label)
    # plt.xlabel("Date")
    # plt.ylabel("Level [MASL - Meters Above Sea Level]")
    # Also save it with a name instead of temp-plot, and in a specified path
    figure = px.line(df)
    figure.update_traces(opacity = alpha)
    figure.update_layout(**kwargs)
        # xaxis_title = xlab,
        # yaxis_title = ylab,
        # legend_title = "Variables"
        # )
    plot(figure, filename = file)
    # return(df)
