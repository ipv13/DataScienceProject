#https://serhanaya.github.io/posts/kaggle-rossmann-sales-prediction/

#data exploration cleaning and preparation
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')
#machine learning models libraries
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import GradientBoostingRegressor
#Preprocessing related libraries
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer

# import data. Be careful for Date type, String type (factors in R).
train = pd.read_csv("train.csv", sep=',', parse_dates=['Date'],
                    dtype={'StateHoliday': str, 'SchoolHoliday':str})
test = pd.read_csv("test.csv", sep=",", index_col = 'Id', parse_dates=['Date'],
                  dtype={'StateHoliday': str, 'SchoolHoliday':str})
store = pd.read_csv("store.csv", sep=",", dtype={'StoreType': str,'Assortment': str,'PromoInterval': str})

# Inspecting train data - See first rows.
print(train.head())

# Inspecting train data - See last rows.

print(train.tail())

#Create new columns Year and Month to be used in the analysis of seasonal effects on sales.
train['Year'] = pd.DatetimeIndex(train['Date']).year
train['Month'] = pd.DatetimeIndex(train['Date']).month

#change the order of the columns
train = train[['Store', 'DayOfWeek', 'Date', 'Year', 'Month', 'Customers', 'Open',
               'Promo', 'StateHoliday', 'SchoolHoliday', 'Sales']]
list(train.columns.values)

# Inspecting train data - Data types
train.dtypes

# Unique values of "StateHoliday" factor
train['StateHoliday'].unique()

# convert categorical data to numeric data
# Factor levels: '0' -> 0 ; 'a' -> 1; 'b' -> 2; 'c' -> 3.
train.loc[train['StateHoliday'] == '0', 'StateHoliday'] = 0
train.loc[train['StateHoliday'] == 'a', 'StateHoliday'] = 1
train.loc[train['StateHoliday'] == 'b', 'StateHoliday'] = 2
train.loc[train['StateHoliday'] == 'c', 'StateHoliday'] = 3
train['StateHoliday'] = train['StateHoliday'].astype(int, copy=False)

# Check if worked
print('levels :', train['StateHoliday'].unique(), '; data type :', train['StateHoliday'].dtype)

# It worked, now automatize the process.
def categorical_to_numerical(df, colname, start_value=0):
    while df[colname].dtype == object:
        myval = start_value # factor starts at "start_value".
        for sval in df[colname].unique():
            df.loc[df[colname] == sval, colname] = myval
            myval += 1
        df[colname] = df[colname].astype(int, copy=False)
    print('levels :', df[colname].unique(), '; data type :', df[colname].dtype)


train['SchoolHoliday'].unique()
categorical_to_numerical(train, 'SchoolHoliday')

train.dtypes

print(train.describe())

#checking the NaN values:
train['Open'].unique()

train = train[['Store', 'DayOfWeek', 'Date', 'Year', 'Month', 'Customers', 'Open',
               'Promo', 'StateHoliday', 'SchoolHoliday', 'Sales']]
list(train.columns.values)

print("NANs for individual columns")
print("---------------------------")
from collections import Counter
x = {colname : train[colname].isnull().sum() for colname in train.columns}
Counter(x).most_common()

#Compute pairwise correlation of columns using pandas.corr() function.
corMat = pd.DataFrame(train.loc[:, ['DayOfWeek', 'Sales', 'Month', 'Year', 'Customers', 'Promo',
                                    'StateHoliday', 'SchoolHoliday']].corr())
print(corMat)

# Visualize correlation of the DataFrame using matplotlib.pcolor() function
plt.pcolor(corMat)
#plt.show()

#Seaborn specializes in static charts and makes making a heatmap from a Pandas DataFrame
sns.heatmap(data=corMat)
#plt.show()

#examine test dataset
test.shape

#Change Year and Month column data types as Date type as we did for the train dataset before.
test['Year'] = pd.DatetimeIndex(test['Date']).year
test['Month'] = pd.DatetimeIndex(test['Date']).month

print(test.head())

#how many closed stores are there
sum(test['Open'] == 0)

#Change the column names of the test dataset to get construct same feature names with the train dataset.
test = test[['Store', 'DayOfWeek', 'Date', 'Year', 'Month', 'Open',
             'Promo', 'StateHoliday', 'SchoolHoliday']]
list(test.columns.values)

#For each column, see how many missing values exist.
print("NANs for individual columns")
print("---------------------------")
from collections import Counter
x = {colname : test[colname].isnull().sum() for colname in test.columns}
Counter(x).most_common()


#There are 11 missing values in Open column. Let’s have a detailed look at those:
print(test.loc[np.isnan(test['Open'])])

#Check train dataset about store 622
print(train.loc[train['Store'] == 622].head())

#Avoid missing any information. So deleting the rows of Store 622 which have missing Open value, 
#should be our last option. Either label it 0 or 1. As seen above, we have data for Store 622 in train dataset. 
#Therefore, let’s label missing values of Open column in test dataset as 1.

test.loc[np.isnan(test['Open']), 'Open'] = 1

#Checking if there are any missing values left.
print("NANs for individual columns")
print("---------------------------")
from collections import Counter
x = {colname : test[colname].isnull().sum() for colname in test.columns}
Counter(x).most_common()

#Check for the data types for test dataset
test.dtypes

#fixing StateHoliday and SchoolHoliday columns type
categorical_to_numerical(test, 'StateHoliday')
categorical_to_numerical(test, 'SchoolHoliday')
test.dtypes

#Because only StateHoliday 0 and 1 exist in test dataset, 
#we should consider deleting the rows in train dataset that the StateHoliday value is different than 0 or 1.
train.loc[train['StateHoliday'] > 1].shape
train = train.loc[train['StateHoliday'] < 2]

# explore the store dataset
store.shape
store.head()
store.tail()

#missing values in this dataset
print("NANs for individual columns")
print("---------------------------")
from collections import Counter
x = {colname : store[colname].isnull().sum() for colname in store.columns}
Counter(x).most_common()

#Promo2SinceWeek, Promo2Interval, Promo2SinceYear, CompetitionOpenSinceMonth, 
#CompetitionOpenSinceYear and CompetitionDistance columns have different size of missing values. 
#We’ll first the contents, unique values in those columns then consider imputation using either 
#scikit-learn or pandas built-in commands.

store['PromoInterval'].unique()

#If there is no promotion, then the corresponding columns should have zero values.
store.loc[store['Promo2'] == 0, ['Promo2SinceWeek', 'Promo2SinceYear', 'PromoInterval']] = 0
store.loc[store['Promo2'] != 0, 'Promo2SinceWeek'] = store['Promo2SinceWeek'].max() - store.loc[store['Promo2'] != 0, 'Promo2SinceWeek']
store.loc[store['Promo2'] != 0, 'Promo2SinceYear'] = store['Promo2SinceYear'].max() - store.loc[store['Promo2'] != 0, 'Promo2SinceYear']
categorical_to_numerical(store, 'PromoInterval', start_value=0)
store.dtypes

#Change the categorical values (string type) of StoreType and Assortment columns to integers. Check the results.
categorical_to_numerical(store, 'StoreType')
categorical_to_numerical(store, 'Assortment')
store.dtypes

#An overview of the data after the latest settings.
print(store.head())

#Are there still missing values?
print("NANs for individual columns")
print("---------------------------")
from collections import Counter
x = {colname : store[colname].isnull().sum() for colname in store.columns}
Counter(x).most_common()

#Filling the missing values with sklearn’s built-in command. Filling with the column.mean().
from sklearn.impute import SimpleImputer
imputer = SimpleImputer().fit(store)
store_imputed = imputer.transform(store)


#Check the resutls
store2 = pd.DataFrame(store_imputed, columns=store.columns.values)

print("NANs for individual columns")
print("---------------------------")
from collections import Counter
x = {colname : store2[colname].isnull().sum() for colname in store2.columns}
Counter(x).most_common()

store2.head()

store2['CompetitionOpenSinceMonth'] = store2['CompetitionOpenSinceMonth'].max() - store2['CompetitionOpenSinceMonth']
store2['CompetitionOpenSinceYear'] = store2['CompetitionOpenSinceYear'].max() - store2['CompetitionOpenSinceYear']
store2.tail()

#Are the Store column similar in both train and store datasets?

len(store2['Store']) - sum(store2['Store'].isin(train['Store']))

# Checking if there are additional (unnecessary) stores in "train" data.
# No difference at all!

StoreStore = pd.Series(store2['Store']); StoreTrain = pd.Series(train['Store'])

sum(StoreTrain.isin(StoreStore) == False)

#Merge train and store datasets before modeling the data.
train_store = pd.merge(train, store2, how = 'left', on='Store')

print(train_store.head())

#Check the results.
print(train_store.head())
print(train_store.tail())

#Merge test and store datasets and check the result.
test_store = test.reset_index().merge(store2, how = 'left', on='Store').set_index('Id')
print(test_store.head())
test_store.shape
test_store.isnull().sum()

test_store.to_csv('test_store.csv', index="Id")


#Visual Exploration
train_store.boxplot(column='Sales', by='Year')
#plt.show()
#Sales by Year
train_store.boxplot(column='Sales', by='Month')
#plt.show()


# Sales by month
train_store.boxplot(column='Sales', by='StateHoliday')
#plt.show()

#Sales in state holidays
train_store.boxplot(column='Sales', by='SchoolHoliday')
#plt.show()


#Sales in school holidays
train_store.boxplot(column='Sales', by='StoreType')
#plt.show()

# Sales by store type
train_store.boxplot(column='Sales', by='DayOfWeek')
#plt.show()

#Sales change through the week

train_store.boxplot(column='Sales', by='Promo2')
#plt.show()

# Promo and Sales change
train_store.boxplot(column='Customers', by='Month')
#plt.show()


#Promo interval vs sales
train_store.hist(column='Sales', by='Year', bins=30)
#plt.show()

#Sales & years
train_store.hist(column='Sales', by='Month', bins=30)
#plt.show()

#Sales & Months
train_store.hist(column='CompetitionDistance', bins=30)
#plt.show()

train_store.to_csv('train_store.csv', index="Id")





#models
train_store = pd.read_csv("train_store.csv")
train_store = pd.DataFrame(train_store)
train_store = train_store.drop(["Unnamed: 0"],axis=1)


test_store = pd.read_csv("test_store.csv")
test_store = pd.DataFrame(test_store)

train_model = train_store.drop(['Customers', 'Date'], axis=1)
train_model['Year'] = train_model['Year'].max() - train_model['Year']

print(train_model.head())

test_model = test_store.drop(['Date'], axis=1)
test_model['Year'] = test_model['Year'].max() - test_model['Year']

print(test_model.head())

test_model_open = test_model.loc[test_model['Open'] == 1]
test_model_open = test_model_open.drop('Open', axis=1)

test_model_close = test_model.loc[test_model['Open'] == 0]

test_model_open.head()

SalesDF = train_model['Sales']
train_model = train_model.drop(['Sales'], axis=1)
train_model['Sales'] = SalesDF

summary = train_model.describe()
train_normalized = train_model.copy()
ncols = len(train_normalized.columns)

for i in range(ncols):
    mean = summary.iloc[1, i]
    sd = summary.iloc[2, i]
    train_normalized.iloc[:,i:(i + 1)] = \
        (train_normalized.iloc[:,i:(i + 1)] - mean) / sd

sales_normalized = train_normalized['Sales']
train_normalized = train_normalized.drop(['Sales'], axis=1)
train_normalized['Sales'] = sales_normalized

from sklearn.model_selection import train_test_split
X = train_model.drop('Sales', axis=1)
y = train_model['Sales']
X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)

from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
scaler.fit(X_train)
X_train_scaled = pd.DataFrame(scaler.transform(X_train),
                                  columns=X.columns.values)
X_test_scaled = pd.DataFrame(scaler.transform(X_test),
                                  columns=X.columns.values)
test_model_open_scaled = pd.DataFrame(scaler.transform(test_model_open),
                                  columns=test_model_open.columns.values)



model_list = {
              'DesisionTree':DecisionTreeRegressor(),
              'RandomForest':RandomForestRegressor(),
              'GradientBoostingRegressor':GradientBoostingRegressor()
           }

for  model_name,model in model_list.items():
    model.fit(X_train, y_train)
    model.score(X_test, y_test)
    test_model_open = pd.DataFrame(test_model_open)
    test_model = pd.DataFrame(test_model)
    submission = {}
    submission = pd.DataFrame()
    submission["Predicted Sales"] = model.predict(test_model_open)
    submission = submission.reset_index()
    submission.head()
    submission.tail()
    submission.to_csv(model_name, sep=',', index=False)
    submission
