from http.client import NETWORK_AUTHENTICATION_REQUIRED
import os, sys
import datetime
import numpy as np
import pandas as pd
import matplotlib.dates as mdates
from sklearn.linear_model import LinearRegression
from fund import utils

# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, os.getcwd())

START_DATE = datetime.datetime.strptime("2024-11-22 2:00", "%Y-%m-%d %H:%M")
X_SHIFT = mdates.date2num(START_DATE)
CHECKPOINTS = {1: "Nuclear Energy", 2: "Grenades", 
               11: "Striker Tandem", 12: "Nuclear Energy", 13: "Magnum Bombard", 15: "Armadillo", 17: "Isida Sustainable Nanobots", 19: "Magnum Destroyer", 
               21: "Ricochet GT", 23: "Ricochet Pulsar", 25: "Legendary Key", 27: "Titan GT", 29: "Gauss Nemesis", 30: "3 Legendary Keys"
              }
DATA_URL = "https://docs.google.com/spreadsheets/d/1mGZVcTbSvR2KE648HvHHHW7Cyqn-qtjI6bEqTbkte-o/edit#gid=0"

def regression(log=None):
    """
    Regression
    """
    df = utils.sheet_to_df()
    x, y = mdates.datestr2num(df["Time"].to_numpy()), df["Fund"].to_numpy()
    r = np.corrcoef(x, y)[0, 1]
    m = r * (np.std(y) / np.std(x))
    b = np.mean(y) - m * np.mean(x)
    return m, b

def predict(x, newton=True, multi=None):
    """
    Prediction using Multiple Linear Regression on Time and ln(Time).
    """
    df = utils.sheet_to_df()
    df["# Days"] = mdates.datestr2num(df["Time"]) - X_SHIFT
    df["# Days (Log)"] = np.log(mdates.datestr2num(df["Time"]) - X_SHIFT)
    df["# Days^2"] = np.square(mdates.datestr2num(df["Time"]) - X_SHIFT)
    # print(df)
    lin_multiple = LinearRegression()
    lin_multiple.fit(X = df[["# Days", "# Days (Log)"]], y = df["Fund"])
    # get checkpoint information
    checknums = list(CHECKPOINTS.keys())
    idx = 0
    while checknums[idx] < df.iloc[-1, 1] / 10 ** 6:
        idx += 1
    shift = checknums[idx]
    if multi:
        return lin_multiple.predict(x)
    elif newton:
        return lin_multiple.predict([[x, np.log(x)]])[0] - (shift * (10 ** 6))
    return lin_multiple.predict([[x, np.log(x)]])[0]

def newton(f=predict, a=mdates.date2num(datetime.datetime.now()) - X_SHIFT, b=min(mdates.date2num(datetime.datetime.now()) - X_SHIFT + 5, 35), tol=1/24):
    """
    Modified Newton's Method. Modified from MATLAB code from Math 128A PA1.
    """
    w, i = 1, 1
    # print(' n a b p f(p) \n')
    # print('--------------\n')
    while i < 100:
        p = a + (w * f(a) * (a - b)) / (f(b) - w * f(a))
        # print(i, a, b, p, f(p))
        if f(p) * f(b) > 0:
            w = 1 / 2
        else:
            w = 1
            a = b
        b = p
        if abs(b - a) < tol or abs(f(p)) < tol:
            break
        i += 1
    return p

def tdelta_format(td):
    seconds = np.round(td.total_seconds())
    days, rem1 = divmod(seconds, 86400)
    hours, rem2 = divmod(rem1, 3600)
    minutes, seconds = divmod(rem2, 60)
    if days > 0:
        return f"{int(days)}d {int(hours)}h {int(minutes)}m"
    return f"{int(hours)}h {int(minutes)}m"
