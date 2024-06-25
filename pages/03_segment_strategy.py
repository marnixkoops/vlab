"""xxx"""

import streamlit as st

from src.compute_segments_analytics import compute_glycogen_level
from src.plotting import plot_segments
from src.utils import excel_download_button, set_page_config

set_page_config()

st.markdown("# Segment Strategy")
# Get or set variables
if "df" in st.session_state:
    df = st.session_state.df
else:
    st.warning("Error: start analysis from stage selection", icon="⚠️")

if "selected_stage" in st.session_state:
    selected_stage = st.session_state.selected_stage

if "segments_df" in st.session_state:
    segments_df = st.session_state.segments_df

if "segments" in st.session_state:
    segments = st.session_state.segments


# Define sidebar
with st.sidebar:
    st.header("Conditions", divider="grey")
    temperature = st.number_input(
        "Temperature (°C)", value=27.0, step=0.1, format="%.1f"
    )
    humidity = st.number_input("Humidity (%)", value=80, step=1)

    st.image(
        "assets/logo.png",
        use_column_width=True,
    )


# Plot elevation with segments
segment_fig = plot_segments(df=df, segments=segments)
st.plotly_chart(segment_fig, use_container_width=True)

# Compute glycogen levels
segments_df = compute_glycogen_level(segments_df, glycogen_start_level=100)

# Display data
segments_df = st.data_editor(segments_df, height=1000, use_container_width=True)
# Download button for dataframe
excel_download_button(
    df=segments_df,
    label="Download segments",
    filename=f"stage_{selected_stage}_segments",
)

# Save data to session state
st.session_state.segments_df = segments_df
