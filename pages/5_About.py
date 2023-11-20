import os, sys
import streamlit as st

# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, os.getcwd())

st.set_page_config(page_title="About")
st.title("About")

st.markdown('''
App made to track the progress of Tanki Fund events over time. Previous funds will be archived and you will be able to access them in the archive tab.

Made in Python using Plotly and Streamlit, and hosted on Streamlit.

If there are any questions, feature requests, or bug reports, feel free to contact me on Discord: @secondatbest.
''')
