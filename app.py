import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fund import utils, tracker

st.set_page_config(layout="wide", page_title="Tanki Fund Tracker")

st.title('Tanki Fund Tracker')
st.header("2022 - Summer Major")

# obtain and clean data
df = utils.sheet_to_df()
unique_funds = df.sort_values("Time", ascending=True).drop_duplicates(subset=["Fund"]).sort_values("Fund", ascending=True)
ymax = df["Fund"].max()
checks = list(tracker.CHECKPOINTS.keys())

# plotting
trace = go.Scatter(x=unique_funds["Time"], y=unique_funds["Fund"], mode="lines+markers", name="Fund Entries")
fig = go.Figure([trace])

# Checklines
for check in checks:
    checkm = check * 1000000
    if checkm <= ymax:
        fig.add_hline(y=checkm, line_color="green", annotation_text=f"Achieved: {tracker.CHECKPOINTS[check]}")
    else: 
        fig.add_hline(y=checkm, line_color="red", annotation_text=f"Upcoming: {tracker.CHECKPOINTS[check]}")

# Notes
fig.add_vrect(x0="2022-07-04 02:00", x1="2022-07-04 17:33", fillcolor="red", annotation_text="Observations", opacity=0.2, line_width=0)

# general
fig.update_xaxes(range=[tracker.START_DATE, utils.get_day()])
fig.update_yaxes(range=[0, 1.2 * ymax])
fig.update_layout(
    title={"text": "Tanki Fund over Time", 'x':0.5, 'xanchor': 'center'},
    xaxis_title="Time (UTC)",
    yaxis_title="Amount in Tanki Fund",
    legend_title="Legend",
    showlegend = True,
    height=600,
)
with st.spinner('Loading Data...'):
    st.plotly_chart(fig, use_container_width=True, height=600)