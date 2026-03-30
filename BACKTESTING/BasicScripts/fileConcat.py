import pandas as pd

#This file merges time-series files and orders them by time 

a = pd.read_csv('/Users/miguelampudia/Downloads/a.csv')
# b = pd.read_csv('/Users/miguelampudia/Downloads/b.csv')
# c = pd.read_csv('/Users/miguelampudia/Downloads/c.csv')
# d = pd.read_csv('/Users/miguelampudia/Downloads/d.csv')
# e = pd.read_csv('/Users/miguelampudia/Downloads/e.csv')
# f = pd.read_csv('/Users/miguelampudia/Downloads/f.csv')
# g = pd.read_csv('/Users/miguelampudia/Downloads/g.csv')
# h = pd.read_csv('/Users/miguelampudia/Downloads/h.csv')
# i = pd.read_csv('/Users/miguelampudia/Downloads/i.csv')
# j = pd.read_csv('/Users/miguelampudia/Downloads/j.csv')
# k = pd.read_csv('/Users/miguelampudia/Downloads/k.csv')
# l = pd.read_csv('/Users/miguelampudia/Downloads/l.csv')
# m = pd.read_csv('/Users/miguelampudia/Downloads/m.csv')
# n = pd.read_csv('/Users/miguelampudia/Downloads/n.csv')
# o = pd.read_csv('/Users/miguelampudia/Downloads/o.csv')
# p = pd.read_csv('/Users/miguelampudia/Downloads/p.csv')
# q = pd.read_csv('/Users/miguelampudia/Downloads/q.csv')
# r = pd.read_csv('/Users/miguelampudia/Downloads/r.csv')
# s = pd.read_csv('/Users/miguelampudia/Downloads/s.csv')
# t = pd.read_csv('/Users/miguelampudia/Downloads/t.csv')
# u = pd.read_csv('/Users/miguelampudia/Downloads/u.csv')
# v = pd.read_csv('/Users/miguelampudia/Downloads/v.csv')
# w = pd.read_csv('/Users/miguelampudia/Downloads/w.csv')
# x = pd.read_csv('/Users/miguelampudia/Downloads/x.csv')
# y = pd.read_csv('/Users/miguelampudia/Downloads/y.csv')
# z = pd.read_csv('/Users/miguelampudia/Downloads/z.csv')


# aa = pd.read_csv('/Users/miguelampudia/Downloads/aa.csv')
# ab = pd.read_csv('/Users/miguelampudia/Downloads/ab.csv')
# ac = pd.read_csv('/Users/miguelampudia/Downloads/ac.csv')
# ad = pd.read_csv('/Users/miguelampudia/Downloads/ad.csv')
# ae = pd.read_csv('/Users/miguelampudia/Downloads/ae.csv')
# af = pd.read_csv('/Users/miguelampudia/Downloads/af.csv')
# ag = pd.read_csv('/Users/miguelampudia/Downloads/ag.csv')
# ah = pd.read_csv('/Users/miguelampudia/Downloads/ah.csv')
# ai = pd.read_csv('/Users/miguelampudia/Downloads/ai.csv')
# aj = pd.read_csv('/Users/miguelampudia/Downloads/aj.csv')
# ak = pd.read_csv('/Users/miguelampudia/Downloads/ak.csv')
# al = pd.read_csv('/Users/miguelampudia/Downloads/al.csv')


merged = pd.concat([a])
merged = merged.drop_duplicates()
merged.columns = merged.columns.str.strip().str.lower()
merged = merged.sort_values(by='time', ascending=True)
merged['date'] = pd.to_datetime(merged['time'], unit='s').dt.tz_localize('America/New_York')
merged['date'] = merged['date'].dt.strftime('%Y-%m-%d-%H:%M')

# print(merged.head())

merge = merged.sort_values(by='time')
merge.to_csv("US100-D1.csv", index=False)

