import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.dates as mdates
import plotly.graph_objects as go
import yaml
import datetime
from fund import utils, tracker

st.set_page_config(layout="wide", page_title="Tanki Fund Tracker")

with open("config.yml", "r") as file:
    fund_config = yaml.safe_load(file)["current_fund"]
    
st.title('Tanki Fund Tracker')
st.header(fund_config["iteration"])

# obtain and clean data
df = utils.sheet_to_df()
unique_funds = df[df["Fund"] != 0].sort_values("Time", ascending=True).drop_duplicates(subset=["Fund"]).sort_values("Fund", ascending=True)
ymax = df["Fund"].max()
checks = list(tracker.CHECKPOINTS.keys())

end_day_num = np.ceil(mdates.date2num(utils.get_day()) - tracker.X_SHIFT)
days = np.arange(0, 30, 1/1440) + 0.001
pred_df = pd.DataFrame({"# Days": days, "# Days (Log)": np.log(days), "# Days^2": np.square(days)})
pred_df["Time"] = mdates.num2date(tracker.X_SHIFT + pred_df["# Days"])
pred_df["Time"] = pred_df["Time"].dt.strftime("%Y-%m-%d %H:%M")
pred_df["Predicted"] = tracker.predict(pred_df[["# Days", "# Days (Log)"]], multi=True)

# plotting
tr_realtime = go.Scatter(x=unique_funds["Time"], y=unique_funds["Fund"], mode="lines+markers", name="Fund Entries")
cutoff_date = tracker.START_DATE + datetime.timedelta(days=3)
if datetime.datetime.now() < cutoff_date:
    try: 
        tr_prediction = go.Scatter(x=pred_df["Time"], y=pred_df["Predicted"], mode="lines", name="Predicted Fund", line = dict(color='grey'))
        fig = go.Figure([tr_realtime, tr_prediction])
    except:
        fig = go.Figure([tr_realtime])
else:
    fig = go.Figure([tr_realtime])

# Checklines
for check in checks:
    checkm = check * 1000000
    if checkm <= ymax:
        fig.add_hline(y=checkm, line_color="green", annotation_text=f"Achieved: {tracker.CHECKPOINTS[check]}")
    else: 
        fig.add_hline(y=checkm, line_color="red", annotation_text=f"Upcoming: {tracker.CHECKPOINTS[check]}")

# Notes
notes = fund_config["notes"]
for note in notes:
    fig.add_vrect(x0=note[0], x1=note[1], fillcolor="red", opacity=0.2, line_width=0)

# general
xmax_num = min(mdates.date2num(tracker.START_DATE + datetime.timedelta(days=30)), max(mdates.date2num(utils.get_day()), mdates.date2num(unique_funds.iloc[0, -1])))
fig.update_xaxes(range=[tracker.START_DATE, mdates.num2date(xmax_num)])
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
