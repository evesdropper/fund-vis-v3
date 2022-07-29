import os, sys
import datetime
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import matplotlib.dates as mdates
from fund import utils, tracker

# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, os.getcwd())

# print(tracker.predict([[35, np.log(35), np.square(35)]]))
print(tracker.newton())