import os
import sys

import matplotlib.dates as mdates
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yaml

from fund import utils

# stop warning me idc
pd.options.mode.chained_assignment = None

# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, os.getcwd())

# get config
with open("config.yml", "r") as file:
    fund_config = yaml.safe_load(file)["current_fund"]

st.set_page_config(layout="wide", page_title="Hourly Changes")
st.title("Fund Hourly Changes")

# get data
df = utils.sheet_to_df()
hourly = df["Time"].str.extract(rf"(:0[012])").dropna()

# draw time series
df_h = df.iloc[hourly.index]
df_h["tnum"] = mdates.datestr2num(df_h["Time"])
df_h["tnd"] = df_h["tnum"].diff()
df_h["Diff"] = df_h["Fund"].diff()
dfh_graph = df_h[df_h["tnd"].between(0.9 / 24, 1.1 / 24)].dropna()
dfh_graph = dfh_graph[dfh_graph["Diff"] < 250000]

trace = go.Scatter(
    x=dfh_graph["Time"],
    y=dfh_graph["Diff"],
    mode="lines+markers",
    name="Change in Past Hour",
)
fig = go.Figure([trace])

# avg
most_recent_time = mdates.datestr2num(df.iloc[-1, 0])
most_recent_value = df.iloc[-1, 1]
avg_change = most_recent_value / (
    24 * (most_recent_time - mdates.datestr2num(fund_config["start_date"]))
)
fig.add_hline(
    y=avg_change,
    line_color="gray",
    annotation_text=f"Avg Hourly Change: {np.round(avg_change, -2) / 10**3}k",
)

# layout
fig.update_xaxes(
    range=[fund_config["start_date"], utils.get_day()],
    rangeslider_visible=True,
    rangeselector=dict(
        buttons=list(
            [
                dict(count=1, label="1d", step="day", stepmode="backward"),
                dict(count=3, label="3d", step="day", stepmode="backward"),
                dict(count=7, label="1w", step="day", stepmode="backward"),
                dict(step="all"),
            ]
        )
    ),
)
fig.update_yaxes(range=[0, dfh_graph["Diff"].max() * 1.2])
fig.update_layout(
    title={"text": "Tanki Fund Hourly Changes", "x": 0.5, "xanchor": "center"},
    xaxis_title="Time (UTC)",
    yaxis_title="Change Since Past Hour",
    legend_title="Legend",
    showlegend=True,
    height=600,
)
with st.spinner("Loading Data..."):
    st.plotly_chart(fig, use_container_width=True, height=600)
