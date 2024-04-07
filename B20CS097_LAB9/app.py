# Imports
import pandas as pd
import numpy as np
# Finance
import streamlit as sl
import yfinance as yf
from stocknews import StockNews as st
# Plotting
import plotly.express as ps
import plotly.graph_objs as go

# Calculate default dates
end = pd.Timestamp.today().date()
start = (end - pd.DateOffset(years=1)).date()
end = str(end.year) +"-"+str(end.month)+"-"+str(end.day)
start = str(start.year) +"-"+str(start.month)+"-"+str(start.day)

# Input Parameters
sl.title('Stock Price Monitoring Dashboard')
symb = sl.sidebar.text_input('Enter a Stock Symbol', 'GS') # Goldman Sachs Stock
Starting = sl.sidebar.date_input('Enter Start Date', value=pd.to_datetime(start))
Ending = sl.sidebar.date_input('Enter End Date', value=pd.to_datetime(end))
Sliding_window = sl.sidebar.slider('Moving Average Window', min_value=10, max_value=100, value=20, step=10)

# Data
yahoo_data = yf.download(symb, Starting, Ending)
temp_data = yahoo_data
average = temp_data['Adj Close'].rolling(window=Sliding_window)
temp_data[f'SMA_{Sliding_window}'] = average.mean()
working_days = 252

# Charts
plot_1 = ps.line(temp_data, x=temp_data.index, y=['Adj Close', f'SMA_{Sliding_window}'], title=f'{symb} - Closing Price (Adjusted)')
sl.plotly_chart(plot_1)

plot_2 = go.Figure(data=[go.Candlestick(x=yahoo_data.index, open=yahoo_data['Open'], high=yahoo_data['High'], low=yahoo_data['Low'], close=yahoo_data['Close'])])
plot_2.update_layout(title=f'{symb} - Candlestick Chart', xaxis_title='Date', yaxis_title='Price')
sl.plotly_chart(plot_2)

temp_data2 = yahoo_data
data_close = temp_data2['Adj Close']
temp_data2['Pct Change'] = data_close.pct_change()
temp_data2['Log Returns'] = np.log(data_close) - np.log(data_close.shift(1))
temp_data2['Cumulative Returns'] = (1 + temp_data2['Log Returns']).cumprod()
temp_data2.dropna(inplace=True)

plot_3 = ps.histogram(temp_data2, x='Pct Change', nbins=25, title=f'{symb} - Distribution of Return')
sl.plotly_chart(plot_3)

price_changes, news = sl.tabs(['Price Changes',  'News'])

with price_changes:
    sl.header('Price Changes')
    sl.write(temp_data2)
    yearly_return = (temp_data2['Pct Change'].mean()*working_days) # fraction
    std_dev = (temp_data2['Pct Change'].std()*np.sqrt(working_days)) # fraction 
    sl.write(f'Annual Returns:', round(yearly_return*(100), 1), '%')
    sl.write(f'Annual Standard Deviation:', round(std_dev*(100), 1), '%')
    sl.write(f'Sharpe Ratio:', round(yearly_return/std_dev, 1))

with news:
    sl.header(f'{symb} - Latest News')
    df_news = st(symb, save_news=False).read_rss()
    for k in range(3):
        sl.subheader(df_news['title'][k])
        sl.write(df_news['summary'][k])
        sl.write(df_news['published'][k])