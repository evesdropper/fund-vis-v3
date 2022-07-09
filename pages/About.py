import os, sys
import streamlit as st

# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, os.getcwd())

from fund import utils

st.title("About")

st.markdown('''
App made to track the progress of the Tanki Fund over time. From now on, this should be the permanent location of all fund tracking tools. Previous funds will be archived and you will be able to access them there.

Made in Python using Plotly and Streamlit.
''')