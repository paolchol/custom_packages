# -*- coding: utf-8 -*-
"""
Functions for dataset manipulation
For data manipulation I mean:
    - operations on the datasets such as merge and concat
    - rows or columns removals

@author: paolo
"""

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