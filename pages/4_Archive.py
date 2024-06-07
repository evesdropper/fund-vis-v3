import os, sys
import streamlit as st
import datetime
import numpy as np
import pandas as pd
import matplotlib.dates as mdates
import plotly.graph_objects as go
from fund import utils, tracker

# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, os.getcwd())
st.set_page_config(layout="wide", page_title="Archive")
st.title('Past Tanki Fund Archive')
st.write("Plots and data for past Tanki Funds will be located here.")

st.header("2022 - Summer Major")

S22_START_DATE = datetime.datetime.strptime("2022-07-04 2:00", "%Y-%m-%d %H:%M")
S22_END_DATE = datetime.datetime.strptime("2022-08-08 2:00", "%Y-%m-%d %H:%M")
S22_X_SHIFT = mdates.date2num(S22_START_DATE)
S22_CHECKPOINTS = {1: "Nuclear Energy", 4: "Prot Slot", 7: "Skin Container", 8: "Magnetic Pellets", 9: "Helios", 10: "Hammer LGC", 11: "Vacuum Shell", 12: "Swarm", 13: "Pulsar", 14: "Armadillo", 15: "Crisis"}
S22_DATA_URL = "https://docs.google.com/spreadsheets/d/1IRZ7yPhBAYOZ3BHpdx3zPNdOhwPvBb3__poumHoieVk/edit#gid=1817523881"

W23_START_DATE = datetime.datetime.strptime("2023-11-17 2:00", "%Y-%m-%d %H:%M")
W23_END_DATE = datetime.datetime.strptime("2023-12-20 2:00", "%Y-%m-%d %H:%M")
W23_X_SHIFT = mdates.date2num(W23_START_DATE)
W23_CHECKPOINTS = {1: "Nuclear Energy", 2: "Module Slot", 10: "Gauss GT",
               11: "Nuclear Energy", 20: "Freeze GT",
               21: "Nuclear Energy", 30: "Hunter GT", 
               31: "Nuclear Energy", 32: "Module Slot", 34: "Magnum Pulsar", 36: "Gauss Pulsar", 38: "Shaft Pulsar", 40: "Skin Container",
               41: "Nuclear Energy", 45: "100 Nuclear Energy", 46: "100 Containers", 47: "30 Weekly Containers", 48: "90 Ultra Containers", 50: "Skin Container"}
W23_DATA_URL = "https://docs.google.com/spreadsheets/d/1GiJQvvwp9cGWyRom5x6gc8qUjgUL2ONWyKfewBVY6sA/edit#gid=0"

def generate_main_fig(event, data_url, checkpoints, start_date, end_date, x_shift, notes=[]):
  df = utils.sheet_to_df(url=data_url)
  unique_funds = df.sort_values("Time", ascending=True).drop_duplicates(subset=["Fund"]).sort_values("Fund", ascending=True)
  ymax = df["Fund"].max()
  checks = list(checkpoints.keys())
  
  end_day_num = np.ceil(mdates.date2num(utils.get_day()) - x_shift)
  days = np.arange(0, 35, 1/1440) + 0.001
  pred_df = pd.DataFrame({"# Days": days, "# Days (Log)": np.log(days), "# Days^2": np.square(days)})
  pred_df["Time"] = mdates.num2date(x_shift + pred_df["# Days"])
  pred_df["Time"] = pred_df["Time"].dt.strftime("%Y-%m-%d %H:%M")
  
  # plotting
  tr_realtime = go.Scatter(x=unique_funds["Time"], y=unique_funds["Fund"], mode="lines+markers", name="Fund Entries")
  fig = go.Figure(tr_realtime)
  
  # Checklines
  for check in checks:
      checkm = check * 1000000
      if checkm <= ymax:
          fig.add_hline(y=checkm, line_color="green", annotation_text=f"Achieved: {checkpoints[check]}")
      else: 
          fig.add_hline(y=checkm, line_color="red", annotation_text=f"Missed: {checkpoints[check]}")
  
  # Notes
  for note in notes:
    fig.add_vrect(x0=note[0], x1=note[1], fillcolor="red", opacity=0.2, line_width=0)
  
  # general
  fig.update_xaxes(range=[start_date, end_date])
  fig.update_yaxes(range=[0, 1.2 * ymax])
  fig.update_layout(
      title={"text": f"{event} Tanki Fund over Time", 'x':0.5, 'xanchor': 'center'},
      xaxis_title="Time (UTC)",
      yaxis_title="Amount in Tanki Fund",
      legend_title="Legend",
      showlegend = True,
      height=600,
  )
  return fig

def generate_hourly_fig(event, data_url, checkpoints, start_date, end_date, x_shift, notes=[]):
  df = utils.sheet_to_df(url=data_url)
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
  
  # Notes
  for note in notes:
    fig.add_vrect(x0=note[0], x1=note[1], fillcolor="red", opacity=0.2, line_width=0)
  
  # layout
  fig.update_xaxes(range=[start_date, end_date], rangeslider_visible=True,
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
      title={"text": f"{event} Tanki Fund Hourly Changes", 'x':0.5, 'xanchor': 'center'},
      xaxis_title="Time (UTC)",
      yaxis_title="Change Since Past Hour",
      legend_title="Legend",
      showlegend = True,
      height=600,
  )
  return fig

s22_main_fig = generate_main_fig("S22", S22_DATA_URL, S22_CHECKPOINTS, S22_START_DATE, S22_END_DATE, S22_X_SHIFT,
                                 [["2022-07-04 02:00", "2022-07-04 17:33"], ["2022-07-14 18:30", "2022-07-16 03:30"]])
with st.spinner('Loading Data...'):
    st.plotly_chart(s22_main_fig, use_container_width=True, height=600)
  
s22_hourly_fig = generate_hourly_fig("S22", S22_DATA_URL, S22_CHECKPOINTS, S22_START_DATE, S22_END_DATE, S22_X_SHIFT,
                                 [["2022-07-04 02:00", "2022-07-04 17:33"], ["2022-07-14 18:30", "2022-07-16 03:30"]])
with st.spinner('Loading Data...'):
    st.plotly_chart(s22_hourly_fig, use_container_width=True, height=600)
