import os, sys
import datetime
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import matplotlib.dates as mdates
from fund import utils, tracker
import scipy as sp

# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, os.getcwd())

# print(tracker.predict([[35, np.log(35), np.square(35)]]))

# cdelta = (mdates.num2date(tracker.newton() + tracker.X_SHIFT).replace(tzinfo=datetime.timezone.utc) - datetime.datetime.now().replace(tzinfo=datetime.timezone.utc))
# print(cdelta)

print(tracker.predict(35))
print(tracker.newton())
# w = 1
# f=tracker.predict 
# a=mdates.date2num(datetime.datetime.now()) - tracker.X_SHIFT
# b = 27 # b=min(mdates.date2num(datetime.datetime.now()) - tracker.X_SHIFT + 5, 35)
# p = a + (w * f(a) * (a - b)) / (f(b) - w * f(a))
# print(p)