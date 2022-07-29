import os, sys
import datetime
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import matplotlib.dates as mdates
from fund import utils, tracker

# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, os.getcwd())

df = utils.sheet_to_df()
cur = df["Fund"].iloc[-1]

# print(tracker.linreg_func(27))
cdelta = (mdates.num2date(tracker.newton() + tracker.X_SHIFT).replace(tzinfo=datetime.timezone.utc) - datetime.datetime.now().replace(tzinfo=datetime.timezone.utc))

print(tracker.tdelta_format(cdelta))
