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
    
    def __init__(self, df, printinfo = True):
        self.df = df
        self.output = pd.DataFrame(np.zeros((len(df.columns), 3)), columns = ['ID', 'n_outlier', 'perc_outlier'])
        for i, column in enumerate(df.columns):
            Q1 = np.nanpercentile(df[column], 25)
            Q3 = np.nanpercentile(df[column], 75)
            IQR = Q3 - Q1
            upper_limit = Q3 + 1.5*IQR
            lower_limit = Q1 - 1.5*IQR
            if printinfo:
                print(f'Column: {column}')
                print(f'Number of upper outliers: {sum(df[column] > upper_limit)}')
                print(f'Number of lower outliers: {sum(df[column] < lower_limit)}')
                print(f'Percentage of outliers: {((sum(df[column] > upper_limit) + sum(df[column] < lower_limit))/len(df[column]))*100}')
            self.output.loc[i, 'ID'] = column
            self.output.loc[i, 'n_outlier'] = sum(df[column] > upper_limit) + sum(df[column] < lower_limit)
            self.output.loc[i, 'perc_outlier'] = ((sum(df[column] > upper_limit) + sum(df[column] < lower_limit))/len(df[column]))*100
    
    def plot(self, tag = 'perc_outlier'):
        plt.plot(self.output['ID'], self.output[tag])
        #to be improved. example: subplots
        #reduce the size of the x labels
    
    def remove(self, fill = np.nan, skip = []):
        output = self.df.copy()
        for column in self.df.columns:
            if column not in skip:
                Q1 = np.nanpercentile(self.df[column], 25)
                Q3 = np.nanpercentile(self.df[column], 75)
                IQR = Q3 - Q1
                upper_limit = Q3 + 1.5*IQR
                lower_limit = Q1 - 1.5*IQR
                output.loc[self.df[column] > upper_limit, column] = fill
                output.loc[self.df[column] < lower_limit, column] = fill
        return output
        #add a method to return the "positions" of the outliers,
        #the index basically, and their values

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

# %% Mann-Kendall and Sen's slope

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

# %% General operations

def print_row(df, row, cond = True):
    for col in df.columns:
        if cond:
            print(f'{col}: {df.loc[row, col].values[0]}')
        else:
            # print(f'{np.where(df.columns == col)[0][0]}')
            print(f'{col}: {df.iloc[row, np.where(df.columns == col)[0][0]]}')
            