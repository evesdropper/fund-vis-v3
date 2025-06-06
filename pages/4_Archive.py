import datetime
import os
import sys

import matplotlib.dates as mdates
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yaml

import fund
from fund import utils

# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, os.getcwd())
st.set_page_config(layout="wide", page_title="Archive")

with open("config.yml", "r") as file:
    fund_config = yaml.safe_load(file)["archive"]

ARCHIVE_URL = "https://docs.google.com/spreadsheets/d/1IRZ7yPhBAYOZ3BHpdx3zPNdOhwPvBb3__poumHoieVk/"
st.title("Past Tanki Fund Archive")
st.write(
    f"Plots and data for past Tanki Funds will be located here. You can also find a backup of the data on [Google Sheets]({ARCHIVE_URL})."
)


def generate_main_fig(
    event: str,
    sheet_id: str,
    sheet_gid: str,
    checkpoints: dict[int, str],
    start_date: datetime.datetime,
    end_date: datetime.datetime,
    x_shift: float,
    notes: list[list[str]] = [],
) -> go.Figure:
    df = utils.sheet_to_df(sheet_id=sheet_id, sheet_gid=sheet_gid)
    unique_funds = (
        df.sort_values("Time", ascending=True)
        .drop_duplicates(subset=["Fund"])
        .sort_values("Fund", ascending=True)
    )
    ymax = df["Fund"].max()
    checks = list(checkpoints.keys())

    end_day_num = np.ceil(mdates.date2num(utils.get_day()) - x_shift)
    days = np.arange(0, 35, 1 / 1440) + 0.001
    pred_df = pd.DataFrame(
        {"# Days": days, "# Days (Log)": np.log(days), "# Days^2": np.square(days)}
    )
    pred_df["Time"] = mdates.num2date(x_shift + pred_df["# Days"])
    pred_df["Time"] = pred_df["Time"].dt.strftime("%Y-%m-%d %H:%M")

    # plotting
    tr_realtime = go.Scatter(
        x=unique_funds["Time"],
        y=unique_funds["Fund"],
        mode="lines+markers",
        name="Fund Entries",
    )
    fig = go.Figure(tr_realtime)

    # Checklines
    for check in checks:
        checkm = check * 1000000
        if checkm <= ymax:
            fig.add_hline(
                y=checkm,
                line_color="green",
                annotation_text=f"Achieved: {checkpoints[check]}",
            )
        else:
            fig.add_hline(
                y=checkm,
                line_color="red",
                annotation_text=f"Missed: {checkpoints[check]}",
            )

    # Notes
    for note in notes:
        fig.add_vrect(
            x0=note[0], x1=note[1], fillcolor="red", opacity=0.2, line_width=0
        )

    # general
    fig.update_xaxes(range=[start_date, end_date])
    fig.update_yaxes(range=[0, 1.2 * ymax])
    fig.update_layout(
        title={"text": f"{event} Tanki Fund over Time", "x": 0.5, "xanchor": "center"},
        xaxis_title="Time (UTC)",
        yaxis_title="Amount in Tanki Fund",
        legend_title="Legend",
        showlegend=True,
        height=600,
    )
    return fig


def generate_hourly_fig(
    event: str,
    sheet_id: str,
    sheet_gid: str,
    start_date: datetime.datetime,
    end_date: datetime.datetime,
    notes: list[list[str]] = [],
) -> go.Figure:
    df = utils.sheet_to_df(sheet_id=sheet_id, sheet_gid=sheet_gid)
    hourly = df["Time"].str.extract(rf"(:0[012])").dropna()

    # draw time series
    df_h = df.iloc[hourly.index]
    df_h["tnum"] = mdates.datestr2num(df_h["Time"])
    df_h["tnd"] = df_h["tnum"].diff()
    df_h["Diff"] = df_h["Fund"].diff()
    dfh_graph = df_h[df_h["tnd"].between(0.9 / 24, 1.1 / 24)].dropna()

    trace = go.Scatter(
        x=dfh_graph["Time"],
        y=dfh_graph["Diff"],
        mode="lines+markers",
        name="Change in Past Hour",
    )
    fig = go.Figure([trace])

    # avg
    final_fund = df.iloc[-1, 1]
    avg_change = final_fund / (
        24 * (mdates.date2num(end_date) - mdates.date2num(start_date))
    )
    fig.add_hline(
        y=avg_change,
        line_color="gray",
        annotation_text=f"Avg Hourly Change: {np.round(avg_change, -2) / 10**3}k",
    )

    # Notes
    for note in notes:
        fig.add_vrect(
            x0=note[0], x1=note[1], fillcolor="red", opacity=0.2, line_width=0
        )

    # layout
    fig.update_xaxes(
        range=[start_date, end_date],
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list(
                [
                    dict(count=1, label="1d", step="day", stepmode="backward"),
                    dict(count=3, label="3d", step="day", stepmode="backward"),
                    dict(count=7, label="1w", step="day", stepmode="backward"),
                    dict(step="all"),
                ]
            )
        ),
    )
    fig.update_yaxes(range=[0, dfh_graph["Diff"].max() * 1.2])
    fig.update_layout(
        title={
            "text": f"{event} Tanki Fund Hourly Changes",
            "x": 0.5,
            "xanchor": "center",
        },
        xaxis_title="Time (UTC)",
        yaxis_title="Change Since Past Hour",
        legend_title="Legend",
        showlegend=True,
        height=600,
    )
    return fig


def generate_archive_content(season: str, year: int) -> None:
    dict_key = season[0] + str(year)
    start_date, end_date = (
        datetime.datetime.strptime(
            fund_config[dict_key]["start_date"], "%Y-%m-%d %H:%M"
        ),
        datetime.datetime.strptime(fund_config[dict_key]["end_date"], "%Y-%m-%d %H:%M"),
    )
    x_shift = mdates.date2num(
        datetime.datetime.strptime(
            fund_config[dict_key]["start_date"], "%Y-%m-%d %H:%M"
        )
    )
    checkpoints = fund_config[dict_key]["checkpoints"]

    st.header(f"20{year} - {season.capitalize()} Major")

    st.subheader("Fund Summary")

    # analytics
    col1, col2, col3 = st.columns(3)

    with col1:
        final_fund = fund_config[dict_key]["final_fund"]
        st.metric(label="Achieved Fund", value=f"{final_fund / 1000000}M")

    with col2:
        final_checkpoint = utils.get_checkpoint(
            final_fund / 1000000, checkpoints=checkpoints, future=False
        )
        st.metric(label="Achieved Checkpoint", value=f"{final_checkpoint}")

    with col3:
        avg_change = final_fund / (
            24 * (mdates.date2num(end_date) - mdates.date2num(start_date))
        )
        st.metric(
            label="Average Hourly Change", value=f"{np.round(avg_change, -2) / 10**3}K"
        )

    main_fig = generate_main_fig(
        f"{season[0].upper()}{year}",
        fund_config[dict_key]["sheet_id"],
        fund_config[dict_key]["sheet_gid"],
        checkpoints,
        start_date,
        end_date,
        x_shift,
        fund_config[dict_key]["notes"],
    )
    with st.spinner("Loading Data..."):
        st.plotly_chart(main_fig, use_container_width=True, height=600)

    hourly_fig = generate_hourly_fig(
        f"{season[0].upper()}{year}",
        fund_config[dict_key]["sheet_id"],
        fund_config[dict_key]["sheet_gid"],
        start_date,
        end_date,
        fund_config[dict_key]["notes"],
    )
    with st.spinner("Loading Data..."):
        st.plotly_chart(hourly_fig, use_container_width=True, height=600)


# archive
generate_archive_content("summer", 22)
generate_archive_content("winter", 23)
generate_archive_content("summer", 24)
generate_archive_content("winter", 24)
