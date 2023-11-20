import os, sys, glob
import datetime
import pandas as pd
import streamlit as st
from fund import tracker

# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, os.getcwd())

"""
Utils
"""

@st.cache_data(ttl=1800)
def sheet_to_df(url=tracker.DATA_URL, colnames=["Time", "Fund"]):
    """
    Tonk fund sheet go csv go df go brr
    """
    as_csv = url.replace("/edit#gid=", "/export?format=csv&gid=")
    df = pd.read_csv(as_csv, names=colnames)
    return df.dropna()

def get_day():
    """
    x-axis boundary moment
    """
    today = datetime.datetime.utcnow().date()
    end_x = (today + datetime.timedelta(days=1))
    return end_x

# format
def format_percent(string):
    if string == "0":
        return "-"
    elif string[0] == "-":
        return f"\u2193 {string}%"
    else:
        return f"\u2191 {string}%"
