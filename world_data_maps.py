#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov  3 14:04:03 2022

@author: annika


Using data from https://ourworldindata.org/ we create static and animated maps visualizing the data

"""


from matplotlib import pyplot as plt
import plotly.express as px
import pandas as pd
import os
import geojson
import json
from matplotlib import animation


# %% read in data 
path_to_data_folder = '../../Daten/OurWorldInData/'  # where the data is stored


df_exp_education = pd.read_csv(path_to_data_folder + 'total-government-expenditure-on-education-gdp.csv')  # as share of GDP given by year
df_development = pd.read_csv(path_to_data_folder + 'human-development-index.csv')    # 
df_learning_vs_expensives = pd.read_csv(path_to_data_folder + 'national-average-learning-outcomes-vs-government-expenditure-per-primary-student.csv')  # 
df_student_achivings_vs_expensives = pd.read_csv(path_to_data_folder + 'share-of-students-achieving-no-or-minimum-learning-outcomes-by-expenditure-per-student.csv')  # 
df_pop_female = pd.read_csv(path_to_data_folder + 'share-population-female.csv')  # 
df_deaths_conflicts = pd.read_csv(path_to_data_folder + 'deaths-conflict-terrorism-per-100000.csv')  # 

# dataframes of last year in the data set:
df_pop_female_last_year = df_pop_female.loc[df_pop_female.groupby('Code')['Year'].transform('max').eq(df_pop_female['Year'])].reset_index(drop=True)
list(df_pop_female_last_year.columns)

df_exp_education_last_year = df_exp_education.loc[df_exp_education.groupby('Code')['Year'].transform('max').eq(df_exp_education['Year'])].reset_index(drop=True)
list(df_exp_education_last_year.columns)

df_development_last_year = df_development.loc[df_development.groupby('Code')['Year'].transform('max').eq(df_development['Year'])].reset_index(drop=True)
list(df_development_last_year.columns)

# %% Output folders:
folder_maps = 'output/maps/'
if not os.path.exists(folder_maps):
    os.makedirs(folder_maps)  

folder_gifs = 'output/gifs/'
if not os.path.exists(folder_gifs):
    os.makedirs(folder_gifs)

# %% bubble map
fig = px.scatter_geo(df_exp_education_last_year, locations="Code",
                     hover_name="Entity", size="Government expenditure on education, total (% of GDP)",
                     projection="natural earth")

fig.write_image(folder_maps + "bubble_expenditure_education_PercentageGDP.png")

# %% choro maps

# we need geo data for the countries in order to color them based on their borders:
with open('../../Daten/countries.geojson') as f:
    gj = geojson.load(f)


# education

# draw figure
fig = px.choropleth(df_exp_education_last_year, locations='Code', color='Government expenditure on education, total (% of GDP)',
                           color_continuous_scale="OrRd", locationmode='ISO-3',
                           geojson=gj,range_color=(0, max(df_exp_education_last_year['Government expenditure on education, total (% of GDP)']))
                          )

# make the colorbar where it is supposed to be and a nice size 
fig.update_layout(coloraxis_colorbar=dict(
    title="",
    thicknessmode="pixels", thickness=20,
    lenmode="pixels", len=200
), 
    title_text='Government expenditure on education, total (% of GDP)' , title_x=0.5, title_y=.85
    )

# save figure
fig.write_image(folder_maps + "heatmap_expenditure_education_PercentageGDP.png")


# pop female
# draw figure
fig = px.choropleth(df_pop_female_last_year, locations='Code', color='Population, female (% of total population)',
                           color_continuous_scale="teal", locationmode='ISO-3',
                           geojson=gj,range_color=(min(df_pop_female_last_year['Population, female (% of total population)']), max(df_pop_female_last_year['Population, female (% of total population)']))
                          )

# make the colorbar where it is supposed to be and a nice size 
fig.update_layout(coloraxis_colorbar=dict(
    title="",
    thicknessmode="pixels", thickness=20,
    lenmode="pixels", len=200
), 
    title_text='Population, female (% of total population)' , title_x=0.5, title_y=.85
    )

fig.write_image(folder_maps + "heatmap_pop_females.png")



# development
fig = px.choropleth(df_development_last_year, locations='Code', color='Human Development Index (UNDP)',
                           color_continuous_scale="viridis", locationmode='ISO-3',
                           geojson=gj,range_color=(min(df_development_last_year['Human Development Index (UNDP)']), max(df_development_last_year['Human Development Index (UNDP)']))
                          )

# make the colorbar where it is supposed to be and a nice size 
fig.update_layout(coloraxis_colorbar=dict(
    title="",
    thicknessmode="pixels", thickness=20,
    lenmode="pixels", len=200
), 
    title_text='Human Development Index (UNDP)' , title_x=0.5, title_y=.85
    )

fig.write_image(folder_maps + "heatmap_developments.png")


# %% some animations:

# to use the dataframes we need the same years for all countries (data is missing). We fill all unknown data with nan
df = df_development.copy()

df = df[df['Year']>=1990]  # dont have much data from before

df['Year'] = pd.to_datetime(df['Year'], format='%Y')
df = (df.set_index(['Year','Code'])['Human Development Index (UNDP)']
        .unstack(fill_value=float('nan')).asfreq('YS', fill_value=float('nan')).unstack().reset_index())
df.rename({0:'Human Development Index (UNDP)'}, axis=1, inplace=True)

## to check if everything went ok
# number_countries = list(set(df['Code']))
# all_years = list(set(df['Year']))

# # how often years appear: 
# dict_year_appearances = {}
# for year in all_years:
#     dict_year_appearances[year]= list(df['Year']).count(year) 

df['Year'] = df['Year'].astype(str)  # chorpleth doesnt like the timestamps

fig = px.choropleth(df, locations='Code', color='Human Development Index (UNDP)',
                           color_continuous_scale="viridis", locationmode='ISO-3',
                           geojson=gj, animation_frame="Year",
                           range_color=(min(df['Human Development Index (UNDP)']), max(df['Human Development Index (UNDP)']))
                          )    
    
fig.write_html(folder_gifs + "heatmap_developments.html")

# deaths in covflicts per 100.000


list(df_deaths_conflicts.columns)
df_deaths_conflicts.rename({'Deaths - Conflict and terrorism - Sex: Both - Age: All Ages (Rate)':'Deaths - Conflict and terrorism'}, axis=1, inplace=True)

fig = px.choropleth(df_deaths_conflicts, locations='Code', color='Deaths - Conflict and terrorism',
                           color_continuous_scale="YlOrRd", locationmode='ISO-3',
                           geojson=gj, animation_frame="Year",
                           range_color=(min(df_deaths_conflicts['Deaths - Conflict and terrorism']), max(df_deaths_conflicts['Deaths - Conflict and terrorism'])/10)
                          )    
fig.update_traces(colorbar_ticksuffix='test')
# leg = ax1.get_legend()
# leg.get_texts()[0].set_text('New label 1')
# leg.get_texts()[1].set_text('New label 2')


    
fig.write_html(folder_gifs + "heatmap_deaths_conflicts.html")    

