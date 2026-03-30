import pandas as pd
import pandas_datareader as web
from datetime import  datetime
import matplotlib.pyplot as plt
from matplotlib.pyplot import legend
dateStart = "2023-01-01"
dateEnd = "2025-11-11"

#get bond ETF as ETF
VIX = web.DataReader('VIX', data_source='stooq', start=dateStart , end=dateEnd)

VIX.to_csv('/Users/miguelampudia/Downloads/VIX.csv')