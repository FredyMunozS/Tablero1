# -*- coding: utf-8 -*-
"""
Created on Sun Mar 10 21:12:35 2019

@author: Admin
"""

import pandas as pd
import numpy as np
import joblib



data = pd.read_csv('tmp.csv',  index_col=False)
data = data[['Price','Year', 'Mileage', 'State', 'Make', 'Model']]


X = data[['Model', 'Mileage',  'Year']]
y = data.Price
X = pd.get_dummies(data=X)


from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=42)



# first we import the GBR model from sklearn
from sklearn.ensemble import GradientBoostingRegressor
# get an instance of the model, using ‘ls’ : least squares regression as a loss function and the default learning rate which 0.1
gbr = GradientBoostingRegressor(loss ='ls', max_depth=6)
# fit the training data
gbr.fit (X_train, y_train)
# get the predicted values from the test set
predicted = gbr.predict(X_test)
# extract the residual values
residual = y_test - predicted

joblib.dump(gbr, 'CarsPriceModel3.pkl')




X2 = pd.DataFrame([['Explorer', 0, 2010 ]], columns=['Model' , 'Mileage',  'Year' ])
T=X.iloc[0:0]
X2D = T.append(pd.get_dummies(data=X2))
X2D.fillna(0, inplace=True)

gbr.predict(X2D)



abs(residual).mean()



