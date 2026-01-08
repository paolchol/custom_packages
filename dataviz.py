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

# %% Utilities

def set_res(res):
    """
    Set plot resolution
    """
    matplotlib.rcParams['figure.dpi'] = res

def cm2inch(*tupl):
    """
    Transforms centrimeters to inches
    """
    inch = 2.54
    if isinstance(tupl[0], tuple):
        return tuple(i/inch for i in tupl[0])
    else:
        return tuple(i/inch for i in tupl)
    
def rgb2hex(tup):
    """
    tup: tuple, list or array of int, float or str
        (r, g, b)
    """
    r = int(tup[0])
    g = int(tup[1])
    b = int(tup[2])
    return "#{:02x}{:02x}{:02x}".format(r,g,b)

# %% General plot

def fast_boxplot(df):
    df.boxplot()

def fast_TS_visualization(df, bbox_to_anchor = (1.15, 0.85), cmap = 'viridis',
                          ret = False, **kwargs):
    cmap = matplotlib.colormaps[cmap]
    colors = cmap(np.linspace(0, 1, len(df.columns)))

    # handles, labels = [], []
    fig, axes = plt.subplots(len(df.columns), 1, **kwargs)
    for i, column in enumerate(df.columns, start = 0):
        # plt.subplot(len(df.columns), 1, i)
        axes[i].plot(df.index, df[column].values, color = colors[i], label = column)
        axes[i].set_xlim(df.index[0], df.index[-1])
        if i < len(df.columns)-1:
            axes[i].set_xticklabels('')
        h, l = axes[i].get_legend_handles_labels()
    #     handles.append(h)
    #     labels.append(l)
    # fig.legend(handles, labels, bbox_to_anchor = bbox_to_anchor)
    plt.figlegend(bbox_to_anchor = bbox_to_anchor)
    
    if ret:
        return fig, axes
    else:
        plt.show()

def interactive_TS_visualization(df, xlab = 'X', ylab = 'Y', file = 'temp.html',
                                 plottype = 'line', legend_title = "Variables",
                                 markers = False, ret = False, **kwargs):
    """
    Function to interactively plot a pandas.DataFrame
    Needs plotly and plotly.express

    df: pandas.DataFrame
        The DataFrame to plot
    xlab, ylab: string, optional
        The x and y axes labels. Default is X, Y
    file: string, optional
        The name of the output .html file containing the plot.
        Default is temp.html
    plottype: string, optional
        If == line, plots a line plot, otherwise a scatterplot.
        Default is line
    markers: bool, optional
        If True, plots markers in the line plot. Default is False
    ret: bool, optional
        If True, returns a plotly.express.line/scatter and doesn't save a .html file.
        Default is False
    kwargs: dictionary
        Additional parameters to be passed to plotly.express.line/scatter.update_layout

    Returns
    none or plotly.express.line/scatter
    """
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

def annotated_heatmap(data, cbar_label = 'value', x_labels = None, y_labels = None,
                      textcolor = 'w', **kwargs):
    if x_labels is None:
        x_labels = data.columns
    if y_labels is None:
        y_labels = data.index

    fig, ax = plt.subplots(1,1, figsize = (10,10), dpi = 300)

    # Create image
    im = ax.imshow(data, **kwargs)

    # Create colorbar
    cbar = ax.figure.colorbar(im, ax = ax)
    cbar.ax.set_ylabel(cbar_label, rotation=-90, va = "bottom")

    # Show all ticks and label them with the respective list entries
    ax.set_xticks(range(len(x_labels)), labels=x_labels,
                  rotation=45, ha="right", rotation_mode="anchor")
    ax.set_yticks(range(len(y_labels)), labels=y_labels)

    # Loop over data dimensions and create text annotations.
    for i in range(len(y_labels)):
        for j in range(len(x_labels)):
            text = ax.text(j, i, round(data.iloc[i, j],2),
                        ha="center", va="center", color=textcolor)
    
    return fig, ax

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
