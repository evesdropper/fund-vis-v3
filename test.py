import numpy as np
import pandas as pd
import matplotlib.dates as mdates
from sklearn.linear_model import LinearRegression
import plotly.graph_objects as go
from fund import utils, tracker

X_SHIFT = mdates.date2num(tracker.START_DATE)

df = utils.sheet_to_df()
unique_funds = df.sort_values("Time", ascending=True).drop_duplicates(subset=["Fund"]).sort_values("Fund", ascending=True)
ymax = df["Fund"].max()
checks = list(tracker.CHECKPOINTS.keys())


df["# Days"] = mdates.datestr2num(df["Time"]) - X_SHIFT
df["# Days (Log)"] = np.log(mdates.datestr2num(df["Time"]) - X_SHIFT)
lin_multiple = LinearRegression()
lin_multiple.fit(X = df[["# Days", "# Days (Log)"]], y = df["Fund"])
print(np.round(lin_multiple.predict([[35, np.log(35)]]), -3))