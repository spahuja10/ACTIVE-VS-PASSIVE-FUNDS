# -*- coding: utf-8 -*-
"""
Created on Sun Nov 24 17:56:32 2024

@author: saded
"""

import dash
from dash import dcc, html, Dash
from dash.dependencies import Input, Output
import yfinance as yf
import pandas as pd
import webbrowser
import threading
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from bs4 import BeautifulSoup


# Define tickers to compare
tickers = ['FCNTX', 'VOO']

# Fetch data for the tickers
start = '2014-11-01'
end = '2024-11-30'

# Download adjusted close price data
assets_data = yf.download(tickers, start=start, end=end, interval='1mo')['Adj Close']

# Calculate percentage change and drop NaN values
assets_data_pct = assets_data.pct_change() * 100
assets_data_pct = assets_data_pct.dropna()

# Resample the data to 6-month intervals and use 'last' to get the 6-month return
assets_data_6mo = assets_data_pct.resample('6ME').last()

# Create the figure
fig = go.Figure()

# Add traces for each ticker
colors = ['#636EFA', '#EF553B']  # Custom colors for the lines
for idx, ticker in enumerate(assets_data_6mo.columns):
    fig.add_trace(
        go.Scatter(
            x=assets_data_6mo.index,
            y=assets_data_6mo[ticker],
            mode='lines+markers',
            name=ticker,
            line=dict(color=colors[idx], width=2),
            marker=dict(size=6, symbol='circle')
        )
    )

# Add annotations for highest return for each ticker
for idx, ticker in enumerate(assets_data_6mo.columns):
    max_value = assets_data_6mo[ticker].max()
    max_date = assets_data_6mo[ticker].idxmax()
    fig.add_annotation(
        x=max_date,
        y=max_value,
        text=f"Max: {max_value:.2f}%",
        showarrow=True,
        arrowhead=2,
        ax=-30, ay=-30,
        font=dict(color=colors[idx])
    )

# Add buttons for selecting tickers
fig.update_layout(
    updatemenus=[
        dict(
            type="buttons",
            direction="left",
            buttons=[
                dict(label="All",
                     method="update",
                     args=[{"visible": [True, True]},
                           {"title": "FCNTX vs VOO Comparison"}]),
                dict(label="FCNTX",
                     method="update",
                     args=[{"visible": [True, False]},
                           {"title": "FCNTX Only"}]),
                dict(label="VOO",
                     method="update",
                     args=[{"visible": [False, True]},
                           {"title": "VOO Only"}]),
            ],
            pad={"r": 10, "t": 10},
            showactive=True,
            x=0.1,
            xanchor="left",
            y=1.15,
            yanchor="top"
        )
    ]
)

# Add range slider for date selection
fig.update_layout(
    xaxis=dict(
        rangeselector=dict(
            buttons=list([
                dict(count=6, label="6M", step="month", stepmode="backward"),
                dict(count=1, label="1Y", step="year", stepmode="backward"),
                dict(count=5, label="5Y", step="year", stepmode="backward"),
                dict(step="all")
            ])
        ),
        rangeslider=dict(visible=True),
        type="date"
    )
)

# Layout updates
fig.update_layout(
    title="FCNTX vs VOO 6-Month Return Performance",
    xaxis_title="Date",
    yaxis_title="Percentage Change",
    yaxis=dict(
        tickmode="linear",
        tick0=0,
        dtick=2,
        ticks="inside"
    ),
    hovermode="x unified",
    template="plotly_white"  # Use a clean theme
)

# Show the chart in a browser
fig.show(renderer="browser")


#%% - Pie chart 

file_path = "VOO_Top 10 Holdings.xlsx"
VOO_Top10_Holdings = pd.read_excel(file_path)

file_path1 = "FCNTX_Top 10 Holdings.xlsx"
FCNTX_Top10_Holdings = pd.read_excel(file_path1)

file_path2 = "FCNTX_Sector Breakdown.xlsx"
FCNTX_Sectorwise_Holdings = pd.read_excel(file_path2)

file_path3 = "VOO_Sector Breakdown.xlsx"
VOO_Sectorwise_Holdings = pd.read_excel(file_path3)

file_path4 = "Sectorwise_Returns.xlsx"
Returns_Sector = pd.read_excel(file_path4)


# Assuming the data contains 'Company' and 'Percentage' columns for the holdings
# Adjust column names to match the actual data in your Excel files
VOO_Holdings_Labels = VOO_Top10_Holdings['Top 10 Holdings']
VOO_Holdings_Sizes = VOO_Top10_Holdings['VOO']

FCNTX_Holdings_Labels = FCNTX_Top10_Holdings['Top 10 Holdings']
FCNTX_Holdings_Sizes = FCNTX_Top10_Holdings['FCNTX']

FCNTX_Sector_labels = FCNTX_Sectorwise_Holdings['Sectors']
FCNTX_Sector_sizes = FCNTX_Sectorwise_Holdings['FCNTX']

VOO_Sector_labels = VOO_Sectorwise_Holdings['Sectors']
VOO_Sector_sizes = VOO_Sectorwise_Holdings['VOO']


# Create a subplot with 1 row and 2 columns
fig = make_subplots(
    rows=1, cols=2, 
    specs=[[{'type': 'domain'}, {'type': 'domain'}]],
    subplot_titles=["VOO Top 10 Holdings", "FCNTX Top 10 Holdings"]
)

# Add VOO pie chart
fig.add_trace(
    go.Pie(
        labels=VOO_Holdings_Labels,
        values=VOO_Holdings_Sizes,
        hole=0.3,  # Creates a donut chart
        pull=[0.05] * len(VOO_Holdings_Labels)  # Slightly "explode" all slices
    ),
    row=1, col=1
)

# Add FCNTX pie chart
fig.add_trace(
    go.Pie(
        labels=FCNTX_Holdings_Labels,
        values=FCNTX_Holdings_Sizes,
        hole=0.3,  # Creates a donut chart
        pull=[0.05] * len(FCNTX_Holdings_Labels)  # Slightly "explode" all slices
    ),
    row=1, col=2
)

# Update layout
fig.update_layout(
    title_text="Comparison of VOO and FCNTX Top 10 Holdings",
    showlegend=True
)

# Show the combined chart in the browser
fig.show(renderer="browser")

# Create a subplot with two pie charts
fig = go.Figure()

# Add FCNTX pie chart
fig.add_trace(go.Pie(
    labels=FCNTX_Sector_labels,
    values=FCNTX_Sector_sizes,
    name="FCNTX",
    hole=0.4,  # Donut chart
    textinfo="percent",
    hoverinfo="label+percent+name"
))

# Add VOO pie chart
fig.add_trace(go.Pie(
    labels=VOO_Sector_labels,
    values=VOO_Sector_sizes,
    name="VOO",
    hole=0.4,  # Donut chart
    textinfo="percent",
    hoverinfo="label+percent+name"
))

# Update layout to display the charts side-by-side
fig.update_layout(
    title_text="Sector Breakdown: FCNTX vs VOO",
    annotations=[
        dict(text='FCNTX', x=0.20, y=0.5, font_size=20, showarrow=False),
        dict(text='VOO', x=0.80, y=0.5, font_size=20, showarrow=False)
    ],
    grid=dict(rows=1, columns=2),
    showlegend=True
)

# Adjust the subplot layout
fig.update_traces(domain=dict(x=[0, 0.5], y=[0, 1]), selector=dict(name="FCNTX"))
fig.update_traces(domain=dict(x=[0.5, 1], y=[0, 1]), selector=dict(name="VOO"))

# Show the chart in the browser
fig.show(renderer="browser")
#%%Comparison of Active and Passive holdings

VOO_Sectorwise_Holdings = VOO_Sectorwise_Holdings.sort_values(by = "Sectors", ascending = True)
VOO_Sectorwise_Holdings

 
FCNTX_Sectorwise_Holdings = FCNTX_Sectorwise_Holdings.sort_values(by="Sectors", ascending=True)
FCNTX_Sectorwise_Holdings


#Combining both
combined_data = pd.merge(VOO_Sectorwise_Holdings, FCNTX_Sectorwise_Holdings, on="Sectors", how="left")
combined_data


combined_data_returns= pd.merge(combined_data, Returns_Sector, on="Sectors", how="left")
combined_data_returns


combined_data_returns['VOO_Asset_Allocation'] = combined_data_returns['VOO'] * combined_data_returns['Returns']
combined_data_returns

combined_data_returns['FCNTX_Asset_Allocation'] = combined_data_returns['FCNTX'] * combined_data_returns['Returns']
combined_data_returns


total_voo_aa = combined_data_returns['VOO_Asset_Allocation'].sum()*100
total_voo_aa
total_fcntx_aa = combined_data_returns['FCNTX_Asset_Allocation'].sum()*100
total_fcntx_aa


asset_allocation_diff = total_fcntx_aa - total_voo_aa
asset_allocation_diff

fcntx_1y_returns = 35.97
voo_1y_returns = 30.86

active_returns = fcntx_1y_returns - voo_1y_returns
active_returns

security_selection = 6.17091100


asset_allocation = active_returns - security_selection
asset_allocation


#this tells that difference in the sector wise returns of passive and active 
#equity funds is equal to the asset allocation

