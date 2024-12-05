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

# stop warning me
pd.options.mode.chained_assignment = None 

st.set_page_config(page_title="Analytics")
st.title('Fund Analytics')

df = utils.sheet_to_df()
unique_funds = df.sort_values("Time", ascending=True).drop_duplicates(subset=["Fund"]).sort_values("Fund", ascending=True)
hourly = df["Time"].str.extract(rf'(:0[012])').dropna()
cur_time, cur_fund = df.iloc[-1]

st.write(f"Last Updated: {cur_time}")

st.header("At a Glance")
st.caption("Final Prediction may be extreme with little data at first; the value will be omitted for the beginning of the fund. In case of further extreme behavior, a value of N/A will be put in place of values that are either negative or severely infeasible.")

# diffing
df_h = df.iloc[hourly.index]
df_h["Diff"] = df_h["Fund"].diff(periods=24)
df_h["% Change"] = df_h["Diff"].pct_change()
dfh_upd = df_h.dropna()

try: 
    inc_24 = int(dfh_upd.iloc[-1, 2]) / 10 ** 3
    inc_24_pct = str(np.round(dfh_upd.iloc[-1, 3] * 100, 3))
except:
    inc_24, inc_24_pct = None, None 

final_pred = int(np.round(tracker.predict(28, newton=False), -3)) / 10 ** 6

col1, col2, col3 = st.columns(3)

cfund = df.iloc[-1, 1] / 10 ** 6
cfund_delta = (unique_funds.iloc[-1, 1] - unique_funds.iloc[-2, 1]) / 10 ** 3

if inc_24 and inc_24 > 1000 and float(inc_24_pct) > 10:
    st.info("The fund is growing quickly right now!", icon="📈")

with col1:
    if cfund < 1:
        st.metric(label="Current Fund", value=f"{cfund * 1000}K", delta=f"{cfund_delta}K")
    else:
        st.metric(label="Current Fund", value=f"{cfund}M", delta=f"{cfund_delta}K")

with col2:
    if inc_24 and inc_24_pct:
        st.metric(label="Change in Past 24 Hours", value=f"{inc_24}K", delta=f"{inc_24_pct}%")
    else:
        st.metric(label="Change in Past 24 Hours", value="N/A", delta="N/A")

with col3:
    cutoff_date = tracker.START_DATE + datetime.timedelta(days=3)
    if final_pred < 0 or datetime.datetime.now() < cutoff_date or final_pred > max(tracker.CHECKPOINTS.keys()) * 1.5:
        final_pred_value = "N/A"
    else: 
        final_pred_value = f"{final_pred}M"
    st.metric(label="Estimated Final Fund", value=final_pred_value)


st.header("Checkpoint Info")
st.caption("Estimated end checkpoint denotes the estimated major checkpoint; we don't care about Mono Apple in this household.")

try:
    # get checkpoint information
    checknums = list(tracker.CHECKPOINTS.keys())
    idx = 0
    while checknums[idx] < cfund:
        idx += 1
    next_checkpoint = tracker.CHECKPOINTS[checknums[idx]]

    final_idx = 0
    if final_pred > checknums[-1]:
        final_checkpoint = tracker.CHECKPOINTS[checknums[-1]]
    else:
        while checknums[final_idx] < final_pred:
            final_idx += 1
        final_checkpoint = tracker.CHECKPOINTS[checknums[final_idx-1]]

    col1, col2, col3 = st.columns(3)

    cur_day_num = np.ceil(mdates.date2num(utils.get_day()) - tracker.X_SHIFT)
    next_week_pred = int(np.round(tracker.predict(cur_day_num + 7, newton=False), -3)) / 10 ** 6
    if cfund >= max(tracker.CHECKPOINTS.keys()):
        cdelta = "N/A"
    elif int(next_week_pred) <= checknums[idx]:
        cdelta = ">1w"
    else:
        cdelta_raw = mdates.num2date(tracker.newton() + tracker.X_SHIFT).replace(tzinfo=datetime.timezone.utc) - datetime.datetime.now().replace(tzinfo=datetime.timezone.utc)
        cdelta = tracker.tdelta_format(cdelta_raw)
        if cdelta_raw.total_seconds() < 12 * 3600:
            st.info("We are about to hit the next checkpoint soon!", icon="🔥")

    with st.spinner('Loading Checkpoint Information...'):
        with col1:
            st.metric(label="Next Checkpoint", value=next_checkpoint)

        with col2:
            st.metric(label="Est. Time To Reach", value=f"{cdelta}")

        with col3 :
            if final_pred < 0 or final_pred > max(tracker.CHECKPOINTS.keys()) * 3:
                final_checkpoint = "N/A"
            else:
                final_checkpoint = f"{tracker.CHECKPOINTS[min(checknums[final_idx-1], max(tracker.CHECKPOINTS.keys()))]}"
            st.metric(label="Est. End Checkpoint", value=final_checkpoint)
except:
    st.write("Coming soon!")
    pass

st.header("Fund Daily Changes")

try:
    # get daily
    daily = df["Time"].str.extract(rf'(\s2:0[012]|\s1:5[789])').dropna()
    print(daily)
    # draw time series
    df_d = df.iloc[daily.index]
    print(df_d)
    df_d["Day"] = list(range(df_d.shape[0]))
    df_d["Diff"] = np.round(df_d["Fund"].diff(), -1).fillna(0).astype(int)
    df_d["% Change"] = np.round(df_d["Diff"].pct_change().fillna(0) * 100, 3)
    df_d["% Change"] = df_d["% Change"].apply(str)
    df_d["% Change"] = df_d["% Change"].apply(utils.format_percent)
    daily_final = df_d[["Day", "Diff", "% Change"]].set_index("Day").iloc[1:]
    print(daily_final)
    if daily_final.size > 0:
        st.dataframe(data=daily_final)
    else:
        st.write("Coming soon!")
except:
    st.write("Coming soon!")
    pass
