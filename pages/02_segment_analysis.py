"""Code for the Segment Analysis page of the app."""

import streamlit as st

from src.plotting import plot_segments

st.set_page_config(
    page_title="Team Visma | Lease a Bike Segment Analytics",
    page_icon="🚴‍♂️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Define sidebar
with st.sidebar:
    relative_power = st.number_input(
        "Relative Power (W/kg)", value=5.5, step=0.1, format="%.1f"
    )

    st.image(
        "assets/logo.png",
        use_column_width=True,
    )


# Load data from session state
df = st.session_state["df"]
selected_stage = st.session_state["selected_stage"]
segments = st.session_state["segments"]
segments_df = st.session_state["segments_df"]

st.markdown("## Segment Analysis")

# Plot elevation with segments
segment_fig = plot_segments(df=df, segments=segments)
st.plotly_chart(segment_fig, use_container_width=True)

segments_df["relative power"] = relative_power

st.dataframe(segments_df, height=1000, use_container_width=True)


# Save data to session state
st.session_state.segments_df = segments_df
