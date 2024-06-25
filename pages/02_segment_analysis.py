"""Code for the Segment Analysis page of the app."""

import random

import pandas as pd
import streamlit as st

from src.compute_segments_analytics import (
    apply_duration,
    apply_relative_power,
    define_drafting_decisions,
)
from src.plotting import plot_segments
from src.utils import excel_download_button, set_page_config

set_page_config()

st.markdown("# Segment Strategy")


# Get or set variables
def save_dataframe_edits() -> None:
    """Save edited dataframe to session state."""
    st.session_state.segments_df_edited = segments_df.copy()


if "df" in st.session_state:
    df = st.session_state.df
else:
    st.warning("Error: start analysis from stage selection", icon="⚠️")

if "selected_stage" in st.session_state:
    selected_stage = st.session_state.selected_stage

if "segments" in st.session_state:
    segments = st.session_state.segments

if "segments_df" in st.session_state:
    segments_df = st.session_state.segments_df

if "average_speed_flat" in st.session_state:
    average_speed_flat = st.session_state.average_speed_flat
else:
    average_speed_flat = 45.0

if "average_speed_down" in st.session_state:
    average_speed_down = st.session_state.average_speed_down
else:
    average_speed_down = 60.0

if "rider_stats" in st.session_state:
    weight_rider = st.session_state.rider_stats["weight_rider"]
    cda_full = st.session_state.rider_stats["cda_values"]["full"]
    cda_semi = st.session_state.rider_stats["cda_values"]["semi"]
    cda_none = st.session_state.rider_stats["cda_values"]["none"]
else:
    weight_rider = 65.0
    cda_full = 0.2625
    cda_semi = 0.305
    cda_none = 0.35

# Define sidebar
with st.sidebar:
    st.header("Drafting strategy", divider="grey")
    semi_draft_point = st.number_input(
        "Semi draft point", value=0.6, step=0.1, on_change=save_dataframe_edits
    )
    full_draft_point = st.number_input(
        "Full draft point", value=0.9, step=0.1, on_change=save_dataframe_edits
    )

    st.header("Rider stats", divider="grey")
    weight_rider = st.number_input(
        "Rider weight (kg)",
        value=weight_rider,
        step=0.1,
        format="%.1f",
        on_change=save_dataframe_edits,
    )
    cda_full = st.number_input(
        "CdA (full draft)",
        value=cda_full,
        step=0.01,
        format="%.4f",
        on_change=save_dataframe_edits,
    )
    cda_semi = st.number_input(
        "CdA (semi draft)",
        value=cda_semi,
        step=0.01,
        format="%.4f",
        on_change=save_dataframe_edits,
    )
    cda_none = st.number_input(
        "CdA (no draft)",
        value=cda_none,
        step=0.01,
        format="%.4f",
        on_change=save_dataframe_edits,
    )
    st.header("Segment Speeds", divider="grey")
    average_speed_flat = st.number_input(
        "Avg. speed flat segments",
        value=average_speed_flat,
        step=0.5,
        format="%.1f",
        on_change=save_dataframe_edits,
    )
    average_speed_down = st.number_input(
        "Avg. speed down segments",
        value=average_speed_down,
        step=0.5,
        format="%.1f",
        on_change=save_dataframe_edits,
    )

    st.image(
        "assets/logo.png",
        use_column_width=True,
    )


# Set rider stats
rider_stats = {
    "weight_rider": weight_rider,  # in kg
    "cda_values": {
        "full": cda_full,
        "semi": cda_semi,
        "none": cda_none,
    },
}

# Plot elevation with segments
segment_fig = plot_segments(df=df, segments=segments)
st.plotly_chart(segment_fig, use_container_width=True)

# Set drafting points
segments_df, semi_draft_segment, full_draft_segment = define_drafting_decisions(
    segments_df, semi_draft_point=semi_draft_point, full_draft_point=full_draft_point
)

if "relative power (w/kg)" not in segments_df.columns:
    relative_power_climb = 5.5
    relative_power_descend = 1.5
    relative_power_flat = 3.0
    segments_df["relative power (w/kg)"] = segments_df.apply(
        apply_relative_power,
        args=(relative_power_climb, relative_power_descend, relative_power_flat),
        axis=1,
    )


# Compute segment durations
def compute_durations(segments_df: pd.DataFrame) -> pd.DataFrame:
    segments_df["duration (s)"] = segments_df.apply(
        apply_duration,
        axis=1,
        rider_stats=rider_stats,
        average_speed_down=average_speed_down,
        average_speed_flat=average_speed_flat,
    ).round(0)

    return segments_df


def force_compute_durations():
    st.session_state.segments_df = compute_durations(segments_df=segments_df)


if "segments_df_edited" in st.session_state:
    segments_df = st.session_state.segments_df_edited

st.session_state.segments_df = compute_durations(segments_df=segments_df)

search = st.button("Recompute durations", on_click=force_compute_durations)
st.session_state.segments_df_edited = st.data_editor(
    st.session_state.segments_df,
    height=800,
    use_container_width=True,
    num_rows="dynamic",
)


# Download button for dataframe
excel_download_button(
    df=segments_df,
    label="Download",
    filename=f"stage_{selected_stage}_segments",
)

# Save data to session state
st.session_state.segments = segments
st.session_state.segments_df = segments_df
st.session_state.rider_stats = rider_stats
st.session_state.average_speed_flat = average_speed_flat
st.session_state.average_speed_down = average_speed_down
