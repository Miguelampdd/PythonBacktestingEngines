import pandas as pd
import datetime


#This file ensures there is no missing data on the time series concatenation.

df = pd.read_csv("/Users/miguelampudia/Desktop/BACKTESTING/BasicScripts/Gold(2024).csv")

df['dt'] = pd.to_datetime(df['time'], unit='s', utc=True)
df['dt_ny'] = df['dt'].dt.tz_convert('America/New_York')

# Extract NY date
df['date'] = df['dt_ny'].dt.date

# Get sorted unique dates
dates = sorted(df['date'].unique())

missing_calendar_days = []

for i in range(len(dates) - 1):
    current = dates[i]
    next_day = dates[i + 1]
    delta = (next_day - current).days

    if delta > 1:
        # Loop through all missing days in between
        for d in range(1, delta):
            missing_day = current + datetime.timedelta(days=d)

            # Skip Sundays (weekday() == 6 means Sunday if using dt.date; but Python: Monday=0, Sunday=6)
            if missing_day.weekday() in [5,6]:
                continue

            missing_calendar_days.append(missing_day)

print("Missing true days (excluding Sundays):", missing_calendar_days)

