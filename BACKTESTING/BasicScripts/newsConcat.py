
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

import pandas as pd
pd.set_option('display.max_columns', None)

newsLog = pd.read_csv("/Users/miguelampudia/Desktop/BACKTESTING/dataFiles/newsLog.csv")
tradeLog   = pd.read_csv("/Users/miguelampudia/Desktop/BACKTESTING/genesisGold_m/finalTradeLog.csv")

# print(newsLog.columns)
# print(tradeLog.columns)

newsLog['date'] = pd.to_datetime(newsLog['date'])
tradeLog['date'] = pd.to_datetime(tradeLog['date'])

newsLog['date']  = newsLog['date'].dt.date
tradeLog['date'] = tradeLog['date'].dt.date

merged = tradeLog.merge(newsLog, on='date', how='left')

merged.to_csv('ms_gold_news.csv', index=False)
# print(tradeLog.head(10))
# print(newsLog.head(10))
