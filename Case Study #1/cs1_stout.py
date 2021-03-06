# -*- coding: utf-8 -*-
"""CS1_Stout.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1REhe8JBRPZWhsVWyLNAeuTsTJZWPuPy0
"""

# Commented out IPython magic to ensure Python compatibility.
import pandas as pd
import numpy as np
import seaborn as sns
sns.set(font_scale=4)
import matplotlib.pyplot as plt
# %matplotlib inline
import os
import warnings
warnings.filterwarnings("ignore")

path = os.getcwd()

"""# EDA of the database"""

ds = pd.read_csv(os.path.join(path, 'loans_full_schema.csv'))
ds.shape

ds.columns

ds.describe()

"""## Inspect Missing Ratio"""

import math
def plot_missing_ratio(df):
    n = int(math.sqrt(len(df.columns))) + 1
    plt.clf()
    fig, ax = plt.subplots(n, n, figsize=(50, 50))

    colors = sns.color_palette('pastel')[0:2]
    for idx, col_name in enumerate(df.columns):
        record = df.iloc[:, idx].isna()
        ratio = [record.sum()/record.shape[0]*100, (1- record.sum()/record.shape[0])*100]
        labels = ['Missing ratio', '']
        explode = [0, 0.1]
        ax[idx // n, idx % n].pie(ratio, explode=explode, labels=labels,
                                  autopct='%1.1f%%', shadow=True, startangle=10, textprops={'fontsize': 15})
        ax[idx // n, idx % n].set_title(col_name, fontsize=40, rotation=5)

    for idx in range(len(df.columns), n*n):
        fig.delaxes(ax[idx // n, idx % n])

    plt.tight_layout(pad = .5)

plot_missing_ratio(ds)

# In place of Nulls in months_since_ values, it is assumed that there is no record of such events, it can be replaced with 0.
ds['months_since_last_delinq'][ds['months_since_last_delinq'].isna()]=0
print(sum(ds['months_since_last_delinq'].isna()))
ds['months_since_90d_late'][ds['months_since_90d_late'].isna()]=0
print(sum(ds['months_since_90d_late'].isna()))
ds['months_since_last_credit_inquiry'][ds['months_since_last_credit_inquiry'].isna()]=0
print(sum(ds['months_since_last_credit_inquiry'].isna()))

# Imputing in the null values for the fields of emp_title emp_length.
ds['emp_title'][ds['emp_title'].isna()]='Other'
print(sum(ds['emp_title'].isna()))
ds['emp_length'][ds['emp_length'].isna()]=0
print(sum(ds['emp_length'].isna()))

# debt_to_income field is empty in cases where the income is 0. Replacing debt to income for such cases with 999
ds['debt_to_income'][ds['debt_to_income'].isna()]=999
print(sum(ds['debt_to_income'].isna()))

"""## Inspect Distribution"""

from pandas.api.types import is_numeric_dtype, is_string_dtype
num_cols = ds.describe().columns

def plot_distribution(df, col_names_numeric):
    df = df.loc[:, col_names_numeric].replace({None: None})
    n = int(math.sqrt(len(df.columns))) + 1

    plt.clf()
    fig, ax = plt.subplots(n, n, figsize=(50, 50))

    for idx, col_name in enumerate(df.columns):
        record = df.iloc[:, idx]
        sns.distplot(record, ax=ax[idx // n, idx % n])
        ax[idx // n, idx % n].set_title(col_name, fontsize=20, rotation=5)
        ax[idx // n, idx % n].set_xlabel(ax[idx // n, idx % n].get_xlabel(), rotation=5)

    for idx in range(len(df.columns), n * n):
        fig.delaxes(ax[idx // n, idx % n])

    plt.tight_layout()


plot_distribution(ds,num_cols)

print(ds['delinq_2y'].value_counts())
print(ds['num_collections_last_12m'].value_counts())
print(ds['num_historical_failed_to_pay'].value_counts())
print(ds['current_accounts_delinq'].value_counts())
print(ds['num_accounts_120d_past_due'].value_counts())
print(ds['num_accounts_30d_past_due'].value_counts())
print(ds['tax_liens'].value_counts())
print(ds['paid_late_fees'].value_counts())

# These columns show very less variation in data and hence cannot provide much information.

"""## Inspect Categorical Data """

cat_cols = list(set(ds.columns)-set(ds.describe().columns))
def plot_category_count(df, col_names_categorical, min_size=1):
    if not col_names_categorical:
        return
    df = df.loc[:, col_names_categorical].replace({None: None})
    n = int(math.sqrt(len(df.columns))) + 1

    plt.clf()
    fig, ax = plt.subplots(n, n, figsize=(20, 20))

    for idx, col_name in enumerate(df.columns):
        df_cnt = df.groupby(col_name).count().reset_index()
        df_cnt = df_cnt.iloc[:, [0, 1]]
        df_cnt.columns = [col_name, 'count']
        df_cnt = df_cnt[df_cnt.loc[:, 'count'] > min_size]
        df_cnt = df_cnt.sort_values(by=['count'], ascending=False)
        sns.barplot(x=col_name, y="count", data=df_cnt, ax=ax[idx // n, idx % n])
        ax[idx // n, idx % n].set_title(col_name, fontsize=15)
        ax[idx // n, idx % n].set_xticklabels(ax[idx // n, idx % n].get_xticklabels(), fontsize=15, rotation = 315, ha='left')

    for idx in range(len(df.columns), n*n):
        fig.delaxes(ax[idx // n, idx % n])
        
    plt.tight_layout()


plot_category_count(ds, cat_cols, 10)

"""From the above visualizations of null value ratios and distribution of information, we can safely assume that the columns:
* delinq_2y
* num_collections_last_12m
* num_historical_failed_to_pay
* current_accounts_delinq
* num_accounts_120d_past_due
* num_accounts_30d_past_due
* tax_liens
* paid_late_fees

can be deleted from the dataset.

Other Columns that provide no information or do not affect the loan interest rate as they occur after the offerring of the loan can also be deleted. These columns are:
* loan_status
* disbursement_method
"""

ds = ds.drop(columns=[
        'delinq_2y',
        'num_collections_last_12m',
        'num_historical_failed_to_pay',
        'current_accounts_delinq',
        'num_accounts_120d_past_due',
        'num_accounts_30d_past_due',
        'tax_liens',
        'paid_late_fees',
        'loan_status',
        'disbursement_method'])

"""## Inspect Correlations throughout the model"""

def plot_corr_matrix(df, col_names_numeric, label_fontsize=20):
    df = df.loc[:, col_names_numeric].replace({None: None})
    
    plt.clf()
    fig = plt.figure(figsize=(70, 70))

    df = df.astype(float)
    sns.heatmap(df.corr(method='spearman'), annot=True, linewidth=0.5, annot_kws={"size": label_fontsize})

    plt.title('Correlation Matrix', fontsize=30)


plot_corr_matrix(ds, ds.describe().columns, 30)

def plot_corr_interest_rate(df, col_names_numeric, label_fontsize=20):
    df = df.loc[:, col_names_numeric].replace({None: None})
    
    plt.clf()
    fig = plt.figure(figsize=(70,2))

    df = df.astype(float).corr(method='spearman')
    sns.heatmap(df['interest_rate':'interest_rate'], center=0.0, vmax=1., vmin=-1., annot=True, linewidth=0.5, annot_kws={"size": label_fontsize})

    plt.title('Correlation Matrix', fontsize=50)


plot_corr_interest_rate(ds, ds.describe().columns, 30)

# checking the ratio of joint to individual:
ds['application_type'].value_counts()

# Through this analysis, the null values displayed for the columns pertaining
# to joint loans are justified as NULL for those that are not joint loans.

# For ease and better ability to understand without having different types of loans 
# in one dataset, a separate subset of data would be the most viable option.

"""## Separating data for Joint and Individual loans"""

j_loan_ds = ds[ds['application_type'] =='joint']
i_loan_ds = ds[ds['application_type'] =='individual']
j_loan_ds.shape, i_loan_ds.shape

"""## Joint Loans Exploration

Removing the columns that don't pertain to joint applications
"""

j_loan_ds = j_loan_ds.drop(columns=['annual_income', 'debt_to_income', 'verified_income'])

"""### Joint Loans - Correlations"""

plot_corr_matrix(j_loan_ds, j_loan_ds.describe().columns, 30)

plot_corr_interest_rate(j_loan_ds, j_loan_ds.describe().columns, 30)

"""Selecting variables with a strong correlation on either sides of atleast 0.2:
* debt_to_income_joint
* total_credit_limit
* total_debt_limit
* num_mort_accounts
* account_never_delinq_percent
* term
* paid_principal
"""

num_cols_j = ['debt_to_income_joint', 'total_credit_limit', 'total_debit_limit', 'num_mort_accounts', 'account_never_delinq_percent', 'term', 'paid_principal']

"""### Creating dummy variables for analysis in regression model"""

j_loan_ds.info()

j_loan_ds = pd.get_dummies(j_loan_ds)
j_new_cols = list(set(j_loan_ds.columns)-(set(cat_cols).union(set(num_cols))))

"""Two training subsets are created, one for only the categorical values and one containing both numerical and categorical values. This is done in response to the poor correlations seen in the correlation with interest rates of numerical values in the dataset.
* Train subset 1 consists of all the columns
* Train subset 2 consists of all the categorical columns

### R-Squared analysis using sklearn
"""

from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
train1_j = j_loan_ds.drop(columns=['interest_rate'])
train2_j = j_loan_ds[j_new_cols]

j_loan_ds = j_loan_ds[j_loan_ds.notna()]

np.any(np.isnan(j_loan_ds)), j_loan_ds.shape

lm1 = LinearRegression()
reg1 = lm1.fit(
    train1_j,
    j_loan_ds['interest_rate']
)
pred1_j = reg1.predict(train1_j)

r2_score(j_loan_ds['interest_rate'], pred1_j)

from sklearn.preprocessing import StandardScaler
sc = StandardScaler()
t2_j = sc.fit_transform(train2_j)
lm2 = LinearRegression()
reg2 = lm2.fit(
    t2_j,
    j_loan_ds['interest_rate']
)
pred2_j = reg2.predict(t2_j)

r2_score(j_loan_ds['interest_rate'], pred2_j)

"""### P-Value analysis using statsmodels.api"""

import statsmodels.api as sm

X = train1_j.astype(float)
X = sm.add_constant(X)
y = j_loan_ds['interest_rate']
mdl1 = sm.OLS(y, X)
reg_sm1 = mdl1.fit()
p_val_j1 = pd.DataFrame(reg_sm1.pvalues, columns=['p-value'])

p_val_j1.sort_values('p-value').head(20).index

# This shows the top 20 features that are most impactful for predicting interest_rate

X2 = train2_j.astype(float)
X2 = sm.add_constant(X2)
mdl2 = sm.OLS(y, X2)
reg_sm2 = mdl2.fit()
p_val_j2 = pd.DataFrame(reg_sm2.pvalues, columns=['p-value'])

p_val_j2.sort_values('p-value').head(20).index

# This shows the top 20 features that are most impactful for predicting interest_rate

"""Since there are multiple classes in some of the variables, it is difficult to interpret the result of the whole model at once, hence regressinon over a set of variables is a good way to go forward.

## Individual Loans Exploration

Removing the columns that don't pertain to individual applications
"""

i_loan_ds = i_loan_ds.drop(columns=['annual_income_joint', 'debt_to_income_joint', 'verification_income_joint'])

"""### Individual Loans - Correlations"""

plot_corr_matrix(i_loan_ds, i_loan_ds.describe().columns, 30)

plot_corr_interest_rate(i_loan_ds, i_loan_ds.describe().columns, 30)

"""Selecting variables with a strong correlation on either sides of atleast 0.2:
* debt_to_income
* total_debit_limit
* term
"""

num_cols_i = ['debt_to_income', 'total_debit_limit', 'term']
cat_cols_i = list(set(i_loan_ds.columns)-set(i_loan_ds.describe().columns))
print(cat_cols_i)

i_loan_ds.info()

"""### Creating dummy variables for analysis in regression model"""

i_loan_ds = pd.get_dummies(i_loan_ds)
i_new_cols = list(set(i_loan_ds.columns)-(set(cat_cols_i).union(set(num_cols_i))))
print(i_new_cols)

"""Two training subsets are created, one for only the categorical values and one containing both numerical and categorical values. This is done in response to the poor correlations seen in the correlation with interest rates of numerical values in the dataset.
* Train subset 1 consists of all the columns
* Train subset 2 consists of all the categorical columns

### R-Squared analysis using sklearn
"""

from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
train1_i = i_loan_ds.drop(columns=['interest_rate'])
train2_i = i_loan_ds[i_new_cols]

i_loan_ds = i_loan_ds[i_loan_ds.notna()]

np.any(np.isnan(i_loan_ds)), i_loan_ds.shape

lm1 = LinearRegression()
reg1 = lm1.fit(
    train1_i,
    i_loan_ds['interest_rate']
)
pred1_i = reg1.predict(train1_i)

r2_score(i_loan_ds['interest_rate'], pred1_i)

from sklearn.preprocessing import StandardScaler
sc = StandardScaler()
t2_i = sc.fit_transform(train2_i)
lm2 = LinearRegression()
reg2 = lm2.fit(
    t2_i,
    i_loan_ds['interest_rate']
)
pred2_i = reg2.predict(t2_i)

r2_score(i_loan_ds['interest_rate'], pred2_i)

"""### P-Value analysis using statsmodels.api"""

X = train1_i.astype(float)
X = sm.add_constant(X)
y = i_loan_ds['interest_rate']
mdl1 = sm.OLS(y, X)
reg_sm1 = mdl1.fit()
p_val_i1 = pd.DataFrame(reg_sm1.pvalues, columns=['p-value'])

p_val_i1.sort_values('p-value').head(20).index

# This shows the top 20 features that are most impactful for predicting interest_rate

X2 = train2_i
X2 = sm.add_constant(X2)
y = i_loan_ds['interest_rate']
mdl2 = sm.OLS(y, X2)
reg_sm2 = mdl2.fit()
p_val_i2 = pd.DataFrame(reg_sm2.pvalues, columns=['p-value'])

p_val_i2.sort_values('p-value').head(20).index

# This shows the top 20 features that are most impactful for predicting interest_rate

"""# Results

* After a string of data cleaning, null-value-replacing and vizualizations, the data provided was modeled on linear regression. In the results, we divided the data into two parts: individual and join loan applications.
* Each of these subsets were processed individually. During doing so, we found that our models perform pretty well under two training subsets of the data; first training set having all the variables and other having only the categorical variables. These two training subsets were created and modeled on for both data individual and joint data. 
* Division of data into training set and testing set was deemed unnecessary due to the poor correlation of numerical values and often imbalanced distributions of categorical data.
"""