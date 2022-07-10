import datetime
import numpy as np
import pandas as pd
import matplotlib.dates as mdates
from sklearn.linear_model import LinearRegression
from fund import utils

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

def predict(x=False, y=False):
    """
    Prediction using Multiple Linear Regression on Time and ln(Time).
    """
    df = utils.sheet_to_df()
    df["# Days"] = mdates.datestr2num(df["Time"]) - X_SHIFT
    df["# Days (Log)"] = np.log(mdates.datestr2num(df["Time"]) - X_SHIFT)
    lin_multiple = LinearRegression()
    lin_multiple.fit(X = df[["# Days", "# Days (Log)"]], y = df["Fund"])
    return int(np.round(lin_multiple.predict([[35, np.log(35)]]), -3))