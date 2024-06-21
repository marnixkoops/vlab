"""xxx"""

import io

import pandas as pd
import streamlit as st

from src.generate_segments import create_segments_dataframe, generate_segments
from src.plotting import plot_map, plot_segments

st.set_page_config(
    page_title="Team Visma | Lease a Bike Segment Analytics",
    page_icon="🚴‍♂️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Define sidebar
with st.sidebar:
    st.header("⚙️ Segment model parameters", divider="grey")
    window_size_km = st.number_input("Minimum segment length (km)", value=2.0, step=0.1)
    min_slope_diff = st.number_input(
        "Minimum slope difference (%)", value=1.5, step=0.1
    )
    st.image(
        "assets/logo.png",
        use_column_width=True,
    )

# Load data from session state
df = st.session_state.df
selected_stage = st.session_state.selected_stage

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
output = io.BytesIO()
writer = pd.ExcelWriter(output, engine="xlsxwriter")
segments_df.to_excel(writer, index=False)
writer.close()
output.seek(0)
st.download_button(
    label="Download Excel file",
    data=output,
    file_name=f"stage_{selected_stage}_generated_segments.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)

# Save data to session state
st.session_state.segments = segments
st.session_state.segments_df = segments_df
