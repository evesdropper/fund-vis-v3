import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.dates as mdates
import plotly.graph_objects as go
from fund import utils, tracker

st.set_page_config(layout="wide", page_title="Tanki Fund Tracker")

st.title('Tanki Fund Tracker')
st.header("2023 - Winter Major")

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
pred_df["Predicted"] = tracker.predict(pred_df[["# Days", "# Days (Log)", "# Days^2"]], multi=True)

# plotting
tr_realtime = go.Scatter(x=unique_funds["Time"], y=unique_funds["Fund"], mode="lines+markers", name="Fund Entries")
tr_prediction = go.Scatter(x=pred_df["Time"], y=pred_df["Predicted"], mode="lines", name="Predicted Fund", line = dict(color='grey'))
fig = go.Figure([tr_realtime, tr_prediction])

# Checklines
for check in checks:
    checkm = check * 1000000
    if checkm <= ymax:
        fig.add_hline(y=checkm, line_color="green", annotation_text=f"Achieved: {tracker.CHECKPOINTS[check]}")
    else: 
        fig.add_hline(y=checkm, line_color="red", annotation_text=f"Upcoming: {tracker.CHECKPOINTS[check]}")

# Notes
fig.add_vrect(x0="2023-11-17 02:00", x1="2023-11-18 17:37", fillcolor="red", opacity=0.2, line_width=0)

# general
fig.update_xaxes(range=[tracker.START_DATE, utils.get_day()], # rangeslider_visible=True,
    # rangeselector=dict(
    #     buttons=list([
    #         dict(count=1, label="1d", step="day", stepmode="backward"),
    #         dict(count=3, label="3d", step="day", stepmode="backward"),
    #         dict(count=7, label="1w", step="day", stepmode="backward"),
    #         dict(step="all")
    #     ]))
)
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
