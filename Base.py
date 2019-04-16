# -*- coding: utf-8 -*-
"""
Created on Sun Apr 14 23:51:19 2019

@author: Admin
"""

from imdb import IMDb
ia = IMDb()
import joblib
import pandas as pd



Movies = joblib.load('Movies.pkl')
Movies= sorted(Movies.Titulo.unique())

Base = pd.DataFrame(columns=['Titulo', 'Poster', 'Genero'])
j=1
for i in Movies:
    try:
        print(j)
        mov=ia.search_movie(i)[0]
        movie = ia.get_movie(mov.movieID)
        Base=Base.append( pd.DataFrame([[i,movie['cover url'],movie['genres']]], columns=['Titulo', 'Poster', 'Genero']))
    except:
        continue
    j=j+1
    
joblib.dump(Base,'Base2.pkl')
