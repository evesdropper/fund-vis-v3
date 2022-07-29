import os, sys
import datetime
import numpy as np
import pandas as pd
import matplotlib.dates as mdates
from sklearn.linear_model import LinearRegression
from fund import utils

# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, os.getcwd())

START_DATE = datetime.datetime.strptime("2022-07-04 2:00", "%Y-%m-%d %H:%M")
X_SHIFT = mdates.date2num(START_DATE)
CHECKPOINTS = {1: "Nuclear Energy", 4: "Prot Slot", 7: "Skin Container", 8: "Magnetic Pellets", 9: "Helios", 10: "Hammer LGC", 11: "Vacuum Shell", 12: "Swarm", 13: "Pulsar", 14: "Armadillo", 15: "Crisis"}
DATA_URL = "https://docs.google.com/spreadsheets/d/1IRZ7yPhBAYOZ3BHpdx3zPNdOhwPvBb3__poumHoieVk/edit#gid=1817523881"

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

def predict(x):
    """
    Prediction using Multiple Linear Regression on Time and ln(Time).
    """
    df = utils.sheet_to_df()
    df["# Days"] = mdates.datestr2num(df["Time"]) - X_SHIFT
    df["# Days (Log)"] = np.log(mdates.datestr2num(df["Time"]) - X_SHIFT)
    df["# Days^2"] = np.square(mdates.datestr2num(df["Time"]) - X_SHIFT)
    lin_multiple = LinearRegression()
    lin_multiple.fit(X = df[["# Days", "# Days (Log)", "# Days^2"]], y = df["Fund"])
    return lin_multiple.predict(x)

def linreg_func(x):
    """
    Get the next checkpoint.
    """
    df = utils.sheet_to_df()
    df["# Days"] = mdates.datestr2num(df["Time"]) - X_SHIFT
    df["# Days (Log)"] = np.log(mdates.datestr2num(df["Time"]) - X_SHIFT)
    lin_multiple = LinearRegression()
    lin_multiple.fit(X = df[["# Days", "# Days (Log)"]], y = df["Fund"])
    shift=np.ceil(df["Fund"].iloc[-1] / 10 ** 6)
    return lin_multiple.coef_.T @ np.array([x, np.log(x), np.square(x)]) + lin_multiple.intercept_ - (shift * 10 ** 6) 

def newton(f=linreg_func, a=mdates.date2num(datetime.datetime.now()) - X_SHIFT, b=min(mdates.date2num(datetime.datetime.now()) - X_SHIFT + 5, 35), tol=1/24):
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