# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.15.2
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Boston Weather

# %% [markdown]
# # Setup
# First, import what we need.

# %%
import math
import altair as alt
from altair import datum
import pandas as pd
import numpy as np
from ipywidgets import interact, interactive, fixed, interact_manual
import ipywidgets as widgets
from vega_datasets import data

# %% [markdown]
# Then, check versions of installed packages.

# %%
'ipywidgets ' + widgets.__version__ + ', altair ' + alt.__version__ + ', pandas ' + pd.__version__ + ', numpy ' + np.__version__

# %% [markdown]
# Allow Altair to use more than 5000 rows

# %%
alt.data_transformers.enable("vegafusion")

# %% [markdown]
# ## Weather

# %%
bostonWeatherDF = pd.read_csv('boston-weather-mid.csv')
bostonWeatherDF

# %% [markdown]
# Data from [Weather.gov NOWData](https://www.weather.gov/wrh/Climate?wfo=box). Extracted monthly summary data `por`–`2023`, replaced "T" and "M" with blank for the missing data, loaded in PowerQuery to unpivot months then to pivot measure.

# %%
monthOrder = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
yearsInData=[bostonWeatherDF['year'].min(), bostonWeatherDF['year'].max()]
tempsInData=[bostonWeatherDF['meanTemp'].min(), bostonWeatherDF['meanTemp'].max()]


# %%
@interact(years=widgets.IntRangeSlider(
    value=yearsInData,
    min=yearsInData[0],
    max=yearsInData[1],
    step=1,
    description='Years:'
))
def tempMonthChangeOverTimeChart(years):    
    return alt.Chart(
        bostonWeatherDF, 
        title=alt.Title(
            'How the Boston temperatures for each month have changed over time',
            subtitle='A comparison of ' + str(years[0]) + '–' + str(years[1])
        )
    ).transform_filter(
        ((datum.year >= years[0]) & (datum.year <= years[1]))
    ).encode(
        color=alt.Color('year', scale=alt.Scale(scheme='lightgreyred', domain=yearsInData), sort='ascending')
    ).mark_line(point=True).encode(
        x=alt.X('month:O').sort(monthOrder),
        y=alt.Y('meanTemp:Q',  title='mean monthly temp in ⁰F', scale=alt.Scale(domain=tempsInData)),
        tooltip=['year', 'meanTemp'],
        opacity=alt.value(.3)
    ).properties(
        width=600,
        height=600
    )


# %%
@interact(month=widgets.Dropdown(
    options=monthOrder,
    value='Aug',
    description='Month:',
))
def tempYearChangeOverTimeChart(month):

    brush = alt.selection_interval(encodings=['x'])
    
    colorChart = alt.Chart(
        title=alt.Title(
            'How the Boston ' + month + ' temperature has changed over time',
            subtitle='A comparison of ' + str(yearsInData[0]) + '–' + str(yearsInData[1]) + ' with interactive selection mean across years'
        )
    ).encode(
        color=alt.Color('year', scale=alt.Scale(scheme='lightgreyred')),
    ).add_params(
        brush
    )

    points = colorChart.mark_point().encode(
        x=alt.X('year:Q', scale=alt.Scale(zero=False)),
        y=alt.Y('meanTemp:Q', title='mean monthly temp in ⁰F', scale=alt.Scale(zero=False)),
        tooltip=['year', 'maxTemp', 'meanTemp', 'minTemp', 'CDDBase65']        
    )

    meanLine = alt.Chart().mark_rule(color='firebrick').encode(
        y=alt.Y('mean(meanTemp):Q', scale=alt.Scale(zero=False)),
        size=alt.SizeValue(3)
    ).transform_filter(
        brush
    )

    tempScatter = alt.layer(points, meanLine, data=bostonWeatherDF).transform_filter(
        (datum.month == month)
    )
    
    return tempScatter.properties(
        width=600,
        height=300
    )


# %%
@interact(month=widgets.Dropdown(
    options=monthOrder,
    value='Aug',
    description='Month:',
))
def tempScatter(month):

    
    colorChart = alt.Chart(
        bostonWeatherDF, 
        title=alt.Title(
            'Cooling Degree Days Base 65 score for ' + month + ' over the years',
            subtitle="A comparison of 1872–2023"
        )
    ).transform_filter(
        (datum.month == month)
    ).encode(
        color=alt.Color('year', scale=alt.Scale(scheme='lightgreyred'))
    )
    
    lines = colorChart.mark_point().encode(
        x=alt.X('year:Q', scale=alt.Scale(zero=False)),
        y=alt.Y('CDDBase65:Q', scale=alt.Scale(zero=False)),
        tooltip=['year', 'maxTemp', 'meanTemp', 'minTemp', 'CDDBase65']        
    )

    tempScatter=lines.properties(
        width=600,
        height=300
    )

    return tempScatter
