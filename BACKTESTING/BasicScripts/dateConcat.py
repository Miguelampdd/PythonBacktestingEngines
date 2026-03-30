import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


df = pd.read_csv('/Users/miguelampudia/Desktop/BACKTESTING/dataFiles/newsLog.csv')
pd.set_option('display.max_columns', None)

df[df[['year', 'month', 'day']].isna().any(axis=1)]

df = df.dropna(subset=['year', 'month', 'day'])


df['year'] = df['year'].astype(int)
df['month'] = df['month'].astype(int)
df['day'] = df['day'].astype(int)

df['date'] = pd.to_datetime(
    df['year'].astype(str) + '-' +
    df['month'].astype(str) + '-' +
    df['day'].astype(str),
    format='%Y-%m-%d')
df.drop(columns=['year', 'month', 'day'], inplace=True)

df.to_csv('newsLogCLEAN.csv', index=False)




# df = pd.read_csv('tradeLog.csv')