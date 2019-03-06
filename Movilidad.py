# -*- coding: utf-8 -*-
"""
Created on Mon Oct 22 19:46:23 2018

@author: Admin
"""

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output, State
import requests
import numpy as np
from sodapy import Socrata
client = Socrata("www.datos.gov.co", None)
import base64


"""
#Si obtiene directo de webservice: 
df = pd.DataFrame.from_records(client.get("dy2z-yk96", limit=1000000))
df.to_csv('Viajes.csv', sep='|', encoding='utf-8', index = False)
df['LAT']=df.latitud_origen.str.slice(0,1)+'.'+df.latitud_origen.str.slice(1,15)
df['LON']=df.longitud_origen.str.slice(0,3)+'.'+df.longitud_origen.str.slice(3,15)
df['Hora']=df.hora_inicio.str.slice(0,5)
df['LAT'] = round(pd.to_numeric(df['LAT']),3)
df['LON'] = round(pd.to_numeric(df['LON']),3)
"""



##########################
#      Carga datos       #
##########################



df = pd.read_csv('Viajes.csv', sep='|', encoding='utf-8', dtype=str)
df['LAT']=df.latitud_origen.str.slice(0,1)+'.'+df.latitud_origen.str.slice(1,15)
df['LON']=df.longitud_origen.str.slice(0,3)+'.'+df.longitud_origen.str.slice(3,15)
df['Hora']=df.hora_inicio.str.slice(0,2)
df['LAT'] = round(pd.to_numeric(df['LAT']),2)
df['LON'] = round(pd.to_numeric(df['LON']),2)       



##########################
#      Api Clima         #
##########################


api_address='http://api.openweathermap.org/data/2.5/weather?appid=03170c3099c344ef380dd97ed3a8a2dd&q='
city = 'Bogota'
url = api_address + city
data = requests.get(url).json()
temp = data['main']['temp']
wind_speed = data['wind']['speed']

latitude = data['coord']['lat']
longitude = data['coord']['lon']

description = data['weather'][0]['description']
ClimaID = data['weather'][0]['id']
icon = data['weather'][0]['icon']


#gs = goslate.Goslate()
#Clima = gs.translate(description, 'es')

Clima = description


##########################
#   Arbol Decision       #
##########################

arbol = pd.read_csv('ArbolDecision.csv', sep='|', encoding='utf-8')




##########################
#    Formato datos       #
##########################


df2=df.groupby(['Hora','medio_predominante','LAT','LON'])['Hora'].count().to_frame(name='Cantidad').reset_index()
df2['Hora']=df2['Hora'].astype('float')
df2['LAT']=df2['LAT'].astype('float')
df2['LON']=df2['LON'].astype('float')



a=df.groupby(['medio_predominante'])['medio_predominante'].count().to_frame(name='Cantidad').reset_index()

medios_predominantes=[  df2['medio_predominante']=='PEATON',
                        df2['medio_predominante']=='TPC-SITP',
                        df2['medio_predominante']=='Transmilenio',
                        df2['medio_predominante']=='AUTO',
                        df2['medio_predominante']=='BICICLETA, BICICLETA CON MOTOR',
                        df2['medio_predominante']=='ESPECIAL',
                        df2['medio_predominante']=='MOTO',
                        df2['medio_predominante']=='INTERMUNICIPAL',
                        df2['medio_predominante']=='TAXI',
                        df2['medio_predominante']=='ALIMENTADOR',
                        df2['medio_predominante']=='ILEGAL',
                        df2['medio_predominante']=='OTROS']

medios=['Peaton','Bus','Bus','Carro','Bici','Carro','Moto','Bus','Taxi','Bus','Carro','Otro']
df2['medio'] = np.select(medios_predominantes, medios, default='Otro')


deciles = np.arange(1, 10) * 10
deciles_dist = [np.percentile(df2['Cantidad'], dec) for dec in deciles]
print(deciles_dist)


conditions = [
    (df2['Cantidad'] >0) & (df2['Cantidad'] < 2) ,
    (df2['Cantidad'] >=2) & (df2['Cantidad'] < 8) ,
    (df2['Cantidad'] >=8)]
choices = ['green', 'yellow', 'red']


df2['color'] = np.select(conditions, choices, default='black')


HORAS = pd.Series(range(0,24))
DEFAULT_OPACITY = 0.8
DEFAULT_HORA = 0

df3=df2[df2['Hora']==DEFAULT_HORA & df2['medio'].isin(['Bici','Moto'])]



df2[df2['Hora']==DEFAULT_HORA]



##########################
#      Objetos           #
##########################

SeleccionMedio=dcc.Checklist(id='ChkList',
                            options=[
                                    {'label': 'Bici', 'value': 'Bici'},
                                    {'label': 'Bus', 'value': 'Bus'},
                                    {'label': 'Carro', 'value': 'Carro'},
                                    {'label': 'Moto', 'value': 'Moto'},
                                    {'label': 'Otro', 'value': 'Otro'},
                                    {'label': 'Peaton', 'value': 'Peaton'},
                                    {'label': 'Taxi', 'value': 'Taxi'}
                            ],
                            values=[],
                            labelStyle={'display': 'inline-block'}
                            )

SliderHora=dcc.Slider(
        					id='horas-slider',
        					min=min(HORAS),
        					max=max(HORAS),
        					#value=DEFAULT_HORA,
        					marks={str(hora): str(hora) for hora in HORAS},
        				)


Mapa=dcc.Graph(id='map', 
              figure={'data': [{
                            'lat': df3['LAT'],
                            'lon': df3['LON'],
                            'marker': {
                                        'color': df3['color'],
                                        'size': 10,
                                        'opacity': 0.6
                                        },
                            'customdata': df['id_encuesta'],
                            'type': 'scattermapbox'
                            }],
                  'layout': {
                            'mapbox': {'accesstoken': 'pk.eyJ1IjoiY2hyaWRkeXAiLCJhIjoiY2ozcGI1MTZ3MDBpcTJ3cXR4b3owdDQwaCJ9.8jpMunbKjdq1anXwU5gxIw',
                                       'bearing':0,
                                       'center':dict(lat=4.66,lon=-74.11),
                                       'pitch':0,
                                       'zoom':9
                                        },
                            'hovermode': 'closest',
                            'margin': {'l': 5, 'r': 5, 'b': 5, 't': 5} 
                            }})

InputTexto=dcc.Input(   id='inputTxt', 
                        placeholder='Distancia de su recorrido (km)...',
                        type='text',
                        value='1'
                    )

colors = {
    'background': '#002b36',
    'text': '#2aa198'
}

Button= html.Button('Calcular..', id='my-button', style={'color': colors['text']})



##########################
#      Layout App        #
##########################

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)




banner = html.Div([
                    html.H1('¿Cúal medio de transporte me recomiendas?' , style={'width': '100%', 'display': 'inline-block', 'color': colors['text'], 'margin':25})
                ])


footer = html.Div(['Universidad de los Andes - Todos los derechos reservados',], style={'textAlign': 'center', 'color': colors['text']})

SupIzq = html.Div(['Así se comporta el tráfico en un día:', ] , style={'color': colors['text'], 'width': '45%', 'margin': 25 , 'display': 'inline-block'})



Med001 = html.Div([SeleccionMedio,], style={'width':'50%', 'margin':25, 'color': colors['text']})

Med002 = html.Div([SliderHora,], style={'width':'100%', 'margin':25})

Med003 = html.Div([html.Img(src='http://openweathermap.org/img/w/'+ str(icon) + '.png')], style={'color': colors['text'], 'textAlign': 'left', 'width': '10%', 'margin': {'l': 0, 'r': 20, 'b': 5, 't': 5}, 'display': 'inline-block', 'float': 'right'})

Med004 = html.Div([ 
                   html.P('{} °C'.format(int(temp-273))),
                   ] , style={ 'fontSize': 30, 'color': colors['text'], 'width': '20%', 'margin': {'l': 20, 'r': 0, 'b':0, 't': 20} , 'textAlign': 'right' ,'display': 'inline-block', 'float': 'right'})

Med005 = html.Div([html.Img(src='http://openweathermap.org/img/w/'+ str(icon) + '.png')], style={'color': colors['text'], 'margin': {'l': 0, 'r': 0, 'b':10, 't': 0} , 'textAlign': 'left', 'width': '20%',  'display': 'inline-block', 'float': 'right'})



BlqClima =html.Div([ Med003,  Med004  ])



BlqSup = html.Div([ SupIzq, BlqClima ])

BlqMed = html.Div([  Med001 , 
                     html.Div([Med002], style={  'width':'45%', 'display': 'inline-block'}), 
                     html.Div([Button], style={  'display': 'inline-block', 'float': 'right' ,'margin': {'l': 0, 'r': 50, 'b':0, 't': 0} }),
                     html.Div([InputTexto] , style={ 'display': 'inline-block', 'float': 'right'}),
                     html.P('Escriba la distancia en Km..' , style={ 'color': colors['text'], 'display': 'inline-block', 'float': 'right'})
                   ])



BlMapa = html.Div([Mapa,], style={'width':'100%', 'margin': 25})

Img01 = html.Img(id='PD1')
Img02 = html.Img(id='PD2')
Img03 = html.Img(id='PD3')


BlqInf = html.Div([ 
                    html.Div([Img03],  style={ 'width': '15%', 'float': 'right'}),
                    html.Div([Img02],  style={ 'width': '15%', 'float': 'right'}),
                     html.Div([Img01],  style={ 'width': '15%',  'float': 'right'}),
                    html.Div([BlMapa], style={ 'width': '45%'})
                   ])



app.layout = html.Div(style={'backgroundColor': colors['background'], 'width': '99%'}, children=[
                banner,
                BlqSup,
                BlqMed,
                BlqInf,
                footer
])



##########################
#      Interacciones     #
##########################

@app.callback(
    Output('map', 'figure'),
    [Input('horas-slider','value'),
     Input('ChkList','values')])

def update_mapa(horam, medios):
    print('hora: ' + str(horam) + ' Medos: ' + str(medios))
    df3=df2.ix[(df2['medio'].isin(medios))&(df2['Hora']==horam)]

    
    figure={'data': [{
                    'lat': df3['LAT'],
                    'lon': df3['LON'],
                    'marker': {
                                'color': df3['color'],
                                'size': 10,
                                'opacity': 0.6
                                },
                    'customdata': df['id_encuesta'],
                    'type': 'scattermapbox'
                    }],
            'layout': {
                    'mapbox': {'accesstoken': 'pk.eyJ1IjoiY2hyaWRkeXAiLCJhIjoiY2ozcGI1MTZ3MDBpcTJ3cXR4b3owdDQwaCJ9.8jpMunbKjdq1anXwU5gxIw',
                               'bearing':0,
                               'center':dict(lat=4.66,lon=-74.11),
                               'pitch':0,
                               'zoom':9
                                },
                    'hovermode': 'closest',
                    'margin': {'l': 5, 'r': 5, 'b': 5, 't': 5}}}
    return figure

@app.callback(Output('PD1', 'src'), 
              [Input('my-button', 'n_clicks')],
              [State('inputTxt', 'value')])
    
def on_click(Num_Clicks, Recorrido):
    d=float(Recorrido)
    a1=arbol.ix[(arbol['DistanciaMinima']<= d)&(arbol['DistanciaMaxima']>=d)&(arbol['Clima']==Clima)]
    a2=a1.sort_values(by='Puntuacion', ascending=False)
    print(a2[['Medio','Puntuacion']])
    print('el primero es: ' +  str(a2['Medio'].iloc[0]))
    
    EncIm1 = base64.b64encode(open(str(a2['Medio'].iloc[0])   + '.png', 'rb').read())
    src1='data:image/png;base64,{}'.format(EncIm1.decode())
    
    return src1



@app.callback(Output('PD2', 'src'), 
              [Input('my-button', 'n_clicks')],
              [State('inputTxt', 'value')])
    
def on_click(Num_Clicks, Recorrido):
    d=float(Recorrido)
    a1=arbol.ix[(arbol['DistanciaMinima']<= d)&(arbol['DistanciaMaxima']>=d)&(arbol['Clima']==Clima)]
    a2=a1.sort_values(by='Puntuacion', ascending=False)
    print('el segundo es: ' +  str(a2['Medio'].iloc[1]))
    
    EncIm2 = base64.b64encode(open(str(a2['Medio'].iloc[1])   + '.png', 'rb').read())
    src2='data:image/png;base64,{}'.format(EncIm2.decode())
    
    return src2


@app.callback(Output('PD3', 'src'), 
              [Input('my-button', 'n_clicks')],
              [State('inputTxt', 'value')])
    
def on_click(Num_Clicks, Recorrido):
    d=float(Recorrido)
    a1=arbol.ix[(arbol['DistanciaMinima']<= d)&(arbol['DistanciaMaxima']>=d)&(arbol['Clima']==Clima)]
    a2=a1.sort_values(by='Puntuacion', ascending=False)
    print('el tercero es: ' +  str(a2['Medio'].iloc[2]))
    
    EncIm3 = base64.b64encode(open(str(a2['Medio'].iloc[2])   + '.png', 'rb').read())
    src3='data:image/png;base64,{}'.format(EncIm3.decode())
    
    return src3

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)

    
    
