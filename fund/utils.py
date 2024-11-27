import os, sys, glob
import yaml
import datetime
import pandas as pd
import streamlit as st

# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, os.getcwd())

# get config
with open("config.yml", "r") as file:
    fund_config = yaml.safe_load(file)["current_fund"]

"""
Utils
"""

@st.cache_data(ttl=1800)
def sheet_to_df(url=fund_config["data_url"], colnames=["Time", "Fund"]):
    """
    Tonk fund sheet go csv go df go brr
    """
    as_csv = url.replace("/edit#gid=", "/export?format=csv&gid=")
    df = pd.read_csv(as_csv, names=colnames)
    return df.dropna().reset_index(drop=True)

def get_day():
    """
    x-axis boundary moment
    """
    today = datetime.datetime.now(datetime.timezone.utc).date()
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
