#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar  9 07:17:02 2025

@author: JiM taken directly from web example
requires a "task.csv" file with various tasks
requires, in my case, to issue "conda install altair" from the anaconda3/condabin folder
"""

output_filename='emolt_gantt.html'

import pandas as pd
import numpy as np
import altair as alt
# alt.renderers.enable('notebook') # if in jupyter

df = pd.read_csv("tasks.csv")
df["Start date"] = pd.to_datetime(df["Start date"])
df["End date"] = pd.to_datetime(df["End date"])

chart = alt.Chart(df.drop('Probe',axis=1)).mark_bar().encode(
    x='Years',
    x2='',
    y=alt.Y('Funding', 
            sort=list(df.sort_values(["End date", "Start date"])
                                    ["Funding"])), # Custom sorting
)

chart.save(output_filename)# brought this into chrome and then saved as png
