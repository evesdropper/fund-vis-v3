import numpy as np
import pandas as pd
import plotly.graph_objects as go
from fund import utils, tracker

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
fig.update_xaxes(range=[tracker.START_DATE, utils.get_day()], rangeslider_visible=True,
    rangeselector=dict(
        buttons=list([
            dict(count=1, label="1d", step="day", stepmode="backward"),
            dict(count=3, label="3d", step="day", stepmode="backward"),
            dict(count=7, label="1w", step="day", stepmode="backward"),
            dict(step="all")
        ]))
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
fig.show()