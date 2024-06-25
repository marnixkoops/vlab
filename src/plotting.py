"""Code with plotting functions for visualization."""

import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots


# Plot map
def plot_map(
    df: pd.DataFrame, segments_df: pd.DataFrame, selected_stage: str
) -> go.Figure:
    """Plot map of stage.

    Args:
        df: Dataframe with gpx data.
        selected_stage: Number id of stage selected in sidebar

    Returns:
        Figure: Plotly figure with route of stage on a map.
    """
    map_fig = px.scatter_mapbox(
        df,
        title=f"<b>📍 {selected_stage}",
        lat="latitude",
        lon="longitude",
        hover_data={
            "distance": ":.2f",
            "latitude": ":.2f",
            "longitude": ":.2f",
            "elevation": ":, m",
        },
        height=800,
        width=1200,
        zoom=8,
        color="elevation",
        color_continuous_scale="YlOrRd",
        template="plotly_dark",
    )
    map_fig.update_layout(margin=dict(l=0, b=0), mapbox_style="carto-positron")

    segments_coordinates_df = segments_df.merge(
        df, left_on="start point (km)", right_on="distance"
    ).drop_duplicates("segment")
    segments_coordinates_df["segment_id"] = (
        segments_coordinates_df["segment"].str.split(" ").str[1]
    )

    segment_indicator_fig = px.scatter_mapbox(
        segments_coordinates_df,
        lat="latitude",
        lon="longitude",
        text="segment_id",
        hover_data={
            "segment_id": True,
            "average slope (%)": ":.1f",
        },
        height=800,
        template="plotly_dark",
    )
    segment_indicator_fig.update_traces(
        marker=go.scattermapbox.Marker(color="slategrey", size=17, opacity=1.0),
    )

    map_fig.add_trace(segment_indicator_fig.data[0])

    return map_fig


# def plot_elevation(df: pd.DataFrame) -> go.Figure:
#     """Plot elevation profile.

#     Args:
#         df: Dataframe with gpx data.

#     Returns:
#         Figure: Plotly figure with elevation visualization.
#     """
#     elevation_fig = px.area(
#         df,
#         x="distance",
#         y="elevation",
#         title="📈 Elevation profile",
#         template="plotly_dark",
#     )
#     elevation_fig.update_traces(
#         line_color="#ffe103",
#         line_width=3,
#     )

#     return elevation_fig


def plot_segments(df: pd.DataFrame, segments: list) -> go.Figure:
    """Plot elevation profile with generated segments.

    Args:
        df: Dataframe with gpx data.
        segments: List of generated segments from `generate_segments` function.

    Returns:
        Figure: Plotly figure with segment visualization.
    """
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df["distance"],
            y=df["elevation"],
            mode="lines",
            name="elevation",
            line_color="#ffe103",
            line_width=2,
            fill="tozeroy",
            fillgradient=dict(
                type="vertical",
                colorscale=[
                    (0.0, "rgb(100, 88, 1, .1)"),
                    (1.0, "rgb(229, 31, 28, .1)"),
                ],
            ),
        )
    )

    # Add segment markers
    for i, segment in enumerate(segments):
        start_idx = segment["start_idx"]
        fig.add_trace(
            go.Scatter(
                x=[df["distance"].iloc[start_idx]],
                y=[df["elevation"].iloc[start_idx]],
                mode="markers+text",
                name=f"segment {i+1}",
                text=f"{i+1}<br>{segment['average_slope']:.1f}%",
                textposition="top center",
                marker=dict(
                    color="#dd161d",
                    size=15,
                    symbol="arrow-right",
                    line=dict(width=1, color="white"),
                ),
            )
        )
        fig.add_shape(
            type="line",
            x0=df["distance"].iloc[start_idx],
            x1=df["distance"].iloc[start_idx],
            y0=0,
            y1=df["elevation"].iloc[start_idx],
            line=dict(color="#ffe103", width=1, dash="dot"),
        )

    num_segments = len(segments)
    fig.update_layout(
        title=f"📈 Elevation profile with {num_segments} segments and average slopes",
        xaxis_title="distance (km)",
        yaxis_title="elevation (m)",
        template="plotly_dark",
        height=600,
        showlegend=False,
        xaxis=dict(
            rangeslider=dict(visible=False),
            range=[0, df["distance"].max()],  # Ensure x-axis starts at 0
        ),
    )

    return fig


def plot_glycogen(df: pd.DataFrame) -> go.Figure:
    """Plot KPI profile with fatigue and failure thresholds.

    Args:
        df: Dataframe with gpx data.

    Returns:
        Figure: Plotly figure with KPI visualization.
    """
    fig = go.Figure()

    # KPI plot
    fig.add_trace(
        go.Scatter(
            x=df["start point (km)"],
            y=df["glycogen level (%)"],
            mode="lines",
            name="glycogen level (%)",
            line_color="#1f77b4",
            line_width=2,
        )
    )

    # Add horizontal lines for fatigue and failure thresholds
    fig.add_trace(
        go.Scatter(
            x=[df["start point (km)"].min(), df["end point (km)"].max()],
            y=[35, 35],
            mode="lines",
            line=dict(color="orange", width=2, dash="dash"),
            showlegend=True,
            name="Fatigue Threshold",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[df["start point (km)"].min(), df["end point (km)"].max()],
            y=[10, 10],
            mode="lines",
            line=dict(color="red", width=2, dash="dash"),
            showlegend=True,
            name="Failure Threshold",
        )
    )

    return fig


def plot_elevation_only(df: pd.DataFrame) -> go.Scatter:
    """Create a transparent elevation trace for overlay.

    Args:
        df: Dataframe with gpx data.

    Returns:
        Scatter: Plotly scatter trace with elevation visualization.
    """
    return go.Scatter(
        x=df["distance"],
        y=df["elevation"],
        mode="lines",
        name="elevation",
        line_color="rgba(255, 225, 3, 0.2)",  # Make the line more transparent
        line_width=2,
        fill="tozeroy",
        fillcolor="rgba(255, 225, 3, 0.05)",  # Transparent fill color
        showlegend=False,  # Hide from legend
    )


def combine_plots(
    df: pd.DataFrame, segments: list, segments_df: pd.DataFrame
) -> go.Figure:
    """Combine elevation and glycogen plots into one figure with transparent background for the elevation plot.

    Args:
        df: Dataframe with elevation data.
        segments: List of segments for elevation data.
        segments_df: Dataframe with glycogen data.

    Returns:
        Figure: Plotly figure with combined visualization.
    """
    """Combine elevation and glycogen plots into one figure with transparent background for the elevation plot.

    Args:
        df_segments: Dataframe with elevation data.
        segments: List of segments for elevation data.
        df_glycogen: Dataframe with glycogen data.

    Returns:
        Figure: Plotly figure with combined visualization.
    """
    elevation_trace = plot_elevation_only(df)
    glycogen_fig = plot_glycogen(segments_df)

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add glycogen trace
    for trace in glycogen_fig["data"]:
        fig.add_trace(trace, secondary_y=False)

    # Add elevation trace
    fig.add_trace(elevation_trace, secondary_y=True)

    # Add vertical segment separation lines
    for segment in segments:
        start_idx = segment["start_idx"]
        x_value = df["distance"].iloc[start_idx]
        y_value = df["elevation"].iloc[start_idx]
        fig.add_shape(
            type="line",
            x0=x_value,
            x1=x_value,
            y0=0,
            y1=y_value,
            yref="y2",
            line=dict(color="rgba(255, 255, 255, 0.4)", width=1, dash="dot"),
        )

    fig.update_layout(
        title="🏔️ Glycogen Depletion with Fatigue and Failure Thresholds",
        xaxis_title="distance (km)",
        yaxis=dict(
            title="glycogen level (%)", side="left", range=[0, 100]
        ),  # Ensure y-axis starts at 0
        yaxis2=dict(
            title="elevation (m)",
            side="right",
            overlaying="y",
            range=[0, df["elevation"].max()],
            showgrid=False,
            showticklabels=True,
        ),  # Ensure y-axis starts at 0
        xaxis=dict(range=[0, df["distance"].max()]),  # Ensure x-axis starts at 0
        template="plotly_dark",
        height=800,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    return fig
