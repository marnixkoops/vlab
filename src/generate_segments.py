"""Code to automate segment generation based on a dataframe with .gpx data."""

import pandas as pd
from scipy.signal import find_peaks


def generate_segments(
    df: pd.DataFrame, window_size_km: float = 1.0, min_slope_diff: float = 2.0
) -> list:
    """Calculate gradients and split segments.

    Args:
        df: Dataframe with gpx data.
        window_size_km: Minimum window length to define a segment  in km.
        min_slope_diff: Minimum slope difference to define a segment in %.

    Returns:
        list: list of defined segments.
    """
    # Detect local maxima and minima
    peaks, _ = find_peaks(df["smoothed_elevation"], prominence=2, width=1)
    valleys, _ = find_peaks(-df["smoothed_elevation"], prominence=2, width=1)
    inflection_points = sorted(list(peaks) + list(valleys))

    # Ensure first segment starts at the beginning and the last segment ends at the end
    if inflection_points[0] != 0:
        inflection_points.insert(0, 0)
    if inflection_points[-1] != len(df) - 1:
        inflection_points.append(len(df) - 1)

    segments = []
    start_idx = inflection_points[0]
    for i in range(1, len(inflection_points)):
        end_idx = inflection_points[i]
        segment_distance = df["distance"].iloc[end_idx] - df["distance"].iloc[start_idx]

        if segment_distance >= window_size_km:
            start_elevation = df["elevation"].iloc[start_idx]
            end_elevation = df["elevation"].iloc[end_idx]
            average_slope = (
                (end_elevation - start_elevation) / (segment_distance * 1000) * 100
            )
            segments.append(
                {
                    "start_idx": start_idx,
                    "end_idx": end_idx,
                    "start_elevation": start_elevation,
                    "end_elevation": end_elevation,
                    "segment_distance": segment_distance,
                    "average_slope": average_slope,
                }
            )
            start_idx = end_idx

    # Merge segments if slope difference is less than min_slope_diff
    i = 0
    while i < len(segments) - 1:
        if (
            abs(segments[i]["average_slope"] - segments[i + 1]["average_slope"])
            < min_slope_diff
        ):
            segments[i]["end_idx"] = segments[i + 1]["end_idx"]
            segments[i]["end_elevation"] = segments[i + 1]["end_elevation"]
            segments[i]["segment_distance"] = (
                df["distance"].iloc[segments[i]["end_idx"]]
                - df["distance"].iloc[segments[i]["start_idx"]]
            )
            segments[i]["average_slope"] = (
                (segments[i]["end_elevation"] - segments[i]["start_elevation"])
                / (segments[i]["segment_distance"] * 1000)
                * 100
            )
            segments.pop(i + 1)
        else:
            i += 1

    return segments


def create_segments_dataframe(df: pd.DataFrame, segments: list) -> pd.DataFrame:
    """Generates a dataframe with the segment information.

    Args:
        df: Dataframe with gpx data.
        segments: List of generated segments from `generate_segments` function.

    Returns:
        pd.DataFrame: Dataframe with generated segment information.
    """
    segments_data = []
    for i, segment in enumerate(segments):
        start_idx = segment["start_idx"]
        end_idx = segment["end_idx"]
        start_elevation = segment["start_elevation"]
        end_elevation = segment["end_elevation"]
        segment_distance = segment["segment_distance"]
        average_slope = segment["average_slope"]

        segments_data.append(
            {
                "segment": f"segment {i+1}",
                "start elevation (m)": start_elevation,
                "end elevation (m)": end_elevation,
                "start point (km)": df["distance"].iloc[start_idx],
                "end point (km)": df["distance"].iloc[end_idx],
                "segment distance (km)": segment_distance,
                "average slope (%)": average_slope,
            }
        )

    segments_df = pd.DataFrame(segments_data)

    return segments_df
