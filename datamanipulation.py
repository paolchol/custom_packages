# -*- coding: utf-8 -*-
"""
Functions for dataset manipulation

@author: paolo
"""

import pandas as pd
import numpy as np

def joincolumns(df, keep = '_x', fillwith = '_y', col_order = None):
    """
    Joins the overlapping columns in a merged dataframe.
    It keeps the 'keep' column and fills the nan with the values in 'fillwith'
    column.

    Parameters
    ----------
    df : pandas.DataFrame
        Merged dataframe with overlapping columns identified by a suffix
    keep : string, optional
        Suffix of the columns to use as a base to join the overlapping columns.
        The default is '_x'.
    fillwith : string, optional
        Suffix of the columns from which to take the values to fill the nans
        in the 'keep' columns. The default is 'y'.
    col_order : list, optional
        Order of the columns wanted for the final dataframe. The default is None.
    
    Returns
    -------
    df : pandas.DataFrame
        Dataframe with joined overlapping columns

    """
    idx = [keep in col for col in df.columns]
    # newdf = pd.DataFrame(np.zeros([len(df.index), sum(idx)]),
    #                      columns = [col.split('_')[0] for col in df.columns[idx]])
    
    # for col in df.columns[idx]:
    #     newcol = col.split('_')[0]
    #     newdf[newcol] = df.loc[:, col]
    #     pos = newdf.loc[:, newcol].isna()
    #     newdf.loc[pos, newcol] = df.loc[df.loc[:, col].isna(), f'{newcol}{fillwith}']
    
    # return newdf
    
    for col in df.columns[idx]:
        new_col = col.split('_')[0]
        df[new_col] = df.loc[:, col]
        df.loc[df.loc[:, col].isna(), new_col] = df.loc[df.loc[:, col].isna(), f'{new_col}{fillwith}']
        df.drop([col, f'{new_col}{fillwith}'], axis = 1, inplace = True)
    if col_order: df = df[col_order]
    return df