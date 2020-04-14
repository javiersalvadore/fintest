from pandas_datareader import data
import os
from datetime import datetime
import pandas as pd

tickers = ['AMZN']
start_date = '2016-01-01'
end_date = '2017-01-01'
panel_data = data.DataReader(tickers,'av-daily',start=datetime(2016,1,1),end=datetime(2017,1,1),api_key='XJ01KSNKV21VWWSL')

print(panel_data.head(9))