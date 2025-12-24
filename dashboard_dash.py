import dash
from dash import dcc, html, Input, Output
import plotly.graph_objs as go
import yfinance as yf
import pandas as pd

# Sample metadata for funds
fund_metadata = {
    'FCNTX': {
        'expense_ratio': 0.39, #From the fund website
        'sharpe_ratio': 3.60, #data from yfinance
        'std_dev': 18.83, #data from yfinance
        'net_asset_value': 22.07,  # Updated from fund website
        'top_holdings': [
            {'Holding': 'Meta Platforms Inc Cl A', 'Weight (%)': 15.74},
            {'Holding': 'Nvidia Corp', 'Weight (%)': 8.71},
            {'Holding': 'Berkshire Hathaway Inc Cl A', 'Weight (%)': 8.56},
            {'Holding': 'Amazon Inc', 'Weight (%)': 5.94},
            {'Holding': 'Microsoft Corp', 'Weight (%)': 5.49},
            {'Holding': 'Apple Inc', 'Weight (%)': 3.32},
            {'Holding': 'Eli Lilly & Co', 'Weight (%)': 2.90},
            {'Holding': 'Alphabet Inc Cl A', 'Weight (%)': 2.29},
            {'Holding': 'Netflix Inc', 'Weight (%)': 1.97},
            {'Holding': 'Alphabet Inc Cl C', 'Weight (%)': 1.88},
            {'Holding': 'Others', 'Weight (%)': 43.20},
        ],
        'sector_breakdown': {
            'Technology': 24.49,
            'Communication Services': 22.70,
            'Financial Services': 17.64,
            'Consumer Discretionary': 10.43,
            'Industrials': 10.20,
            'Healthcare': 18,
            'Industrials': 7.46,
            'Consumer Staples': 1.88,
            'Basic Materials': 1.45,
            'Energy': 1.33,
            'Utilities': 0.83,
            'Real Estate': 0.09,
            
        }
    },
    'VOO': {
        'expense_ratio': 0.03, # Updated from fund website
        'sharpe_ratio': 1.51, # Updated from yfinance
        'std_dev': 17.41, # Updated from yfinance
        'net_asset_value': 553.54,  # Updated from fund website
        'top_holdings': [
            {'Holding': 'Apple Inc.', 'Weight (%)': 7.12},
            {'Holding': 'Nvidia Corp', 'Weight (%)': 6.77},
            {'Holding': 'Microsoft Corp', 'Weight (%)': 6.26},
            {'Holding': 'Amazon Inc', 'Weight (%)': 3.61},
            {'Holding': 'Meta Platforms Inc', 'Weight (%)': 2.57},
            {'Holding': 'Alphabet Inc (GOOGL)', 'Weight (%)': 2.08},
            {'Holding': 'Alphabet Inc (GOOG)', 'Weight (%)': 1.72},
            {'Holding': 'Berkshire Hathaway', 'Weight (%)': 2.1},
            {'Holding': 'Broadcom Inc', 'Weight (%)': 1.64},
            {'Holding': 'Tesla Inc', 'Weight (%)': 1.44},
        ],
        'sector_breakdown': {
            'Technology': 33.02,
            'Financial Services': 12.89,
            'Healthcare': 11.18,
            'Consumer Discretionary': 10.21,
            'Communication Services': 9.11,
            'Industrials': 7.54,
            'Consumer Staples': 5.76,
            'Energy': 3.37,
            'Utilities': 2.70,
            'Real Estate': 2.28,
            'Basic Materials': 1.93
        }
    }
}

# Initialize the Dash app
app = dash.Dash(__name__)
app.title = "Compact Fund Dashboard"

# Layout
app.layout = html.Div([ 
    # Title
    html.H1("Comparative Analysis of Actively Managed Funds vs Benchmark Index Performance", style={'textAlign': 'left', 'font-size': '23px', 'color': 'white'}),

    # Dropdown for fund selection
    html.Div([ 
        html.Label("Select Fund", style={'font-size': '12px', 'color': 'black'}),
        dcc.Dropdown(
            id='fund-dropdown',
            options=[{'label': ticker, 'value': ticker} for ticker in fund_metadata.keys()],
            value='FCNTX',
            style={'width': '100%', 'font-size': '12px', 'margin': 'left', 'color': 'black', 'backgroundColor': '#f0f0f0'}
        )
    ], style={'margin-bottom': '60px', 'textAlign': 'left', 'width': '50%', 'backgroundColor': 'black'}),

    # Charts and tables (arranged in one row)
    html.Div([ 
        # Candlestick chart and fund details table in one column
        html.Div([ 
            # Candlestick chart (reduced height by 10%)
            dcc.Graph(id='candlestick-chart', style={'height': '350px'}),  # Adjust height here

            # Fund Details tiles below the chart (horizontal)
            html.Div([ 
                # Tile for Expense Ratio
                html.Div(
                    children=[
                        html.Div("Expense Ratio", style={'font-size': '20px', 'color': 'skyblue', 'margin-bottom': '10px', 'font-weight': 'bold'}),
                        html.Div(id='expense-ratio-tile', style={'font-size': '20px', 'font-weight': 'bold', 'color': 'white'})
                    ],
                    style={'backgroundColor': '#444', 'padding': '20px', 'border-radius': '10px', 'textAlign': 'center', 'flex': 1, 'margin': '5px'}
                ),
                # Tile for Sharpe Ratio / Information Ratio
                html.Div(
                    children=[
                        html.Div("Sharpe Ratio / Information Ratio", style={'font-size': '20px', 'color': 'skyblue', 'margin-bottom': '10px', 'font-weight': 'bold'}),
                        html.Div(id='sharpe-ratio-tile', style={'font-size': '20px', 'font-weight': 'bold', 'color': 'white'})
                    ],
                    style={'backgroundColor': '#444', 'padding': '20px', 'border-radius': '10px', 'textAlign': 'center', 'flex': 1, 'margin': '5px'}
                ),
                # Tile for Standard Deviation
                html.Div(
                    children=[
                        html.Div("Standard Deviation", style={'font-size': '20px', 'color': 'skyblue', 'margin-bottom': '10px', 'font-weight': 'bold'}),
                        html.Div(id='std-dev-tile', style={'font-size': '20px', 'font-weight': 'bold', 'color': 'white'})
                    ],
                    style={'backgroundColor': '#444', 'padding': '20px', 'border-radius': '10px', 'textAlign': 'center', 'flex': 1, 'margin': '5px'}
                ),
                # Tile for Net Asset Value (NAV)
                html.Div(
                    children=[
                        html.Div("Net Asset Value (NAV)", style={'font-size': '20px', 'color': 'skyblue', 'margin-bottom': '10px', 'font-weight': 'bold'}),
                        html.Div(id='nav-tile', style={'font-size': '20px', 'font-weight': 'bold', 'color': 'white'})
                    ],
                    style={'backgroundColor': '#444', 'padding': '20px', 'border-radius': '10px', 'textAlign': 'center', 'flex': 1, 'margin': '5px'}
                )
            ], style={'display': 'flex', 'flex-wrap': 'wrap', 'justify-content': 'space-between', 'margin-top': '20px'}), 

        ], style={'flex': '2', 'padding': '5px'}),

        # Fund details and charts
        html.Div([ 
            # Top Holdings Pie chart (no heading)
            dcc.Graph(id='top-holdings-pie-chart', style={'height': '270px'}),  # Reduced size

            # Sector Breakdown Pie chart (no heading)
            dcc.Graph(id='sector-breakdown-pie-chart', style={'height': '270px'}),  # Reduced size
        ], style={'flex': '1', 'margin-top': '-90px'})
    ], style={'display': 'flex', 'justify-content': 'center', 'margin-top': '-60px', 'backgroundColor': 'black'})
], style={'backgroundColor': 'black', 'color': 'white'})

# Callback for candlestick chart
@app.callback(
    Output('candlestick-chart', 'figure'),
    Input('fund-dropdown', 'value')
)
def update_candlestick_chart(selected_fund):
    # Define date range (1 year by default)
    end_date = pd.Timestamp.now()
    start_date = end_date - pd.DateOffset(years=1)
    
    # Fetch data from Yahoo Finance
    fund_data = yf.download(selected_fund, start=start_date, end=end_date)
    
    if fund_data.empty:
        return go.Figure()

    # Create candlestick chart
    fig = go.Figure(data=[go.Candlestick(
        x=fund_data.index,
        open=fund_data['Open'],
        high=fund_data['High'],
        low=fund_data['Low'],
        close=fund_data['Close'],
        name=selected_fund
    )])
    
    # Add range selector buttons
    fig.update_layout(
        title=f"{selected_fund} Candlestick Chart",
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        xaxis_rangeslider_visible=False,
        template="plotly_dark",  # Dark theme for the chart
        xaxis=dict(
            rangeselector=dict(
                buttons=[dict(count=1, label="1M", step="month", stepmode="backward"),
                         dict(count=6, label="6M", step="month", stepmode="backward"),
                         dict(count=1, label="1Y", step="year", stepmode="backward")],
                font=dict(color="black")  # Apply the color to the entire rangeselector
            ),
            rangeslider=dict(visible=False)
        )
    )
    
    return fig

# Callback for fund details and charts
@app.callback(
    [Output('expense-ratio-tile', 'children'),
     Output('sharpe-ratio-tile', 'children'),
     Output('std-dev-tile', 'children'),
     Output('nav-tile', 'children'),  # Updated callback here for NAV
     Output('top-holdings-pie-chart', 'figure'),
     Output('sector-breakdown-pie-chart', 'figure')],
    Input('fund-dropdown', 'value')
)
def update_fund_details(selected_fund):
    fund_info = fund_metadata[selected_fund]

    # Tile values
    return (
        f"{fund_info['expense_ratio']}%",
        f"{fund_info['sharpe_ratio']}",  # Updated here
        f"{fund_info['std_dev']}%",
        f"${fund_info['net_asset_value']}",  # Updated here for NAV
        # Top Holdings Pie chart
        go.Figure(data=[go.Pie(
            labels=[h['Holding'] for h in fund_info['top_holdings']],
            values=[h['Weight (%)'] for h in fund_info['top_holdings']],
            hole=0.3
        )]).update_layout(title="Top Holdings Distribution", template="plotly_dark"),
        # Sector Breakdown Pie chart
        go.Figure(data=[go.Pie(
            labels=list(fund_info['sector_breakdown'].keys()),
            values=list(fund_info['sector_breakdown'].values()),
            hole=0.3
        )]).update_layout(title="Sector Breakdown Distribution", template="plotly_dark")
    )

# Run app
if __name__ == '__main__':
    app.run_server(debug=True)
