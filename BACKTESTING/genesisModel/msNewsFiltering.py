import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
pd.set_option('display.max_columns', None)

df1 = pd.read_csv('msEDA(v1.1).csv')
# print(df1.head())
# print(df1.columns)

newsCols = ['news1','news2','news3']
newsLongFormat = (df1[newsCols].stack().dropna())
newsDummies = pd.get_dummies(newsLongFormat)
newsDummies = (newsDummies.groupby(level=0).max())
df = df1.join(newsDummies).fillna('FALSE')

df.to_csv('msEDA(news1).csv', index=False)

# print(df.head())

news_dummy_cols = [
    c for c in df.columns
    if c not in [
        'date','dayOfWeek','side','entryTime','entry_price',
        'exitTime','exit_price','sl','tp','exit_reason',
        'pnl_points','r_multiple','battingAvg',
        'news1','news2','news3']]


results = []

for news in news_dummy_cols:
    subset = df[df[news] == True]

    if len(subset) == 0:
        continue

    results.append({
        'news_event': news,
        'num_trades': len(subset),
        'r_multiple_sum': subset['r_multiple'].sum(),
        'battingAvg_mean': subset['battingAvg'].mean()})

news_performance = pd.DataFrame(results).sort_values(
    by='r_multiple_sum',
    ascending=False)


print(news_performance)

