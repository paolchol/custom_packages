# -*- coding: utf-8 -*-
"""
Collection of custom functions for basic data analysis

Sections:
    - Outlier detection and rejection
    - Missing data detection
    - Mann-Kedall test and Sen's slope
    - General operations on dataframes

author: paolo
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as st

# %% Outlier detection and rejection

class CheckOutliers():
    """
    Class to perform outliers imputation and removal

    Attributes
    ------------------------------
    df: pandas.DataFrame
        DataFrame containing time series as columns
    output: pandas.DataFrame
        Dataframe summarizing number and percentage of outliers for each column
    outliers: dict
        Dictionary containing the indexes of outliers for each df column

    Methods
    -------
    count(self, printinfo, saveoutliers):
        Counts the number of outliers
    remove(self, fill = np.nan, skip = [], upperonly = False,
            loweronly = False, keepchanges = False, ret = False):
        Removes the identified outliers, providing options to decide which ones
    plot_outliers(self, column, ret = False):
        Plots df's column values along with its identified outliers
    plot_bar():

    """

    def __init__(self, df, printinfo = True, inplace = False, saveoutliers = False, method = 'IQR'):
        """
        df: pandas.DataFrame
            DataFrame containing time series as columns
        printinfo: bool, optional
            If True, prints the count of outliers for each column. Default is True
        inplace: bool, optional
            If False, a copy of df is created to avoid making changes in the original df. Default is False 
        saveoutliers: bool, optional.
            If True, a list containing the indexes of the outliers is created and saved.
        """
        if inplace:
            self.df = df
        else:
            self.df = df.copy()
        self.count(printinfo, saveoutliers, method)
        self.df_plot = self.df.copy()
    
    def count(self, printinfo, saveoutliers, method):
        """
        Counts the number of outliers

        Creates a pandas.DataFrame containing it.
        The outliers are identified through 1.5*IQR (Inter-Quantile Range).

        printinfo: bool
            If True, prints the count of outliers and their percentage in the time series.
            __init__ sets this to True as default.
        saveoutliers: bool
            If True, will save the position of outliers in the df.
            __init__ will set this to False as default.
        method: str
            Options: IQR, 3std
            If IQR, it will identify outliers as values above/below 1.5*IQR
            If 3std, it will identify outliers as values above/below 3*std
            __init__ will set this to IQR as default.
        
        Generates:
        self.output: pandas.DataFrame
            Dataframe summarizing number and percentage of outliers for each column.
        self.outliers:
            Dictionary with columns labels as keys containing the indexes of the
            identified outliers.
            If saveoutliers is True.
        """
        df = self.df
        if saveoutliers:
            self.outliers = {}
        self.output = pd.DataFrame()
        for column in df.columns:
            if not df[column].isnull().all():
                if method == 'IQR':
                    Q1 = np.nanpercentile(df[column], 25)
                    Q3 = np.nanpercentile(df[column], 75)
                    IQR = Q3 - Q1
                    upper_limit = Q3 + 1.5*IQR
                    lower_limit = Q1 - 1.5*IQR
                elif method == '3std':
                    std = np.nanstd(df[column])
                    upper_limit = 3*std
                    lower_limit = -3*std
                else:
                    print('Invalid method chosen. Available methods are: IQR, 3std')
                    return

                self.output = pd.concat([self.output,
                                        pd.DataFrame([column,
                                        sum(df[column] > upper_limit) + sum(df[column] < lower_limit),
                                        sum(df[column] > upper_limit),
                                        sum(df[column] < lower_limit),
                                        ((sum(df[column] > upper_limit) + sum(df[column] < lower_limit))/len(df[column]))*100]).transpose()])
            else:
                self.output = pd.concat([self.output, pd.DataFrame([column, np.nan, np.nan, np.nan, np.nan]).transpose()])
            if printinfo:
                print(f'Column: {column}')
                print(f'Number of upper outliers: {sum(df[column] > upper_limit)}')
                print(f'Number of lower outliers: {sum(df[column] < lower_limit)}')
                print(f'Percentage of outliers: {((sum(df[column] > upper_limit) + sum(df[column] < lower_limit))/len(df[column]))*100}')
            if saveoutliers:
                if sum(df[column] > upper_limit) > 0 or sum(df[column] < lower_limit) > 0:
                    self.outliers[column] = df.loc[df[column] > upper_limit, :].index.to_list() +\
                                            df.loc[df[column] < lower_limit, :].index.to_list()
        self.output.columns = ['ID', 'n_outlier', 'n_outlier_up', 'n_outlier_lw', 'perc_outlier']
        self.output.reset_index(inplace=True, drop=True)
    
    def remove(self, method = 'IQR', fill = np.nan, skip = [], upperonly = False, loweronly = False,
               keepchanges = False, ret = False, idxintervals = None):
        """
        Remove the outliers present in the df provided

        method: str, optional
            Options: IQR, 3std
            If IQR, it will identify outliers as values above/below 1.5*IQR
            If 3std, it will identify outliers as values above/below 3*std
            Default is IQR
        fill: inst, float, str, optional
            The value with which to fill in inplace of the outliers. Default is numpy.nan
        skip: str, list of str
            Labels of columns to skip in the outlier removal
        upperonly: bool, optional
            If True, remove only the upper outliers, i.e. values above the upper threshold (Q75 + 1.5*IQR).
            Default is False.
        loweronly: bool, optional
            If True, remove only the lower outliers, i.e. values above the lower threshold (Q25 - 1.5*IQR).
            Default is False.
        keepchanges: bool, optional
            If True, CheckOutliers.df will be modified, thus "keeping the changes" made by this module.
            Otherwise, it will not be changed. Default is False.
        ret: bool, optional
            If True, it will return CheckOutliers.df with the outliers removed by this module.
            Default is False.
        
        Returns:
        output: pandas.DataFrame
            The original df in input to the class with removed outliers.
            Returns only if ret is True.
        """
        if keepchanges:
            output = self.df
        else:
            output = self.df.copy()
        for column in self.df.columns:
            if column not in skip:
                if method == 'IQR':
                    Q1 = np.nanpercentile(output[column], 25)
                    Q3 = np.nanpercentile(output[column], 75)
                    IQR = Q3 - Q1
                    upper_limit = Q3 + 1.5*IQR
                    lower_limit = Q1 - 1.5*IQR
                elif method == '3std':
                    std = np.nanstd(output[column])
                    upper_limit = 3*std
                    lower_limit = -3*std
                else:
                    print('Invalid method chosen. Available methods are: IQR, 3std')
                if idxintervals is not None and column in idxintervals.keys():
                    if not upperonly: output.loc[(self.df[column] < lower_limit) & (self.df.index > idxintervals[column][0]) & (self.df.index < idxintervals[column][1]), column] = fill
                    if not loweronly: output.loc[(self.df[column] > upper_limit) & (self.df.index > idxintervals[column][0]) & (self.df.index < idxintervals[column][1]), column] = fill
                else:
                    if not upperonly: output.loc[self.df[column] < lower_limit, column] = fill
                    if not loweronly: output.loc[self.df[column] > upper_limit, column] = fill
        if ret:
            return output
        elif not keepchanges:
            self.removed = output
    
    def plot_outliers(self, column, ret = False):
        """
        Plots df's column values along with its identified outliers

        column: str
            The label of the df's column to plot
        ret: bool, optional
            If True, returns fig, ax for further customization
        """
        if column in [*self.outliers]:
            fig, ax = plt.subplots(figsize = (10,5))
            ax.plot(self.df_plot.loc[:, column], marker = '.', color = '#3782BD',
                    label = column, linestyle = '-', alpha = 0.5)
            ax.plot(self.df_plot.loc[self.outliers[column], column], marker = 'o',
                    color = '#CB8EC8', label = 'Identified outliers', linestyle = '', alpha = 0.5,
                    markersize = 10)
            ax.legend(fancybox = False, frameon = False)
            if ret:
                return fig, ax
        else:
            print("This column has no outliers, use another function to plot its values")

    def plot_bar(self, label = 'perc_outlier', **kwargs):
        """
        Plot the percentage of outliers in each column

        label: str, optional
            Column label of the self.output df to be plotted 
        kwargs: optional
            Additional parameters for matplotlib.axes.bar
        """
        _, ax = plt.subplots(figsize=(self.df.shape[1]//5, 5))
        ax.bar(self.output['ID'], self.output[label], width = 1, **kwargs)
        ax.set_xlabel('Outlier percentage [%]')
        plt.xticks(rotation=90)
        plt.tight_layout()
    
    def plot_boxplot(self, column, upperonly = False, loweronly = False):
        #plot series boxplot with outliers highlighted
        #plot boxplot
        pass

# %% Missing data detection

class CheckNA():
    
    def __init__(self, df, threshold = 10, printinfo = True):
        self.df = df.copy()
        self.check(threshold, printinfo)
        
    def check(self, threshold, printinfo):
        count = 0
        self.output = pd.DataFrame(np.zeros((len(self.df.columns), 2)), columns = ['ID', 'perc_NA'])
        fvi = self.df.apply(pd.Series.first_valid_index, axis = 0)
        for i, column in enumerate(self.df.columns):            
            perc_NA = round(self.df.loc[fvi[column]:, column].isna().sum()/len(self.df.loc[fvi[column]:, column]), 3)*100
            if printinfo: print(f'The column "{column}" has this percentage of NAs:\n{perc_NA}')
            if perc_NA > threshold:
                count = count + 1
            self.output.loc[i, 'ID'] = column
            self.output.loc[i, 'perc_NA'] = perc_NA
        if printinfo:
            print(f'There are {count} columns which have more than {threshold}% of missing values')
            print('Call self.output to access the NA percentage dataframe')
    
    def filter_col(self, threshold = 10, fvicond = False):
        self.filtered = self.df.copy()
        if fvicond: fvi = self.df.apply(pd.Series.first_valid_index, axis = 0)
        NAs = pd.DataFrame(index = self.df.columns, columns = ['NA_perc', 'Removed'])
        for i, column in enumerate(self.df.columns, start = 0):
            #Percentage of NAs over the period
            if fvicond: 
                NAs.iloc[i,0] = round(self.df.loc[fvi[column]:, column].isna().sum()/len(self.df.loc[fvi[column]:, column]), 3)*100
            else:
                NAs.iloc[i,0] = round(self.df[column].isna().sum()/len(self.df[column]), 3)*100
            if NAs.iloc[i,0] > threshold:
                self.filtered.drop(columns = column, inplace = True)
                NAs.iloc[i,1] = True  
            else:
                NAs.iloc[i,1] = False
        return self.filtered, NAs
    
    def fill_NA(self, method = 'ffill', subset = None,
                get_first_valid_index = False, **kwargs):
        '''
        Fills the NA in the dataframe

        method: str, optional
            Available options: ffill, bfill, interpolate, else
            If else, you can specify additional
            parameters to pandas.DataFrame.fillna() through kwargs
            Default is ffill
        subset: str, list of str, optional
            A single label or multiple labels from df columns to which
            to perform the filling
        get_first_valid_index: bool, optional
            If True, the values before the first valid index in the original
            df are set to nan also in the resulting df
            Default is False
        kwargs: dict, optional
            Parameters to pandas.DataFrame.fillna()
            To provide a filling through a mooving average, provide the following:
            value = df.rolling(4, 1).mean()
            (check https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.rolling.html)
            You may want to then interpolate the results using:
            df.interpolate(method = 'linear')

        Returns
        out: pandas.DataFrame
            df filled. Subset of original df if subset is provided
        '''
        if subset is not None:
            out = self.df.loc[:, subset].copy()
        else:
            out = self.df.copy()
        if method == 'ffill':
            out = out.ffill()
        elif method == 'bfill':
            out = out.bfill()
        else:
            out = out.fillna(**kwargs)
        
        if get_first_valid_index:
            cols = self.df.columns if subset is None else subset
            for col in cols:
                fvd = self.df[col].first_valid_index()
                out.loc[:fvd, col] = np.nan

        return out



# %% Mann-Kendall test and Sen's slope estimation

def mann_kendall(vals, confidence = 0.95):
    #source: https://github.com/manaruchi/MannKendall_Sen_Rainfall
    
    n = len(vals)
    box = np.ones((len(vals), len(vals)))
    box = box * 5
    sumval = 0
    for r in range(len(vals)):
        for c in range(len(vals)):
            if(r > c):
                if(vals[r] > vals[c]):
                    box[r,c] = 1
                    sumval = sumval + 1
                elif(vals[r] < vals[c]):
                    box[r,c] = -1
                    sumval = sumval - 1
                else:
                    box[r,c] = 0
    
    freq = 0
    #Lets calculate frequency now
    tp = np.unique(vals, return_counts = True)
    for tpx in range(len(tp[0])):
        if(tp[1][tpx]>1):
            tp1 = tp[1][tpx]
            sev = tp1 * (tp1 - 1) * (2 * tp1 + 5)
            freq = freq + sev
        
    se = ((n * (n-1) * (2 * n + 5) - freq) / 18.0) ** 0.5
    
    #Lets calc the z value
    if(sumval > 0):
        z = (sumval - 1) / se
    else:
        z = (sumval + 1) / se
    
    #lets see the p value
    
    p = 2 * st.norm.cdf(-abs(z))
    
    #trend type
    if(p<(1-confidence) and z < 0):
        tr_type = -1
    elif(p<(1-confidence) and z > 0):
        tr_type = +1
    else:
        tr_type = 0
    
    return z, p, tr_type

def sen_slope(vals, confidence = 0.95, scipy = True):
    #source: https://github.com/manaruchi/MannKendall_Sen_Rainfall
    
    if scipy: return st.mstats.theilslopes(vals)
    #this returns 4 values, not 3
    
    alpha = 1 - confidence
    n = len(vals)
    
    box = np.ones((len(vals), len(vals)))
    box = box * 5
    boxlist = []
    
    for r in range(len(vals)):
        for c in range(len(vals)):
            if(r > c):
                box[r,c] = (vals[r] - vals[c]) / (r-c)
                boxlist.append((vals[r] - vals[c]) / (r-c))
    freq = 0
    #Lets caluclate frequency now
    tp = np.unique(vals, return_counts = True)
    for tpx in range(len(tp[0])):
        if(tp[1][tpx]>1):
            tp1 = tp[1][tpx]
            sev = tp1 * (tp1 - 1) * (2 * tp1 + 5)
            freq = freq + sev
        
    se = ((n * (n-1) * (2 * n + 5) - freq) / 18.0) ** 0.5
    
    #lets find K value
    k = st.norm.ppf(1-(alpha/2)) * se
    
    slope = np.median(boxlist)
    return slope, k, se

def step_trend(df, step, output = 'ss', dropna = True, **kwargs):
    """
    Parameters
    ----------
    df : pandas.DataFrame
    step : int
        step in which compute the sen's slope each
        time. needs to be in the unit of the df index
    stat : str
        ss: Sen's slope
        mk: Mann-Kendall test
    dropna : boolean
        remove the na from the columns passed to the sen's slope
        function
    """
    ncol = round(len(df.index)/step)
    db = pd.DataFrame(np.zeros((len(df.columns), ncol)),
                            columns = [f'{output}{i}' for i in range(1, ncol+1)],
                            index = df.columns)
    db[:] = np.nan
    for col in df.columns:
        series = df[col].dropna() if dropna else df[col]
        # if len(series) >= 2*step:
        start, end = 0, 0
        for n in range(round(len(series)/step)):
            end = step*(n+1) if step*(n+1) < len(series) else len(series)
            if output == 'ss':
                db.loc[db.index.isin([col]), f'{output}{n+1}'], _, _, _ = sen_slope(series[start:end])
            elif output == 'mk':
                _, _, db.loc[db.index.isin([col]), f'{output}{n+1}'] = mann_kendall(series[start:end], **kwargs)
            start = end
    return db

# %% Groundwater-specific operations

def correct_quota(meta, ts, metacorr, codes, quotacols, printval = False):
    """
    Correct the time series which have been measured at a different quota 
    with respect to a correct quota, providing two metadata datasets.

    Parameters
    ----------
    meta : pandas.DataFrame
        Metadata of the time series to be corrected.
    ts : pandas.DataFrame
        DataFrame containing the time series to be corrected. The columns
        names are the series' codes.
    metacorr : pandas.DataFrame
        Metadata of the correct time series.
    codes : pandas.Series
        Series containing the corresponding couples of codes in the two metadata
        dataframes.
        Series with:
            values: codes associated to meta
            index: codes associated to metacorr
    printval : bool, optional
        If True, prints the values of the quota in the two dataframes. The 
        default is False.
    
    Returns
    -------
    tscorr : pandas.DataFrame
        DataFrame containing the time series corrected.
    """
    tscorr = ts.copy()
    for code in codes.index:
        if meta.loc[codes[code], quotacols[0]] != metacorr.loc[code, quotacols[1]]:
            sogg = meta.loc[codes[code], quotacols[0]] - ts[codes[code]]
            tscorr[codes[code]] = metacorr.loc[code, quotacols[1]] - sogg
            if printval:
                print(code)
                print('meta: ' + str(meta.loc[codes[code], quotacols[0]]))
                print('metacorr: ' + str(metacorr.loc[code, quotacols[1]]))
    return tscorr

# %% Data operations

def operation_xperiods(df, col, xperiods, function = sum,
                       includep = True):
    """
    Perform an operation on a variable over a specified number of periods
    The default operation is the sum

    df: pandas.DataFrame
        the dataframe for which to compute the sum of x periods
    col: 
        the df column from which to extract the variable to sum
    xperiods: int
        the number of periods to sum, *including* the period at the line where it will be computed.
        to avoid this, set "includep" as False
    function: function, optional
        Default: sum function
    includep: bool, optional
        Default: True

    Returns:
    sumx: list
        List of float or int containing the sum over the x periods
    """
    sumx = []
    if includep:
        xperiods = xperiods - 1
    df_copy = df.reset_index().copy()
    for row in df_copy.iterrows():
        if row[0] > xperiods:
            if includep:
                sumx.append(function(df_copy[col][row[0]-xperiods:row[0]+1]))
            else:
                sumx.append(function(df_copy[col][row[0]-xperiods:row[0]]))
        else:
            sumx.append(np.nan)
    return sumx

# %% General operations

def print_row(df, row, cond = True):
    for col in df.columns:
        if cond:
            print(f'{col}: {df.loc[row, col].values[0]}')
        else:
            # print(f'{np.where(df.columns == col)[0][0]}')
            print(f'{col}: {df.iloc[row, np.where(df.columns == col)[0][0]]}')    
            
def ts_sel_date(df, meta = None, sttime = None, entime = None, delta = None):
    """
    Select time series from a DataFrame based on the starting and ending
    dates

    Parameters
    ----------
    df : pandas.DataFrame
        DESCRIPTION.
    meta : pandas.Series, list or array, optional
        A selection of columns (associated to time series) in df. The default
        is None.
    sttime : str, optional
        DESCRIPTION. The default is None.
    entime : str, optional
        DESCRIPTION. The default is None.
    delta : int, optional
        If provided, the . The default is None.

    Returns
    -------
    sel : list
        List containing the time series DataFrame column labels of the time
        series respecting the conditions provided.
    """
    sel = []
    if (sttime is not None) & (entime is not None):
        sttime, entime = pd.to_datetime(sttime), pd.to_datetime(entime)
    cols = meta if meta is not None else df.columns
    for ts in cols:
        start = df.index[df[ts].notna()][0]
        end = df.index[df[ts].notna()][-1]
        if (sttime is not None) & (entime is not None):
            if (start < sttime) & (end > entime):
                sel += [ts]
        else:
            dt = end - start
            if dt.days >= delta:
                sel += [ts]
    return sel