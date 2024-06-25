"""xxx"""

import streamlit as st

from src.generate_segments import create_segments_dataframe, generate_segments
from src.plotting import plot_map, plot_segments
from src.utils import excel_download_button, set_page_config

set_page_config()

st.markdown("# Segment Generation")

# Get or set variables
if "df" in st.session_state:
    df = st.session_state.df
else:
    st.warning("Error: start analysis from stage selection", icon="⚠️")

if "selected_stage" in st.session_state:
    selected_stage = st.session_state.selected_stage

if "window_size_km" in st.session_state:
    window_size_km = st.session_state.window_size_km
else:
    window_size_km = 2.0

if "min_slope_diff" in st.session_state:
    min_slope_diff = st.session_state.min_slope_diff
else:
    min_slope_diff = 1.5

# Define sidebar
with st.sidebar:
    st.header("⚙️ Segment model parameters", divider="grey")
    window_size_km = st.number_input(
        "Minimum segment length (km)", value=window_size_km, step=0.1
    )
    min_slope_diff = st.number_input(
        "Minimum slope difference (%)", value=min_slope_diff, step=0.1
    )
    st.image(
        "assets/logo.png",
        use_column_width=True,
    )

# Generate segments
segments = generate_segments(
    df=df, window_size_km=window_size_km, min_slope_diff=min_slope_diff
)
segments_df = create_segments_dataframe(df=df, segments=segments)

# Plot map with segments
map_fig = plot_map(
    df=df,
    segments_df=segments_df,
    selected_stage=selected_stage,
)
st.plotly_chart(map_fig, use_container_width=True)

# Add stage info metrics
total_distance = int(df["distance"].max())
min_elevation = int(df["elevation"].min())
max_elevation = int(df["elevation"].max().round(0))
total_gain = int(df[df["elevation_diff"] >= 0]["elevation_diff"].sum().round(0))

col1, col2, col3, col4 = st.columns(4)
col1.metric(label="Total distance", value=f"🗺️ {total_distance} km")
col2.metric(label="Total elevation gain", value=f"📈 {total_gain} m")
col3.metric(label="Min elevation", value=f"⬇️ {min_elevation} m")
col4.metric(label="Max elevation", value=f"⬆️ {max_elevation} m")

# Plot elevation with segments
segment_fig = plot_segments(df=df, segments=segments)
st.plotly_chart(segment_fig, use_container_width=True)

# Display dataframe with segment info
st.caption(f"💾 Dataframe with {len(segments_df)} generated segments")
st.dataframe(segments_df, use_container_width=True)

# Download button for dataframe
excel_download_button(
    df=segments_df,
    label="Download segments",
    filename=f"stage_{selected_stage}_segments",
)

# Save data to session state
st.session_state.window_size_km = window_size_km
st.session_state.min_slope_diff = min_slope_diff
st.session_state.segments = segments
st.session_state.segments_df = segments_df
