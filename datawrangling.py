# -*- coding: utf-8 -*-
"""
Functions for data wrangling.
Some functionalities:
    - operations on the datasets such as merge and concat
    - rows or columns removals

@author: paolo
"""

import numpy as np
import pandas as pd

# %% Merge operations and utility

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
        df.loc[pos, col] = df.loc[pos, f"{newcol}{fillwith}"]
        df.drop(columns = f"{newcol}{fillwith}", inplace = True)
        df.rename(columns = {f"{col}": f"{newcol}"}, inplace = True)
    if col_order is not None: df = df[col_order]
    return df

def join_twocols(df, cols, onlyna = True, rename = None, add = False,
                 inplace = False, sep = '-', drop = True):
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
    add : 
        
    inplace :
        
    sep : str, optional
        Separator between the merged values in the final column. The default is
        '-'.
    drop :
    
    Returns
    -------
    df : pandas.DataFrame
        DESCRIPTION.
    """
    def itsnan(num):
        return num != num
    if not inplace: df = df.copy()
    if onlyna:
        pos = df.loc[:, cols[0]].isna()
    else:
        pos = df.loc[:, cols[1]].notna()
    if add:
        vals = [f"{y}" if itsnan(x) else f"{x}{sep}{y}" for x, y in zip(df.loc[pos, cols[0]], df.loc[pos, cols[1]])]
    else:
        vals = df.loc[pos, cols[1]]
    df.loc[pos, cols[0]] = vals
    if drop: df.drop(columns = cols[1], inplace = True)
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

def mergets(left, right, codes, report = False, tag = None):
    """
    Function to merge two time series dataframes based on associated codes
    provided.

    The merge operated is an 'outer' join, meaning it will use union of keys
    from both frames. The resulting dataframe will then also have columns which
    were present in only one of the two dataframes.
    
    The merged dataframe is passed to joincolumns to join the duplicated
    columns that pandas.merge will produce.

    Parameters
    ----------
    left : pandas.DataFrame
        Time series dataframe to merge.
    right : pandas.DataFrame
        Time series dataframe to merge.
    codes : pandas.Series or str
        Series with:
            values: codes associated to the right df
            index: codes associated to the left df, to perform the merge.
        If it is a single code, insert it as a string.
    report : bool, optional
        If report = True, a report is returned containing the codes of the 
        merged time series along with the starting and ending dates of the added
        ts. The default is False.

    Returns
    -------
    out : pandas.DataFrame
        DataFrame with time series merged.
    """
    y = right[codes]
    if isinstance(codes, pd.Series): y.columns = codes.index
    out = joincolumns(pd.merge(left, y, how = 'outer', left_index = True, right_index = True))
    if report:
        rprt = pd.DataFrame(y.columns)
        rprt['start'] = [y[col].first_valid_index().date() for col in y.columns]
        rprt['end'] = [y[col].last_valid_index().date() for col in y.columns]
        if tag is not None:
            rprt['tag'] = tag
        return out, rprt
    return out

def merge_rprt(left, right):
    """
    Merge two "rprt" objects (reports) generated from the function mergets.
    If some codes are in both reports it adds their values in a unique column
    with values separated by '/'.

    Parameters
    ----------
    left, right : pandas.DataFrame
        DataFrames in the structure of 'rprt' from mergets.

    Returns
    -------
    out : pandas.DataFrame
        Merged dataframe from left and right.
    """
    if sum(right.index.isin(left.index)) > 0:
        out = pd.merge(left, right, how = 'outer', left_index = True, right_index = True)
        out = join_twocols(out, ['tag_x', 'tag_y'], onlyna = False, add = True, rename = 'tag', sep ='/')
        out = join_twocols(out, ['start_x', 'start_y'], onlyna = False, add = True, rename = 'start', sep = '/')
        out = join_twocols(out, ['end_x', 'end_y'], onlyna = False, add = True, rename = 'end', sep = '/')
    else:
        out = pd.concat([left, right])
    return out
    
# %% General operations

def create_datecol(df, d = None, year = None, month = None):
    df = df.copy()
    df[month] = [d[m] for m in df[month]]
    datecol = [f"{x}-{y}-1" for x, y in zip(df[year], df[month])]
    datecol = pd.to_datetime(datecol, format = '%Y-%m-%d')
    return datecol

def enum_instances(lst, check = None, start = 1):
    """
    Returns a list where all instances in 'lst' which are present in 'check'
    are enumerated with a progressive number

    Parameters
    ----------
    lst : list, array or Index
        A list, array or Index with instances to be enumerated.
    check : list
        A list containing one or more values.
    start : int, optional
        The starting number from which to count. The default is 1.

    Returns
    -------
    new : list
        A list where all instances which are present in 'check'
        are enumerated with a progressive number.
    """
    new = []
    st = (start, 'null')
    
    if check is None:
        #trova i duplicati in lst e crea una lista di valori con duplicati
        
        newlist = [] # empty list to hold unique elements from the list
        check = [] # empty list to hold the duplicate elements from the list
        for i in lst:
            if i not in newlist:
                newlist.append(i)
            else:
                check.append(i)
    check = list(dict.fromkeys(check))
    for c in check:
        start = st[0]
        for lab in lst:
            if lab == c:
                new += [f'{lab}-{start}']
                start = start + 1
            elif (lab not in new) & (lab not in check):
                new += [lab]
    return new

def datecol_arrange(datecol):
    dates = []
    for date in datecol:
        if date == date:
            s = date.split('/')
            s.reverse()
            dates += ['-'.join(s)]
        else:
            dates += [np.nan]
    return dates

def print_colN(df):
    for i, col in enumerate(df.columns):
        print(f"{i}: {col}")

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

# %% stackedDF: class for stacked dataframe management

class stackedDF():
    """
    Creation of a stackedDF object

    Parameters
    ----------
    df : pandas.DataFrame
        A "stacked" DataFrame.
    dftype : sts
        A string indicating "df"' structure. It can be:
            - monthscols: 
                The data is organized with codes as index, a column
                indicating the year and 12 columns indicating the value
                each month.
            - daterows:
                The data is organized with codes as index, a column 
                indicating the date and a column indicating the values in 
                each date.
        The default is "monthscols".
    yearcol : str
        Label of the column in df containing the years. Needed for dftype
        "monthscols". The default is None.
    datecol : str
        Label of the column in df containing the date. Needed for dftype
        "daterows". The default is None.
    d : dict, only needed for dftype "monthscols"
        A dictionary associating the months in the columns to their
        cardinal number. It can be obtained as:
            d = {month: index for index, month in enumerate(months, start = 1) if month}
            where month is the list containing the months columns labels
    """
    def __init__(self, df, dftype = 'monthscols', yearcol = None,
                 datecol = None, d = None):        
        self.df = df.copy()
        self.dt = dftype
        self.y = yearcol
        self.dc = datecol
        if (yearcol is None) & (datecol is None):
            print('ERROR: You need to provide one between yearcol and datecol.\
                  Refer to the documentation to learn which one you need.')
            return
        if (dftype == 'monthscols') & (d is None):
            print("ERROR: d is necessary when dftype is 'monthscols'")
        self.d = d
    
    #Methods
    #-------
    
    def rearrange(self, index_label = None, store = False, setdate = False,
                  resample = True, rule = '1MS', *, dateargs = dict(), pivotargs = dict()):
        """
        Rearranges the stackedDF to obtain a simpler date/code dataframe

        Parameters
        ----------
        index_label : str, optional
            The label of the output dataframe's index. The default is None.
        store : bool, optional
            If to store the obtained df inside the object. The default is False.
        setdate : bool, optional
            If to transform df's date column as DateTime. Only useful for dftype 
            "daterows" when the date column isn't already a DateTime object.
            The default is False.
        rule : DateOffset, Timedelta or str, optional
            The offset string or object representing target conversion in 
            pandas.DataFrame.resample(). The default is "1MS".
        
        **dateargs : dict, optional
            Optional arguments to provide to pandas.to_datetime. Example: to 
            specify a specific date format. Only useful for dftype "daterows".
        **pivotargs : dict, optional
            Arguments to pass to pandas.DataFrame.pivot_table(). Needed for dftype 
            "daterows".
        
        Returns
        -------
        tool : pandas.DataFrame
            Re-arranged DataFrame with date as index and codes as columns.
        """
        if self.dt == 'monthscols':
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
        elif self.dt == 'daterows':
            if setdate: self.df[self.dc] = pd.to_datetime(self.df[self.dc], **dateargs)
            tool = self.df.reset_index(self.df.index.names).copy()
            tool.set_index(self.dc, inplace = True)
            tool = tool.pivot_table(index = self.dc, **pivotargs)
            if resample: tool = tool.resample(rule).mean()
        else:
            print("Invalid 'dftype' provided when creating the object")
            return
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

# %% From meta and ts to a single dataframe

class arrange_metats():
    """
    Joins two dataframes ('meta' and 'ts') in a single dataframe
    
    Parameters for __init__
    -----------------------
    meta : pandas.DataFrame
        A DataFrame with rows containing the metadata of the time series 
        contained in 'ts'. 'meta' and 'ts' are linked through 'ts' column labels,
        stored in column 'idcol' in 'meta'.
    ts : pandas.DataFrame
        A DataFrame with columns containing the time series which metadata are
        contained in 'meta'.
    idcol : str
        The label of the column in meta containing the IDs used for ts columns
        labels.    
    """
    def __init__(self, meta, ts, idcol):
        self.meta = meta.copy()
        self.ts = ts.copy()
        self.id = idcol
    
    #Methods
    #-------
    
    def to_webgis(self, anfields, ancouples, pzfields = None, pzcouples = None, idcol = None,
                  ids = None, stacklab = None, onlymeta = False):
        """
        Returns the database in a format which can be uploaded in a WebGIS

        Parameters
        ----------
        anfields : str or list of str
             Labels for the final metadata DataFrame associated with the time series.
        ancouples : dict
            Dictionary containing the labels from the original metadata DataFrame
            ('meta' in __init__) corresponding to the final metadata DataFrame.
        tsfields : string or list of string
            Same as 'metafields' but relative to the final time series DataFrame.
        tscouples : dict
            Same as 'metacouples' but linking 'ts' in __init__ and the final
            time serie DataFrame.
        idcol : str
            Label of the column containing the unique id of the point in the
            future dataframes.
        ids : str or list of str, optional
            Labels for progressive numerical index columns. The default is None.
        stacklab : str or list of str, optional
            Label to associate to the resulting stacked dataframe columns.
            The default is None.
        onlymeta : bool
            If you only want to consider anfields and ancouples. The default is False
        
        Returns
        -------
        meta : pandas.DataFrame
            Metadata dataframe acting as a registry for the time series in 'ts',
            in a format which can then be uploaded in a desired WebGIS.
        ts : pandas.DataFrame
            Time series dataframe in in a format which can then be uploaded in
            a desired WebGIS. Linked to 'meta' through the 'idcol' label.
        """
        # an - Anagrafica (metadata)
        an = pd.DataFrame(np.zeros((self.meta.shape[0],len(anfields))), columns = anfields)
        an[:] = np.nan
        for tag in ancouples:
            an[tag] = self.meta[ancouples[tag]]
        if ids is not None:
            an[ids[0]] = [x for x in range(1, an.shape[0]+1)]
        # dpz - Piezometric data
        if not onlymeta:
            dpz = self.ts.stack().reset_index(drop = False)
            if stacklab is not None:
                dpz.columns = stacklab
            dump = self.meta.loc[self.meta[self.id].isin(self.ts.columns), :].copy()
            dump.reset_index(drop = True, inplace = True)
            tool = pd.DataFrame(np.zeros((dump.shape[0],len(pzfields))), columns = pzfields)
            tool[:] = np.nan
            for tag in pzcouples:
                tool[tag] = dump[pzcouples[tag]]
            if ids is not None:
                tool[ids[1]] = an.loc[an[idcol].isin(tool[idcol]), ids[0]].values        
            dpz = joincolumns(pd.merge(dpz, tool, how = 'right', left_on = idcol, right_on = idcol))
            if ids is not None:
                dpz[ids[0]] = [x for x in range(1, dpz.shape[0]+1)]
            dpz = dpz[pzfields]
            return an, dpz
        return an
    
    def to_stackeDF(self):
        #transform to a format passable to the class stackeDF
        pass

# %% Work in progress

class DBU():
    """
    Work in progress
    """
    
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

