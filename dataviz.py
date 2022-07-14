# -*- coding: utf-8 -*-
"""
Collection of custom functions for data visualization

author: paolo
"""

from matplotlib import pyplot
import plotly.express as px
from plotly.offline import plot

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