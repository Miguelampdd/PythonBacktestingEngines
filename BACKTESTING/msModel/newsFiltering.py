import pandas as pd

pd.set_option('display.max_columns', None)
df1 = pd.read_csv('ms_pink_news.csv')


newsCols = ['news1','news2','news3']
newsLongFormat = (df1[newsCols].stack().dropna())
newsDummies = pd.get_dummies(newsLongFormat)
newsDummies = (newsDummies.groupby(level=0).max())
df = df1.join(newsDummies).fillna('FALSE')

df.to_csv('msW_News.csv', index=False)



news_dummy_cols = [
    c for c in df.columns
    if c not in [
        'date','dayOfWeek','side','entryTime','entry_price',
        'exitTime','exit_price','sl','tp','exit_reason',
        'pnl_points','return','wr',
        'news1','news2','news3', 'trade#','dow','return','wr']]


results = []

for news in news_dummy_cols:
    subset = df[df[news] == True]

    if len(subset) == 0:
        continue

    results.append({
        'news_event': news,
        'num_trades': len(subset),
        'r_multiple_sum': subset['return'].sum(),
        'wr': subset['wr'].mean()})

news_performance = pd.DataFrame(results).sort_values(
    by='r_multiple_sum',
    ascending=False)

# news_performance.to_csv('news_performance.csv')
# print(news_performance)