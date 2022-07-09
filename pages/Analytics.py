import os, sys
import numpy as np
import pandas as pd
import streamlit as st

from fund import utils, tracker

# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, os.getcwd())

#
st.title('Fund Analytics')

st.header("At a Glance")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Current Fund", value="X M", delta="50k")

with col2:
    st.metric(label="Change in Past 24 Hours", value="Y K", delta="-25%")

with col3:
    st.metric(label="Estimated Final Fund", value="Z M")

st.header("Fund Daily Changes")

df = utils.sheet_to_df()
daily = df["Time"].str.extract(rf'(\s2:0[012]|\s1:5[789])').dropna()

# # draw time series
df_d = df.iloc[daily.index]
df_d["Day"] = list(range(1, df_d.shape[0] + 1))
df_d["Diff"] = np.round(df_d["Fund"].diff(), -1).fillna(0).astype(int)
df_d.loc[55, "Diff"] = df_d.loc[55, "Fund"].astype(int)
df_d["% Change"] = np.round(df_d["Diff"].pct_change().fillna(0) * 100, 3)

# format
def format_percent(string):
    if string == "0":
        return "-"
    elif string[0] == "-":
        return f"\u2193 {string}%"
    else:
        return f"\u2191 {string}%"

df_d["% Change"] = df_d["% Change"].apply(str)
df_d["% Change"] = df_d["% Change"].apply(format_percent)
daily_final = df_d[["Day", "Diff", "% Change"]].set_index("Day")

st.dataframe(data=daily_final)