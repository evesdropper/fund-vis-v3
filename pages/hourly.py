import os, sys
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from fund import utils, tracker

# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, os.getcwd())
st.set_page_config(layout="wide", page_title="Hourly Changes")
st.title('Fund Hourly Changes')

# get data
df = utils.sheet_to_df()
hourly = df["Time"].str.extract(rf'(:0[012])').dropna()

# draw time series
df_h = df.iloc[hourly.index]
diff_series = df_h["Fund"].diff()
df_h["Diff"] = diff_series
dfh_graph = df_h.dropna()
avg_change = dfh_graph["Diff"].mean()

trace = go.Scatter(x=dfh_graph["Time"], y=dfh_graph["Diff"], mode="lines+markers", name="Change in Past Hour")
fig = go.Figure([trace])

# avg
fig.add_hline(y=avg_change, line_color="gray", annotation_text=f"Avg Hourly Change: {np.round(avg_change, -2) / 10 ** 3}k")

# layout
fig.update_xaxes(range=[tracker.START_DATE, utils.get_day()])
fig.update_yaxes(range=[0, dfh_graph["Diff"].max() * 1.2])
fig.update_layout(
    title={"text": "Tanki Fund Hourly Changes", 'x':0.5, 'xanchor': 'center'},
    xaxis_title="Time (UTC)",
    yaxis_title="Change Since Past Hour",
    legend_title="Legend",
    showlegend = True,
    height=600,
)
with st.spinner('Loading Data...'):
    st.plotly_chart(fig, use_container_width=True, height=600)