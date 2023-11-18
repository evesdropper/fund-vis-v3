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

START_DATE = datetime.datetime.strptime("2023-11-17 2:00", "%Y-%m-%d %H:%M")
X_SHIFT = mdates.date2num(START_DATE)
CHECKPOINTS = {1: "Nuclear Energy", 2: "Module Slot", 10: "Gauss GT",
               11: "Nuclear Energy", 20: "Freeze GT",
               21: "Nuclear Energy", 30: "Hunter GT", 
               31: "Nuclear Energy", 32: "Module Slot", 34: "Magnum Pulsar", 36: "Gauss Pulsar", 38: "Shaft Pulsar", 40: "Skin Container",
               41: "Nuclear Energy", 45: "100 Nuclear Energy", 46: "100 Containers", 47: "30 Weekly Containers", 48: "90 Ultra Containers", 50: "Skin Container"}
DATA_URL = "https://docs.google.com/spreadsheets/d/1GiJQvvwp9cGWyRom5x6gc8qUjgUL2ONWyKfewBVY6sA/edit#gid=0"

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
    lin_multiple = LinearRegression()
    lin_multiple.fit(X = df[["# Days", "# Days (Log)", "# Days^2"]], y = df["Fund"])
    shift = np.ceil(df["Fund"].iloc[-1] / 10 ** 6)
    if multi:
        return lin_multiple.predict(x)
    elif newton:
        return lin_multiple.predict([[x, np.log(x), np.square(x)]])[0] - (shift * (10 ** 6))
    return lin_multiple.predict([[x, np.log(x), np.square(x)]])[0]

def newton(f=predict, a=mdates.date2num(datetime.datetime.now()) - X_SHIFT, b=min(mdates.date2num(datetime.datetime.now()) - X_SHIFT + 5, 35), tol=1/24):
    """
    Modified Newton's Method. Modified from MATLAB code from Math 128A PA1.
    """
    w, i = 1, 1
    print(' n a b p f(p) \n')
    print('--------------\n')
    while i < 100:
        p = a + (w * f(a) * (a - b)) / (f(b) - w * f(a))
        print(i, a, b, p, f(p))
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
