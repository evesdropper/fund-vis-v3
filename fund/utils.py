import os, sys, glob
import datetime
import pandas as pd
from fund import tracker

"""
Utils
"""

def sheet_to_df(url=tracker.DATA_URL, colnames=["Time", "Fund"]):
    """
    Tonk fund sheet go csv go df go brr
    """
    as_csv = url.replace("/edit#gid=", "/export?format=csv&gid=")
    return pd.read_csv(as_csv, names=colnames, header=None)

def get_day():
    """
    x-axis boundary moment
    """
    today = datetime.datetime.utcnow().date()
    end_x = (today + datetime.timedelta(days=1))
    return end_x