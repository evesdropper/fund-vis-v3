import numpy as np
import pandas as pd
import plotly.graph_objects as go
from fund import utils, tracker

df = utils.sheet_to_df()
# print(df.head())

daily = df["Time"].str.extract(rf'(\s2:0[012]|\s1:5[789])').dropna()
print(daily)

# # draw time series
df_d = df.iloc[daily.index]
df_d["Day"] = list(range(1, df_d.shape[0] + 1))
df_d["Diff"] = df_d["Fund"].diff()
df_d.loc[55, "Diff"] = df_d.loc[55, "Fund"]
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
daily = df_d[["Day", "Diff", "% Change"]].set_index("Day")
print(daily)
# dfh_graph = df_h.dropna()
# avg_change = dfh_graph["Diff"].mean()

# trace = go.Scatter(x=dfh_graph["Time"], y=dfh_graph["Diff"], mode="lines+markers", name="Change in Past Hour")
# fig = go.Figure([trace])

# # avg
# fig.add_hline(y=avg_change, line_color="gray", annotation_text=f"Avg Hourly Change: {np.round(avg_change, -2) / 10 ** 3}k")

# fig.update_xaxes(range=[tracker.START_DATE, utils.get_day()])
# fig.update_yaxes(range=[0, dfh_graph["Diff"].max() * 1.2])
# fig.update_layout(
#     title={"text": "Tanki Fund Hourly Changes", 'x':0.5, 'xanchor': 'center'},
#     xaxis_title="Time (UTC)",
#     yaxis_title="Change Since Past Hour",
#     legend_title="Legend",
#     showlegend = True,
# )
# fig.show()