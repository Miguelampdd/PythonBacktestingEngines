import pandas as pd
import numpy as np
from datetime import time as dtime
import random
from datetime import time

df = pd.read_csv("/Users/miguelampudia/Desktop/BACKTESTING/dataFiles/us100.csv") # until Nov 12th
pd.set_option('display.max_columns', None)

df['dt'] = pd.to_datetime(df['date'], format='%Y-%m-%d-%H:%M', utc=True)
df['dt'] = df['dt'].dt.tz_convert('America/New_York')

df.set_index('dt', inplace=True)
df.drop(columns=['time', 'date'], inplace=True)


# ===== SUPER SMOOTHER ====
#Reproduces the Ehlers SuperSmoother filter used Pine Script.
def ehlers_supersmoother(price: pd.Series, period: int) -> pd.Series:

    step = 2.0 * np.pi / period

    a1 = np.exp(-np.sqrt(2) * np.pi / period)
    b1 = 2 * a1 * np.cos(np.sqrt(2) * step / period)
    c2 = b1
    c3 = -a1 * a1
    c1 = 1 - c2 - c3

    ss = np.zeros(len(price))

    # iterate
    for i in range(len(price)):
        if i >= 2:
            ss[i] = c1 * (price.iloc[i] + price.iloc[i - 1]) / 2 + c2 * ss[i - 1] + c3 * ss[i - 2]
        else:
            ss[i] = price.iloc[i]

    return pd.Series(ss, index=price.index)

# ==== SMMA MAKER ====
def smma (series: pd.Series, length: int) -> pd.Series:
    smma_vals = np.full(len(series), np.nan)
    sma_init = series.rolling(length).mean()
    for i in range(len(series)):
        if i == length -1:
            smma_vals[i] = sma_init.iloc[i]
        elif i >= length:
            smma_vals[i] = (smma_vals[i-1]*(length-1) + series.iloc[i]) / length

    return pd.Series(smma_vals, index = series.index)




PRECOMP = {}
src = (df['open'] + df['high'] + df['low'] + df['close']) / 4

for length1 in [9, 10, 11, 12, 13]:
    s1 = ehlers_supersmoother(src, length1 * 3)
    s2 = ehlers_supersmoother(src, length1 * 2)
    s3 = ehlers_supersmoother(src, length1)
    PRECOMP[("SS", length1)] = (s1, s2, s3)

for lengthSMMA in [2, 3, 4]:
    PRECOMP[("SMMA", lengthSMMA)] = smma(src, lengthSMMA)

# =========================
# Strategy Hyper-Parameters
# =========================
SESSION_START = dtime(9, 30)
SESSION_END   = dtime(10, 59)
FORCE_CLOSE   = dtime(15, 30)
N_CONSEC = 4
SL_PCT   = 0.0011   # 0.11%
# TP_PCT   = SL_PCT * 2   # 0.22%
WORST_CASE_SAME_BAR = True
MTPS = 5
# ==== STRATEGY RANDOM SEARCH ====

def run_strategy( df,N_CONSEC, lengthSMMA, length1, SL_PCT, MTPS):

    TP_PCT = SL_PCT * 2.5

    df = df.copy()

    # ==== BANDS ====
    df['s1'], df['s2'], df['s3'] = PRECOMP[("SS", length1)]

    # === SMMA COLUMN ====
    df['SMMA'] = PRECOMP[("SMMA", lengthSMMA)]

    # ==== COLUMNS TO ENABLE TRADE ====
    # Trend alignment
    df['aligned_long'] = (df['s3'] > df['s2']) & (df['s2'] > df['s1'])
    df['aligned_short'] = (df['s3'] < df['s2']) & (df['s2'] < df['s1'])  # These two are correct

    # eligible bars for counting
    df['long_ok'] = df['aligned_long'] & (df['close'] > df['SMMA'])
    df['short_ok'] = df['aligned_short'] & (df['close'] < df['SMMA'])

    # group id increments whenever the condition is NOT true (i.e., streak breaks)
    g_long = (~df['long_ok']).cumsum()
    g_short = (~df['short_ok']).cumsum()

    # consecutive counts (1,2,3,...) during True streaks, else 0
    df['consec_long'] = df['long_ok'].astype(int).groupby(g_long).cumsum()
    df['consec_short'] = df['short_ok'].astype(int).groupby(g_short).cumsum()

    # Arming based on previous columns
    df['armed_long'] = df['consec_long'] >= N_CONSEC
    df['armed_long_prev'] = df['armed_long'].shift(1)

    df['armed_short'] = df['consec_short'] >= N_CONSEC
    df['armed_short_prev'] = df['armed_short'].shift(1)

    # SMMA filter
    df['touch_long'] = df['low'] <= df['SMMA']
    df['touch_short'] = df['high'] >= df['SMMA']

    # Entry window constrain
    df['in_entry_window'] = ((df.index.time >= SESSION_START) & (df.index.time <= SESSION_END))

    # Full entry signals (no trade)
    df['long_entry_signal'] = (
            df['armed_long_prev'] &
            df['touch_long'] &
            df['in_entry_window'])

    df['short_entry_signal'] = (
            df['armed_short_prev'] &
            df['touch_short'] &
            df['in_entry_window'])

    # =========================
    # ====  Backtest Loop  ====
    # =========================

    trades = []

    for session_date, day_df in df.groupby(df.index.date):

        in_trade = False
        trade_count = 0
        alignment_used_long = False
        alignment_used_short = False

        side = None
        entry_price = None
        entry_time = None
        sl = None
        tp = None

        # 3 goes here

        for dt, row in day_df.iterrows():
            t = dt.time()

            # =====================
            # MANAGE OPEN TRADE
            # =====================
            if in_trade:
                high = row['high']
                low = row['low']
                close = row['close']

                exit_reason = None
                exit_price = None

                if side == 'LONG':
                    hit_sl = low <= sl
                    hit_tp = high >= tp

                    if hit_sl and hit_tp:
                        exit_reason = 'SL_same_bar' if WORST_CASE_SAME_BAR else 'TP_same_bar'
                        exit_price = sl if WORST_CASE_SAME_BAR else tp
                    elif hit_sl:
                        exit_reason = 'SL'
                        exit_price = sl
                    elif hit_tp:
                        exit_reason = 'TP'
                        exit_price = tp

                elif side == 'SHORT':
                    hit_sl = high >= sl
                    hit_tp = low <= tp

                    if hit_sl and hit_tp:
                        exit_reason = 'SL_same_bar' if WORST_CASE_SAME_BAR else 'TP_same_bar'
                        exit_price = sl if WORST_CASE_SAME_BAR else tp
                    elif hit_sl:
                        exit_reason = 'SL'
                        exit_price = sl
                    elif hit_tp:
                        exit_reason = 'TP'
                        exit_price = tp

                # Force close at 15:30
                if exit_reason is None and t >= FORCE_CLOSE:
                    exit_reason = 'EOD'
                    exit_price = close

                if exit_reason is not None:
                    pnl = (exit_price - entry_price) if side == 'LONG' else (entry_price - exit_price)
                    r_mult = pnl / (entry_price * SL_PCT)

                    trades.append({
                        'date': session_date,
                        'side': side,
                        'entry_time': entry_time,
                        'entry_price': entry_price,
                        'exit_time': dt,
                        'exit_price': exit_price,
                        'sl': sl,
                        'tp': tp,
                        'exit_reason': exit_reason,
                        'pnl_points': pnl,
                        'r_multiple': r_mult
                    })

                    in_trade = False
                    side = None

                continue  # do NOT evaluate new entries while in trade

            # =====================
            # LOOK FOR ENTRY
            # =====================
            if not (SESSION_START <= t <= SESSION_END):
                continue

            if trade_count >= MTPS:
                continue

            if not row['aligned_long']:
                alignment_used_long = False

            if not row['aligned_short']:
                alignment_used_short = False

            # LONG ENTRY
            if row['long_entry_signal'] and not alignment_used_long:
                entry_price = row['SMMA']
                entry_time = dt
                sl = entry_price * (1 - SL_PCT)
                tp = entry_price * (1 + TP_PCT)

                in_trade = True
                side = 'LONG'
                trade_count += 1
                alignment_used_long = True
                continue

            # SHORT ENTRY
            if row['short_entry_signal'] and not alignment_used_short:
                entry_price = row['SMMA']
                entry_time = dt
                sl = entry_price * (1 + SL_PCT)
                tp = entry_price * (1 - TP_PCT)

                in_trade = True
                side = 'SHORT'
                trade_count += 1
                alignment_used_short = True
                continue

    return pd.DataFrame(trades)


PARAM_SPACE = { #remember that these MUST be the same as the ones specified in the blocks that define them above
    "N_CONSEC": [4, 5],
    "lengthSMMA": [2, 3, 4,],
    "length1": [9, 10, 11, 12, 13],
    "SL_PCT": [0.0007, 0.0008, 0.0009, 0.0010],
    "MTPS": [2, 3, 4]
}

N_ITER = 10
from joblib import Parallel, delayed

# build random param dicts
sampled_params = [
    {k: random.choice(v) for k, v in PARAM_SPACE.items()}
    for _ in range(N_ITER)
]

def eval_params(params):
    trades_df = run_strategy(df, **params)
    n_trades = len(trades_df)
    if n_trades < 1000:
        return None

    win_rate = (trades_df['pnl_points'] > 0).mean()
    avg_r = trades_df['r_multiple'].mean()

    if win_rate < 0.30 or avg_r <= 0:
        return None

    return {**params, "trades": n_trades, "win_rate": win_rate, "avg_r": avg_r}

raw = Parallel(n_jobs=10)(
    delayed(eval_params)(p) for p in sampled_params
)

results = [r for r in raw if r is not None]
results_df = pd.DataFrame(results).sort_values("avg_r", ascending=False)
results_df.to_csv("random_search_results.csv", index=False)







# dfT = df.tail(900)
# dfT.to_csv("entry_signal_audit(v5.0).csv")



 #MAX_TRADES_PER_SESSION



# trades_df = pd.DataFrame(trades)

# trades_df.to_csv("trade_log(v2.1).csv", index=False)




















# =MID(A2,12,5)

# Tenemos que hacer una columna que indique cuanto precio hay de desplazamiento en % para saber si despues de tantos
#   cierta cantidad de puntos nos conviene mejor no tomar la operacion.
#random or grid search, maybe bayesion optimization hyperparameter tunning.