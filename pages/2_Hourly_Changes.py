import os, sys
import numpy as np
import pandas as pd
import matplotlib.dates as mdates
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
df_h["tnum"] = mdates.datestr2num(df_h["Time"])
df_h["tnd"] = df_h["tnum"].diff()
df_h["Diff"] = df_h["Fund"].diff()
dfh_graph = df_h[df_h["tnd"].between(0.9/24, 1.1/24)].dropna()
avg_change = dfh_graph["Diff"].mean()

trace = go.Scatter(x=dfh_graph["Time"], y=dfh_graph["Diff"], mode="lines+markers", name="Change in Past Hour")
fig = go.Figure([trace])

# avg
fig.add_hline(y=avg_change, line_color="gray", annotation_text=f"Avg Hourly Change: {np.round(avg_change, -2) / 10 ** 3}k")

# outages
fig.add_vrect(x0="2023-11-17 02:00", x1="2023-11-18 17:37", fillcolor="red", opacity=0.2, line_width=0)
fig.add_vrect(x0="2023-11-20 06:30", x1="2023-11-21 09:00", fillcolor="red", opacity=0.2, line_width=0)

# layout
fig.update_xaxes(range=[tracker.START_DATE, utils.get_day()], rangeslider_visible=True,
    rangeselector=dict(
        buttons=list([
            dict(count=1, label="1d", step="day", stepmode="backward"),
            dict(count=3, label="3d", step="day", stepmode="backward"),
            dict(count=7, label="1w", step="day", stepmode="backward"),
            dict(step="all")
        ]))
)
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
