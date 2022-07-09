import numpy as np
import pandas as pd
import plotly.graph_objects as go
from fund import utils, tracker

df = utils.sheet_to_df()
hourly = df["Time"].str.extract(rf'(:0[012])').dropna()
print(df.iloc[-1])
cur_time, cur_fund = df.iloc[-1]

# diffing
df_h = df.iloc[hourly.index]
df_h["Diff"] = df_h["Fund"].diff(periods=24)
df_h["% Change"] = df_h["Fund"].pct_change(periods=24)
dfh_upd = df_h.dropna()
inc_24 = int(dfh_upd.iloc[-1, 2]) / 10 ** 3
inc_24_pct = utils.format_percent(str(np.round(dfh_upd.iloc[-1, 3] * 100, 3)))