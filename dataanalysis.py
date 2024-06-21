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
    
    def __init__(self, df, printinfo = True, inplace = False, saveoutliers = False):
        """
        df: pandas.DataFrame
            DataFrame containing time series as columns
        printinfo: bool, optional
            If True, prints the count of outliers for each column. Default is True
        inplace: bool, optional
            If False, a copy of df is created to avoid making changes in the original df. Default is False 
        saveoutliers: bool, optional
            If True, a list containing the indexes of the outliers is created and saved.
        """
        if inplace:
            self.df = df
        else:
            self.df = df.copy()
        self.count(printinfo, saveoutliers)
        self.df_plot = self.df.copy()
    
    def count(self, printinfo, saveoutliers):
        df = self.df
        # if saveoutliers:
        # return the "positions" of the outliers,
        # the index basically, and their values
        # self.outliers = pd.DataFrame()
        # self.outliers_list
        self.output = pd.DataFrame()
        for i, column in enumerate(df.columns):
            if not df[column].isnull().all():
                Q1 = np.nanpercentile(df[column], 25)
                Q3 = np.nanpercentile(df[column], 75)
                IQR = Q3 - Q1
                upper_limit = Q3 + 1.5*IQR
                lower_limit = Q1 - 1.5*IQR

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
            # if save_outliers:
                # salva l'index come una lista
                # crea un dictionary di liste
                # outliers_list = {'code': column,
                # 'lower_outliers': df.loc[df[column] < lower_limit, column].index}
                # 'upper_outliers': df.loc[df[column] > upper_limit, column].index}
                # pass
        self.output.columns = ['ID', 'n_outlier', 'n_outlier_up', 'n_outlier_lw', 'perc_outlier']
        self.output.reset_index(inplace=True, drop=True)
    
    def remove(self, fill = np.nan, skip = [], upperonly = False, loweronly = False, keepchanges = False,
                ret = False):
        """
        Remove the outliers present in the df provided

        fill: optional
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
            Default is False
        """
        if keepchanges:
            output = self.df
        else:
            output = self.df.copy()
        for column in self.df.columns:
            if column not in skip:
                Q1 = np.nanpercentile(self.df[column], 25)
                Q3 = np.nanpercentile(self.df[column], 75)
                IQR = Q3 - Q1
                upper_limit = Q3 + 1.5*IQR
                lower_limit = Q1 - 1.5*IQR
                if not upperonly: output.loc[self.df[column] < lower_limit, column] = fill
                if not loweronly: output.loc[self.df[column] > upper_limit, column] = fill
        if ret:
            return output

    def plot_outliers(self):
        # self.df_plot
        pass

    def plot(self, tag = 'perc_outlier', **kwargs):
        plt.bar(self.output['ID'], self.output[tag], **kwargs)
        #to be improved. example: subplots
        #reduce the size of the x labels
    
    def plot_perc(self, tag = 'perc_outlier', **kwargs):
        plt.bar(self.output['ID'], self.output[tag], **kwargs)
        #to be improved. example: subplots
        #reduce the size of the x labels
    
    def plot_series(self, upperonly = False, loweronly = False):
        #plot time series with outliers highlighted
        #plot boxplot
        pass

# %% Missing data detection

class CheckNA():
    
    def __init__(self, df):
        self.df = df
        
    def check(self, threshold = 10, printinfo = True):
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
    #Lets caluclate frequency now
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
            
