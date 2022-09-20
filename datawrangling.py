# -*- coding: utf-8 -*-
"""
Functions for dataset wrangling
For data wrangling I mean:
    - operations on the datasets such as merge and concat
    - rows or columns removals

@author: paolo
"""

import pandas as pd

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
    for col in df.columns[idx]:
        newcol = col.split('_')[0]
        pos = df.loc[:, col].isna()
        df.loc[pos, col] = df.loc[pos, f'{newcol}{fillwith}']
        df.drop(f'{newcol}{fillwith}', axis = 1, inplace = True)
        df.rename(columns = {f'{col}': f'{newcol}'}, inplace = True)
    if col_order: df = df[col_order]
    return df

def mergehead(left, right, codes):
    """
    Function to merge two time series dataframes based on the codes each piezometer
    has in each 
    """
    y = right[codes]
    y.columns = codes.index
    out = joincolumns(pd.merge(left, y, how = 'outer', left_index = True, right_index = True))
    return(out)

def remove_wcond(df, cond):
    """
    Removes rows/data from a dataframe by applying a specified condition

    Parameters
    ----------
    df : pandas.DataFrame
        A pandas dataframe.
    cond : TYPE
        anything that could be a condition. Example: df['x'].notna()

    Returns
    -------
    pandas.DataFrame
        dataframe with the data specified by the condition.

    """
    return df[cond]