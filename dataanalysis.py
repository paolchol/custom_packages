# -*- coding: utf-8 -*-
"""
Collection of custom functions for basic data analysis

author: paolo
"""

import numpy as np
import pandas as pd
import matplotlib as plt

# %% Outlier detection and rejection

class CheckOutliers():
    
    def __init__(self, df):
        self.df = df
        self.output = pd.DataFrame(np.zeros((len(df.columns), 3)), columns = ['ID', 'n_outlier', 'perc_outlier'])
        for i, column in enumerate(df.columns):
            Q1 = np.nanpercentile(df[column], 25)
            Q3 = np.nanpercentile(df[column], 75)
            IQR = Q3 - Q1
            upper_limit = Q3 + 1.5*IQR
            lower_limit = Q1 - 1.5*IQR
            print(f'Column: {column}')
            print(f'Number of upper outliers: {sum(df[column] > upper_limit)}')
            print(f'Number of lower outliers: {sum(df[column] < lower_limit)}')
            print(f'Percentage of outliers: {((sum(df[column] > upper_limit) + sum(df[column] < lower_limit))/len(df[column]))*100}')
            self.output['ID'][i] = column
            self.output['n_outlier'][i] = sum(df[column] > upper_limit) + sum(df[column] > upper_limit)
            self.output['perc_outlier'][i] = ((sum(df[column] > upper_limit) + sum(df[column] < lower_limit))/len(df[column]))*100
    
    def plot(self, tag = 'perc_outlier'):
        plt.pyplot.plot(self.output['ID'], self.output[tag])
                
        #to be improved. example: subplots
        #reduce the size of the x labels
    
    def remove(self, fill = np.nan):
        output = self.df.copy()
        for column in self.df.columns:
            Q1 = np.nanpercentile(self.df[column], 25)
            Q3 = np.nanpercentile(self.df[column], 75)
            IQR = Q3 - Q1
            upper_limit = Q3 + 1.5*IQR
            lower_limit = Q1 - 1.5*IQR
            output.loc[self.df[column] > upper_limit, column] = fill
            output.loc[self.df[column] < lower_limit, column] = fill
            
            #add a method to return the "positions" of the outliers,
            #the index basically, and their values
        return output

# %% Missing data detection

class CheckNA():
    
    def __init__(self, df):
        self.df = df
        
    def check(self, threshold = 10):
        count = 0
        self.output = pd.DataFrame(np.zeros((len(self.df.columns), 2)), columns = ['ID', 'perc_NA'])
        fvi = self.df.apply(pd.Series.first_valid_index, axis = 0)
        for i, column in enumerate(self.df.columns):            
            perc_NA = round(self.df.loc[fvi[column]:, column].isna().sum()/len(self.df.loc[fvi[column]:, column]), 3)*100
            print(f'The column "{column}" has this percentage of NAs:\n{perc_NA}')
            if perc_NA > threshold:
                count = count + 1
            self.output['ID'][i] = column
            self.output['perc_NA'][i] = perc_NA
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

# %% General operations

def print_row(df, row, cond = True):
    for col in df.columns:
        if cond:
            print(f'{col}: {df.loc[row, col].values[0]}')
        else:
            # print(f'{np.where(df.columns == col)[0][0]}')
            print(f'{col}: {df.iloc[row, np.where(df.columns == col)[0][0]]}')