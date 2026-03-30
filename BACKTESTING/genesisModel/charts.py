import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates
pd.set_option('display.max_columns', None)

df = pd.read_csv('msFinalLog.csv')
# print(df.head(5))
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df = df.sort_values('date')
# print(df['date'].min(), df['date'].max())



df = df.sort_values('date')
df['cum_R'] = df['r_multiple'].cumsum()
df['cum_max'] = df['cum_R'].cummax()
df['drawdown'] = df['cum_R'] - df['cum_max']



# ===== EQUITY CURVE ======

# plt.figure(figsize=(10,5))
# plt.plot(df['date'], df['cum_R'])
# plt.xlabel('Date')
# plt.ylabel('Cumulative R')
# plt.title('Equity Curve (Cumulative R)')
# plt.grid(True)
# plt.show()



# ===== DRAWDOWN CURVE =====

# fig, ax = plt.subplots(figsize=(18,4))
#
# ax.plot(df['date'], df['drawdown'])
# ax.set_ylabel('Drawdown (R)')
# ax.set_title('Drawdown Curve')
#
# # Monthly ticks
# ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))  # every 3 months
# ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
#
# ax.set_xlim(df['date'].min(), df['date'].max())
# ax.grid(True)
#
# plt.show()



# ===== WR by DOW =====

# wr_by_day = (
#     df.groupby('dayOfWeek')['battingAvg']
#       .mean()
#       .rename('win_rate')
#       .reset_index())
#
#
# day_map = {1:'Mon', 2:'Tue', 3:'Wed', 4:'Thu', 5:'Fri'}
# wr_by_day['day'] = wr_by_day['dayOfWeek'].map(day_map)
#
#
#
# plt.figure(figsize=(8,5))
# plt.bar(wr_by_day['day'], wr_by_day['win_rate'])
#
# plt.ylabel('Win Rate')
# plt.xlabel('Day of Week')
# plt.title('Win Rate by Day of Week')
# plt.ylim(0, 1)
# plt.grid(axis='y')
#
# plt.show()



# ===== TOTAL R PER MONTH =====

df['month'] = df['date'].dt.to_period('M')
monthly_R = (
    df.groupby('month')['r_multiple']
      .sum()
      .reset_index()
)

monthly_R['month'] = monthly_R['month'].astype(str)

#
# plt.figure(figsize=(10,4))
# plt.bar(monthly_R['month'], monthly_R['r_multiple'])
#
# plt.xlabel('Month')
# plt.ylabel('Total R')
# plt.title('Total R per Month')
# plt.axhline(0)
#
# plt.xticks(rotation=45)
# plt.grid(axis='y')
#
# plt.show()



# ===== RETURN BY 10-MINUTE HEATMAP =====

df['date'] = pd.to_datetime(df['date'], format='%m/%d/%y')


df['time_10m_label'] = (
    pd.to_datetime(df['entryTime'], format='%H:%M')
      .dt.floor('10min')
      .dt.strftime('%H:%M')
)

trade_counts = df.pivot_table(
    values='r_multiple',
    index='dayOfWeek',
    columns='time_10m_label',
    aggfunc='count'
)

entry_dt = pd.to_datetime(df['entryTime'], format='%H:%M')


heatmap_data = df.pivot_table(
    values='r_multiple',
    index='dayOfWeek',
    columns='time_10m_label',
    aggfunc='mean'
)




day_map = {1:'Mon', 2:'Tue', 3:'Wed', 4:'Thu', 5:'Fri'}
heatmap_data.index = heatmap_data.index.map(day_map)


fig, ax = plt.subplots(figsize=(12,7))

im = ax.imshow(heatmap_data, aspect='auto')
plt.colorbar(im, ax=ax, label='Avg R')

ax.set_xticks(range(len(heatmap_data.columns)))
ax.set_xticklabels(heatmap_data.columns, rotation=45)

ax.set_yticks(range(len(heatmap_data.index)))
ax.set_yticklabels(heatmap_data.index)

# Overlay trade counts
for i in range(heatmap_data.shape[0]):
    for j in range(heatmap_data.shape[1]):
        count = trade_counts.iloc[i, j]
        if not pd.isna(count) and count > 0:
            ax.text(
                j, i,
                int(count),
                ha='center',
                va='center',
                fontsize=8,
                color='black'
            )

ax.set_xlabel('Time (10-minute bins)')
ax.set_ylabel('Day of Week')
ax.set_title('Avg R by Day and 10-Minute Window (Counts Annotated)')

plt.show()

