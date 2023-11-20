import os, sys
import datetime
from matplotlib.backend_bases import FigureManagerBase
import numpy as np
import pandas as pd
import matplotlib.dates as mdates
import streamlit as st

from fund import utils, tracker

# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, os.getcwd())

st.set_page_config(page_title="Analytics")
st.title('Fund Analytics')

df = utils.sheet_to_df()
unique_funds = df.sort_values("Time", ascending=True).drop_duplicates(subset=["Fund"]).sort_values("Fund", ascending=True)
hourly = df["Time"].str.extract(rf'(:0[012])').dropna()
cur_time, cur_fund = df.iloc[-1]

st.write(f"Last Updated: {cur_time}")

st.header("At a Glance")

# diffing
df_h = df.iloc[hourly.index]
df_h["Diff"] = df_h["Fund"].diff(periods=24)
df_h["% Change"] = df_h["Diff"].pct_change()
dfh_upd = df_h.dropna()
inc_24 = int(dfh_upd.iloc[-1, 2]) / 10 ** 3
inc_24_pct = str(np.round(dfh_upd.iloc[-1, 3] * 100, 3))
final_pred = int(np.round(tracker.predict(35, newton=False), -3)) / 10 ** 6

col1, col2, col3 = st.columns(3)

cfund = df.iloc[-1, 1] / 10 ** 6

with col1:
    st.metric(label="Current Fund", value=f"{cfund}M", delta=f"{(unique_funds.iloc[-1, 1] - unique_funds.iloc[-2, 1]) / 10 ** 3}K")

with col2:
    try:
        st.metric(label="Change in Past 24 Hours", value=f"{inc_24}K", delta=f"{inc_24_pct}%")
    except:
        st.metric(label="Change in Past 24 Hours", value="N/A", delta="N/A")

with col3:
    if final_pred > max(tracker.CHECKPOINTS.keys()) * 3:
        final_pred_value = "N/A"
    else: 
        final_pred_value = f"{final_pred}M"
    st.metric(label="Estimated Final Fund", value=final_pred_value)

st.header("Checkpoint Info")
st.info("Note: Estimated end checkpoint denotes the estimated major checkpoint; we don't care about Mono Apple in this household.")

# get checkpoint information
checknums = list(tracker.CHECKPOINTS.keys())
idx = 0
while checknums[idx] < cfund:
    idx += 1
next_checkpoint = tracker.CHECKPOINTS[checknums[idx]]

final_idx = 0
while checknums[final_idx] < final_pred:
    final_idx += 1
final_checkpoint = tracker.CHECKPOINTS[checknums[final_idx]]

cur_day_num = np.ceil(mdates.date2num(utils.get_day()) - tracker.X_SHIFT)
next_week_pred = int(np.round(tracker.predict(cur_day_num + 7, newton=False), -3)) / 10 ** 6
if cfund >= max(tracker.CHECKPOINTS.keys()) or int(next_week_pred) <= checknums[idx]:
    cdelta = "N/A"
else:
    cdelta = tracker.tdelta_format(mdates.num2date(tracker.newton() + tracker.X_SHIFT).replace(tzinfo=datetime.timezone.utc) - datetime.datetime.now().replace(tzinfo=datetime.timezone.utc))

col1, col2, col3 = st.columns(3)

with st.spinner('Loading Checkpoint Information...'):
    with col1:
        st.metric(label="Next Checkpoint", value=next_checkpoint)

    with col2:
        st.metric(label="Est. Time To Reach", value=f"{cdelta}")

    with col3:
        if final_pred > max(tracker.CHECKPOINTS.keys()) * 3:
            final_checkpoint = "N/A"
        else:
            final_checkpoint = f"{tracker.CHECKPOINTS[min(checknums[final_idx], max(tracker.CHECKPOINTS.keys()))]}"
        st.metric(label="Est. End Checkpoint", value=final_checkpoint)

st.header("Fund Daily Changes")

try:
# get daily
    daily = df["Time"].str.extract(rf'(\s2:0[012]|\s1:5[789])').dropna()
# # draw time series
    df_d = df.iloc[daily.index]
    df_d["Day"] = list(range(1, df_d.shape[0] + 1))
    df_d["Diff"] = np.round(df_d["Fund"].diff(), -1).fillna(0).astype(int)
    df_d["% Change"] = np.round(df_d["Diff"].pct_change().fillna(0) * 100, 3)
    df_d["% Change"] = df_d["% Change"].apply(str)
    df_d["% Change"] = df_d["% Change"].apply(utils.format_percent)
    daily_final = df_d[["Day", "Diff", "% Change"]].set_index("Day")
    # for w23 only:
    st.info("Note: fund data was not collected on the first day, so the first two days' daily changes are not completely accurate.")
    # END for w23 only
    st.dataframe(data=daily_final)
except:
    st.write("Coming soon!")
    pass
