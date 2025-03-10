#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 16 11:53:58 2023

@author: JiM
plots site location of partners along the coast
Derived from plot_emolt_sites.py

"""

region='all' # other options are "all", "Maine", "Mass_DMF_sites", "Downeast", etc
border=0.1 # border in lat/lon coordinates to extend boundary
plt_filename='partners.png'

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
#import shapely.geometry as sgeom
import cartopy
import cartopy.crs as ccrs
import pandas as pd
import numpy as np
import matplotlib as mpl
from adjustText import adjust_text


df=pd.read_csv('partners.csv') # has numyears, syr, eyr, and numpts columns derived from "fix_emolt_sites.py"
df.rename(columns={'la': 'LAT','lo': 'LON'}, inplace=True)

lats=df['LAT'].values
lons=df['LON'].values


ax = plt.axes(projection=cartopy.crs.PlateCarree())
ax.add_feature(cartopy.feature.LAND,color='lightgray')
ax.add_feature(cartopy.feature.OCEAN,color='white')
#ax.add_feature(cartopy.feature.COASTLINE)
ax.add_feature(cartopy.feature.BORDERS, linestyle=':')
gls=ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False,color="None")
gls.top_labels=False   # suppress top labels
gls.right_labels=False

if plt_filename=='partners.png':
    ax.set_xlim([min(lons)-border,max(lons)+border])
    ax.set_ylim([min(lats)-border,max(lats)+border])
    ax.set_title('eMOLT partners along the coast')
    #plt.scatter(x=lons,y=lats,s=8,c='black',alpha=1)
    lnames=[]
    texts = []
    for i, row in df.iterrows():
            texts.append(ax.text(df['LON'][i],df['LAT'][i],df['p'][i], color="red", 
                                  ha='left',va='bottom', fontweight='bold',fontsize=8))#, path_effects=[pe.withStroke(linewidth=3,foreground="white")]))
            lnames.append(df['p'][i])
    adjust_text(texts)
plt.show()
plt.savefig(plt_filename)