# Tanki Fund Tracker, v3

App made to track the Tanki Fund. Visualizations made with Plotly and displayed with/deployed on Streamlit.

Subject to change back to Flask + Plotly whenever I figure out how to configure that better; this does allow me to not worry about UI (especially the metric stuff), but I think it could be more personalized. This is probably never happening.

## Usage
Have finally made it such that once a new fund hits, the update process is fairly straightforward: simply update `config.yml` with the according fund iteration, start date, data URL, and checkpoints, and archive the old fund.

## To Do
- More Analytics
- Time Series Analysis
- Regressions/Trendlines
