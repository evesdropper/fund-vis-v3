import datetime
import glob
import os
import sys

import pandas as pd
import streamlit as st
import yaml

# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, os.getcwd())

# get config
with open("config.yml", "r") as file:
    fund_config = yaml.safe_load(file)["current_fund"]

"""
Utils
"""


@st.cache_data(ttl=1800)
def sheet_to_df(
    url: str = fund_config["data_url"], colnames: list[str] = ["Time", "Fund"]
) -> pd.DataFrame:
    """
    Tonk fund sheet go csv go df go brr
    """
    as_csv = url.replace("/edit#gid=", "/export?format=csv&gid=")
    df = pd.read_csv(as_csv, names=colnames)
    return df.dropna().reset_index(drop=True)


def get_day() -> datetime.date:
    """
    x-axis boundary moment
    """
    today = datetime.datetime.now(datetime.timezone.utc).date()
    end_x = today + datetime.timedelta(days=1)
    return end_x


def get_checkpoint(
    fund: int,
    checkpoints: dict[int, str] = fund_config["checkpoints"],
    future: bool = False,
):
    checknums = list(checkpoints.keys())

    if fund > checknums[-1]:
        return checkpoints[checknums[-1]]

    idx = 0
    while checknums[idx] < fund:
        idx += 1
    return checkpoints[checknums[idx - abs(1 - int(future))]]


# format
def format_percent(string: str):
    if string == "0":
        return "-"
    elif string[0] == "-":
        return f"\u2193 {string}%"
    else:
        return f"\u2191 {string}%"
