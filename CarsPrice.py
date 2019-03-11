# -*- coding: utf-8 -*-
"""
Created on Fri Mar  8 19:30:09 2019

@author: Admin
"""


import pandas as pd
import numpy as np
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import joblib
import category_encoders as ce


########################################################
#   obtienen las marcas y modelos correspondientes     #
########################################################

#data = pd.read_csv('https://github.com/albahnsen/PracticalMachineLearningClass/raw/master/datasets/dataTrain_carListings.zip')
#data.to_csv('tmp.csv', index=False)
data = pd.read_csv('tmp.csv',  index_col=False)
data = data[['Price','Year', 'Mileage', 'State', 'Make', 'Model']]
#print('data ',data.shape)
#print('data ',data.head())


Cars = data.groupby(['Make', 'Model'])['Make'].count().to_frame(name='Cantidad').reset_index()
Makers= sorted(Cars.Make.unique())
Years=sorted(data.Year.unique(), reverse=True)
States=sorted(data.State.unique())

########################################################
#   Importar el modelo                                 #
########################################################

#Model = joblib.load('C:/Users/Admin/Documents/1. Universidad/5. Mineria de Datos/Proyecto/CarsPriceModel.pkl')
Model = joblib.load('CarsPriceModel.pkl')




##########################
#      Objetos           #
##########################

colors = {
    'background': '#002b36',
    'text': '#2aa198'
}


MakeSelect=dcc.Dropdown(id='DropdownMake',
                        options=[{'label': i, 'value': i} for i in Makers],
                        placeholder='Fabricante',
                        )

ModelSelect=dcc.Dropdown(id='DropdownModel',
                         placeholder='Modelo')

YearSelect=dcc.Dropdown(id='DropdownYear',
                        placeholder='Año',
                        options=[{'label': i, 'value': i} for i in Years]
                        )

StateSelect=dcc.Dropdown(id='DropdownState',
                        placeholder='Estado',
                        options=[{'label': i, 'value': i} for i in States]
                        )


Milleage=dcc.Input(id='InputMilleage',
                   placeholder='Recorrido [millas]',
                   type='number'
                   )

Button= html.Button('Calcular..', id='ButtonCalc')




##########################
#      Layout App        #
##########################

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


banner = html.Div([
                    html.H1('Pronóstico de precio de vehiculos V2:' , style={'width': '100%', 'display': 'inline-block', 'color': colors['text'], 'margin':25})
                ])


Med001 = html.Div([MakeSelect,], style={'width':'80%',  'textAlign': 'center', 'marginBottom': 20, 'margin-left': '10%' ,'color': colors['text']})

Med002 = html.Div([ModelSelect,], style={'width':'80%',  'textAlign': 'center', 'marginBottom': 20, 'margin-left': '10%','color': colors['text']})

Med003 = html.Div([YearSelect,], style={'width':'80%',  'textAlign': 'center', 'marginBottom': 20, 'margin-left': '10%','color': colors['text']})

Med031 = html.Div([StateSelect,], style={'width':'80%',  'textAlign': 'center', 'marginBottom': 20, 'margin-left': '10%','color': colors['text']})


Med04Izq = html.Div([Milleage,], style={'width':'50%', 'display': 'inline-block', 'marginBottom': 20, 'margin-left': '10%','color': colors['text'], 'fontSize': 24})

Med04Der = html.Div([Button],   style={ 'width':'20%', 'display': 'inline-block', 'margin-right': '10%'})

Med004 = html.Div([ Med04Izq,
                    Med04Der              
                  ])

TextOut = html.Div(id='OutputTxt', style={'width':'80%',  'textAlign': 'center', 'marginBottom': 20, 'margin-left': '10%','color': colors['text'], 'fontSize': 24})


footer = html.Div(['Universidad de los Andes - Mineria de Datos',], style={'textAlign': 'center', 'color': colors['text']})



app.layout = html.Div(style={'backgroundColor': colors['background'], 'width': '99%'}, 
                     children=[ banner,
                                Med001,
                                Med002,
                                Med003,
                                Med031,
                                Med004,
                                html.Br(),
                                TextOut,
                                html.Br(),
                                footer

                                ])



##########################
#      Interacciones     #
##########################



@app.callback(
    dash.dependencies.Output('DropdownModel', 'options'),
    [dash.dependencies.Input('DropdownMake', 'value')])
def set_model_options(selected_make):
    return [{'label': i, 'value': i} for i in Cars.loc[Cars['Make']==selected_make, 'Model']]


@app.callback(
    dash.dependencies.Output('OutputTxt', 'children'),
    [dash.dependencies.Input('ButtonCalc', 'n_clicks'),
     dash.dependencies.Input('DropdownYear', 'value'),
     dash.dependencies.Input('InputMilleage', 'value'),
     dash.dependencies.Input('DropdownMake', 'value'),
     dash.dependencies.Input('DropdownModel', 'value'),
     dash.dependencies.Input('DropdownState', 'value'),
     ])
def update_output(clicks, Year, Milleage, Make, CarModel, State):
    
    
    
    T=joblib.load('VarT.pkl')
    Z2=joblib.load('VarZ2.pkl')

    X2=T.append(pd.DataFrame([[Year , Milleage, State , Make , CarModel]], columns=['Year', 'Mileage', 'State', 'Make', 'Model']))
    print(X2)
    
    Z2=Z2.append(ce.BinaryEncoder().fit_transform(X2.drop(['Mileage'], axis=1)))
    Z2['Mileage']=X2['Mileage']
    Z2['Year']=X2['Year']
    Z2.fillna(0, inplace=True)
    print(Z2)
       
    return 'El precio estimado es: {}'.format(Model.predict(Z2))




if __name__ == '__main__':
    app.run_server(
        debug=True,
        host='0.0.0.0',
        port=80
    )
    
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
