import os, sys
import numpy as np
import pandas as pd
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
df_h["% Change"] = df_h["Fund"].pct_change(periods=24)
dfh_upd = df_h.dropna()
inc_24 = int(dfh_upd.iloc[-1, 2]) / 10 ** 3
inc_24_pct = str(np.round(dfh_upd.iloc[-1, 3] * 100, 3))

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Current Fund", value=f"{df.iloc[-1, 1] / 10 ** 6}M", delta=f"{(unique_funds.iloc[-1, 1] - unique_funds.iloc[-2, 1]) / 10 ** 3}K")

with col2:
    st.metric(label="Change in Past 24 Hours", value=f"{inc_24}K", delta=f"{inc_24_pct}%")

with col3:
    st.metric(label="Estimated Final Fund", value=f"{tracker.predict() / 10 ** 6}M")

st.header("Fund Daily Changes")


daily = df["Time"].str.extract(rf'(\s2:0[012]|\s1:5[789])').dropna()

# # draw time series
df_d = df.iloc[daily.index]
df_d["Day"] = list(range(1, df_d.shape[0] + 1))
df_d["Diff"] = np.round(df_d["Fund"].diff(), -1).fillna(0).astype(int)
df_d.loc[55, "Diff"] = df_d.loc[55, "Fund"].astype(int)
df_d["% Change"] = np.round(df_d["Diff"].pct_change().fillna(0) * 100, 3)
df_d["% Change"] = df_d["% Change"].apply(str)
df_d["% Change"] = df_d["% Change"].apply(utils.format_percent)
daily_final = df_d[["Day", "Diff", "% Change"]].set_index("Day")

st.dataframe(data=daily_final)