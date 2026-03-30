import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
pd.set_option('display.max_columns', None)

df = pd.read_csv('msEDA(news1).csv')
vix = pd.read_csv('/Users/miguelampudia/Desktop/BACKTESTING/dataFiles/VIX(2023).csv')
df['date']  = pd.to_datetime(df['date'], format='mixed')
vix['date'] = pd.to_datetime(vix['date'], format='mixed')


merged = df.merge(vix, on='date', how='left')

merged.to_csv('msEDA(news1-VIX).csv', index=False)