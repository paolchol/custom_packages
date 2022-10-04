# -*- coding: utf-8 -*-
"""
Functions for data wrangling.
As data wrangling I mean:
    - operations on the datasets such as merge and concat
    - rows or columns removals

@author: paolo
"""

import numpy as np
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
        if len(col.split('_')) > 2:
            newcol = ('_').join(col.split('_')[0:-1])
        else:
            newcol = col.split('_')[0]
        pos = df.loc[:, col].isna()
        df.loc[pos, col] = df.loc[pos, f'{newcol}{fillwith}']
        df.drop(columns = f'{newcol}{fillwith}', inplace = True)
        df.rename(columns = {f'{col}': f'{newcol}'}, inplace = True)
    if col_order is not None: df = df[col_order]
    return df

def join_twocols(df, cols, onlyna = True, rename = None, add = False,
                 inplace = False):
    """
    Uses the data in cols[1] to fill the nans in cols[0] (onlyna = True) or 
    to replace the values in cols[0] when an occurrence in cols[1] is found 
    (onlyna = False).

    Parameters
    ----------
    df : pandas.DataFrame
        A dataframe with two columns you want to merge into one.
    cols : list of str
        A list containing the labels of the two columns. The order is important
        and explained in the function's and onlyna descriptions.
    onlyna : bool, optional
        If True, cols[0] nans are filled with cols[1] values in the same position.
        If False, the values in cols[0] are replaced with non-nan values from
        cols[1].
        The default is True.
    rename : str, optional
        Name of the merged column. The default is None.

    Returns
    -------
    df : pandas.DataFrame
        DESCRIPTION.
    """
    if not inplace: df = df.copy()
    if onlyna:
        pos = df.loc[:, cols[0]].isna()
    else:
        pos = df.loc[:, cols[1]].notna()
    vals = df.loc[pos, cols[1]] if not add else df.loc[pos, cols[0]] + '-' + df.loc[pos, cols[1]]
    df.loc[pos, cols[0]] = vals
    df.drop(columns = cols[1], inplace = True)
    if rename is not None: df.rename(columns = {f'{cols[0]}': rename}, inplace = True)
    if not inplace: return df

def join_tworows(df, rows, inplace = False):
    if not inplace: df = df.copy()
    pos = df.loc[rows[0], :].isna()
    df.loc[rows[0], pos] = df.loc[rows[1], pos]
    df.drop(index = rows[1], inplace = True)
    if not inplace: return df

def mergemeta(left, right, link = None,*, firstmerge: dict, secondmerge: dict):
    """
    Merge two metadata databases

    Parameters
    ----------
    left, right : pandas.DataFrame
        Two DataFrames containing metadata.
    link : pandas.DataFrame, optional
        A DataFrame containing codes which link 'right' to 'left'.
        The default is None.
    firstmerge : dict, optional
        A **kwargs argument to provide additional instructions to the
        (optional) merge between 'right' and 'link'.
    secondmerge : dict, optional
        A **kwargs argument to provide additional instructions to the
        merge between 'left' and 'right'.
    
    Returns
    -------
    out : pandas.DataFrame
        A merged DataFrame of 'left' and 'right'. If 'link' is provided, it
        will be used as a link between the two dataframes.

    """
    if link is not None:
        right = pd.merge(right, link, how = 'inner', **firstmerge)
    out = pd.merge(left, right, how = 'left', **secondmerge)
    out.reset_index(inplace = True)
    return out

def mergets(left, right, codes):
    """
    Function to merge two time series dataframes based on associated codes
    provided.
    The merged dataframe is passed to joincolumns to join the duplicated
    columns that pandas.merge will produce.

    Parameters
    ----------
    left : pandas.DataFrame
        Time series dataframe to merge.
    right : pandas.DataFrame
        Time series dataframe to merge.
    codes : pandas.Series
        Series with:
            values: codes associated to the right df
            index: codes associated to the left df, to perform the merge.

    Returns
    -------
    out : pandas.DataFrame
        DataFrame with time series merged.
    """
    y = right[codes]
    y.columns = codes.index
    out = joincolumns(pd.merge(left, y, how = 'outer', left_index = True, right_index = True))
    return out

def remove_wcond(df, cond):
    """
    Removes rows/data from a dataframe by applying a specified condition

    Parameters
    ----------
    df : pandas.DataFrame
        A pandas dataframe.
    cond : -
        Anything that could be a condition. Example: df['x'].notna()

    Returns
    -------
    pandas.DataFrame
        dataframe with the data specified by the condition.
    """
    return df[cond]

def create_datecol(df, d = None, year = None, month = None):
    df = df.copy()
    df[month] = [d[m] for m in df[month]]
    datecol = [f"{x}-{y}-1" for x, y in zip(df[year], df[month])]
    datecol = pd.to_datetime(datecol, format = '%Y-%m-%d')
    return datecol

class stackedDF():
    
    def __init__(self, df, yearcol, d):
        """
        Creation of a stackedDF object

        Parameters
        ----------
        df : pandas.DataFrame
            A "stacked" DataFrame with codes as index, a column indicating
            the year and the other columns indicating the months.
        yearcol : str
            Label of the column in df containing the years.
        d : dict
            A dictionary associating the months in the columns to their
            cardinal number. It can be obtained as:
                d = {month: index for index, month in enumerate(months, start = 1) if month}
                where month is the list containing the months columns labels
        """
        self.df = df
        self.y = yearcol
        self.d = d
    
    def rearrange(self, index_label = None, store = False):
        """
        Rearranges the stackedDF to obtain a simpler date/code dataframe

        Parameters
        ----------
        index_label : str, optional
            The label of the output dataframe's index. The default is None.
        store : bool, optional
            If to store the obtained df inside the object. The default is False.

        Returns
        -------
        tool : pandas.DataFrame
            Re-arranged DataFrame with date as index and codes as columns.
        """
        idx = pd.date_range(f"{min(self.df[self.y])}-01-01", f"{max(self.df[self.y])}-12-01", freq = 'MS')
        tool = pd.DataFrame(np.zeros(len(idx)), index = idx)
        tool.rename(columns = {0: 'tool'}, inplace = True)
        uniquecodes = list(dict.fromkeys(self.df.index.to_list()))
        for code in uniquecodes:
            subset = self.df.loc[code, :]
            if not isinstance(subset, pd.Series):
                s = subset.set_index(self.y).stack(dropna = False)
                s = s.reset_index()
                s['datecol'] = self.create_datecol(s, month = 'level_1')
                s.drop(columns = [self.y, 'level_1'], inplace = True)
                s.sort_values('datecol', inplace = True)
                s.rename(columns = {0: code}, inplace = True)
                s.set_index('datecol', inplace = True)
            else:
                s = self.dealwithseries(subset)
            tool = pd.merge(tool, s, left_index = True, right_index = True, how = 'left')
        tool.drop(columns = 'tool', inplace = True)
        if index_label is not None: tool.index.names = [index_label]
        if store: self.arranged = tool
        return tool
    
    def create_datecol(self, s, month):
        df = s.copy()
        df[month] = [self.d[m] for m in df[month]]
        datecol = [f"{x}-{y}-1" for x, y in zip(df[self.y], df[month])]
        datecol = pd.to_datetime(datecol, format = '%Y-%m-%d')
        return datecol
    
    def dealwithseries(self, subset):
        """
        Single-year codes
        """
        year = subset[self.y]
        subset = subset[1:]
        df = pd.DataFrame(subset)
        df.reset_index(inplace = True)
        df.insert(0, self.y, int(year))
        df['datecol'] = self.create_datecol(df, 'index')
        df.drop(columns = [self.y, 'index'], inplace = True)
        df.set_index('datecol', inplace = True)
        return df

class DBU():
    
    def __init__(self, meta_index = None, ts_index = None):
        self.meta_index = meta_index if meta_index is not None else ['CODICE', 'CODICE']
        self.ts_index = ts_index if ts_index is not None else ['DATA', 'DATA']
    
    def pass_meta(self, first, second, SIF = False):
        self.meta1 = pd.read_csv(first, index_col = self.meta_index[0])
        self.meta2 = pd.read_csv(second, index_col= self.meta_index[1])
        if SIF:
            first['CODICE_SIF'] = [f"0{int(idx)}" if not np.isnan(idx) else np.nan for idx in first['CODICE_SIF']]
    
    def pass_ts(self, first, second):
        self.ts1 = pd.read_csv(first, index_col= self.ts_index[1])
        self.ts2 = pd.read_csv(second, index_col= self.ts_index[1])
    
    def identify_codes(self, codes_db = None, spatial = False):
        pass
    
    def merge_meta(self):
        pass
    
    def merge_ts(self):
        pass

