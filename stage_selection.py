"""Main code to generate the streamlit app."""

import gpxpy
import streamlit as st

from src.process_data import create_dataframe, read_gpx_file
from src.utils import get_session_state

st.set_page_config(
    page_title="Team Visma | Lease a Bike Analytics",
    page_icon="🚴‍♂️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Define sidebar
with st.sidebar:
    st.image(
        "assets/logo.png",
        use_column_width=True,
    )

session_state = get_session_state()

if "selected_stage" in st.session_state:
    selected_stage = st.session_state.selected_stage
    selected_index = int(selected_stage.split("-")[1]) - 1
else:
    selected_stage = "stage-1"
    selected_index = 0

st.header("📍 TDF Stage selection", divider="grey")
stage_list = [f"stage-{i}" for i in range(1, 22)]
selected_stage = st.selectbox("", stage_list, index=selected_index)

st.header("💾 Custom GPX upload", divider="grey")
uploaded_file = st.file_uploader("", type=["gpx"])

# Load and process data
if uploaded_file:
    gpx_file = gpxpy.parse(uploaded_file)
    selected_stage = "custom gpx"
else:
    gpx_file = read_gpx_file(path=f"data/tdf/{selected_stage}-route.gpx")

df = create_dataframe(gpx_file=gpx_file)

# Save data to session state
st.session_state.df = df
st.session_state.selected_stage = selected_stage
