"""xxx"""

import streamlit as st

from src.compute_segments_analytics import (
    apply_duration,
    compute_glycogen_level,
    define_drafting_decisions,
)

st.markdown("# Segment Strategy")
st.sidebar.markdown("# Segment Strategy")

# Define sidebar
with st.sidebar:
    weight_rider = st.number_input(
        "Rider weight (kg)", value=60.0, step=0.1, format="%.1f"
    )
    cda_full = st.number_input(
        "CdA (full draft)", value=0.2625, step=0.01, format="%.4f"
    )
    cda_semi = st.number_input(
        "CdA (semi draft)", value=0.305, step=0.01, format="%.4f"
    )
    cda_none = st.number_input("CdA (no draft)", value=0.35, step=0.01, format="%.4f")

    st.image(
        "assets/logo.png",
        use_column_width=True,
    )


# Load data from session state
segments_df = st.session_state["segments_df"]


rider_stats = {
    "weight_rider": weight_rider,  # in kg
    "cda_values": {
        "Full Draft": cda_full,
        "Semi Draft": cda_semi,
        "No Draft": cda_none,
    },
}

segments_df, semi_draft_segment, full_draft_segment = define_drafting_decisions(
    segments_df, semi_draft_point=0.6, full_draft_point=0.9
)

segments_df["duration"] = segments_df.apply(
    apply_duration, axis=1, rider_stats=rider_stats
)

segments_df = compute_glycogen_level(segments_df, glycogen_start_level=100)

st.dataframe(segments_df, height=1000, use_container_width=True)
