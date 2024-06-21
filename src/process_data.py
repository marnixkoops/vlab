"""Code to parse and process .gpx data into a dataframe."""

import logging

import gpxpy
import numpy as np
import pandas as pd
from scipy.ndimage import gaussian_filter1d

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s 🚴‍♂️ %(message)s",
)


def read_gpx_file(path: str) -> gpxpy.gpx.GPX:
    """Read a gpx file from a specified path.

    Args:
        path: path of file location to read.

    Returns:
        gpxpy.gpx.GPX: gpx file object.
    """
    logger.info(f"Reading gpx file from path: {path}")
    with open(path, "r") as gpx_file:
        gpx_file = gpxpy.parse(gpx_file)

    return gpx_file


def create_dataframe(gpx_file: gpxpy.gpx.GPX) -> pd.DataFrame:
    """Create a pandas DataFrame from the gpx file.

    Also calculates the distance between each point, the elevation difference, and
    gradients.

    Args:
        gpx_file: gpx file object.

    Returns:
        pd.DataFrame: Dataframe with gpx data.
    """
    logger.info("Parsing gpx file to a pandas DataFrame.")

    route_info = []
    for track in gpx_file.tracks:
        for segment in track.segments:
            for point in segment.points:
                route_info.append(
                    {
                        "latitude": point.latitude,
                        "longitude": point.longitude,
                        "elevation": point.elevation,
                    }
                )
    df = pd.DataFrame(route_info)

    df["distance"] = np.nan
    total_distance = 0
    for i in range(1, len(df)):
        prev_point = (df.at[i - 1, "latitude"], df.at[i - 1, "longitude"])
        curr_point = (df.at[i, "latitude"], df.at[i, "longitude"])
        distance = gpxpy.geo.haversine_distance(
            prev_point[0], prev_point[1], curr_point[0], curr_point[1]
        )
        total_distance += distance
        df.at[i, "distance"] = total_distance / 1000  # Convert to kilometers
    df.loc[0, "distance"] = 0

    df["elevation_diff"] = df["elevation"].diff()
    df.loc[0, "elevation_diff"] = 0

    df["gradient"] = 0.0
    for i in range(1, len(df)):
        elevation_diff = df.at[i, "elevation"] - df.at[i - 1, "elevation"]
        # Convert back to meters for gradient calculation
        distance_diff = (df.at[i, "distance"] - df.at[i - 1, "distance"]) * 1000
        df.at[i, "gradient"] = _calculate_gradient(elevation_diff, distance_diff)

    # Smooth the elevation data
    df["smoothed_elevation"] = gaussian_filter1d(df["elevation"], sigma=2)

    logger.info(f"DataFrame shape: {df.shape}")

    return df


def _calculate_gradient(elevation_diff, distance_diff) -> float:
    """Calculate the gradient between two points.

    Args:
        elevation_diff: Difference in elevation between two points.
        distance_diff: Difference in distance between two points.

    Returns:
        float: Computed gradient between two points.
    """
    if distance_diff == 0:
        return 0
    return (elevation_diff / distance_diff) * 100
