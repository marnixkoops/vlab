"""xxx"""

import streamlit as st

from src.plotting import combine_plots
from src.utils import get_session_state, set_page_config

set_page_config()

st.markdown("# Glycogen Analysis")
# Get or set variables
if "df" in st.session_state:
    df = st.session_state.df

if "segments_df" in st.session_state:
    segments_df = st.session_state.segments_df

if "segments" in st.session_state:
    segments = st.session_state.segments

# Get or set variables
session_state = get_session_state()

# Plot elevation with segments
combined_fig = combine_plots(df=df, segments=segments, segments_df=segments_df)
st.plotly_chart(combined_fig, use_container_width=True)


# Save data to session state
st.session_state.df = df
st.session_state.segments = segments
st.session_state.segments_df = segments_df
