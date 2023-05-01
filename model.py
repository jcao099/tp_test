# Importing the required libraries
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
 
# Reading the dataset
data = pd.read_excel('data/IPL_Data.xlsx')
data = data.dropna()

# Seperating the target and features
# target ->y, features -> X
y = data['GP']
X = data[["Qty Invoiced", "Price","Extended Price","Ext Price USD", "Custom Total USD", "Unit Cost", "Ext Cost"]]
#X = data['Qty Invoiced', 'Price','Extended Price', 'Ext Price USD', 'Custom Total USD', '', 'Ext Cost']

# Splitting into training and test set
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=1)
 
# Making the model
lr = LinearRegression()
lr.fit(X_train.values, y_train.values)
# Predicting the output
y_pred = lr.predict(X_test.values)
 
# Saving the model
import joblib
 
joblib.dump(lr, "lr_model.sav")