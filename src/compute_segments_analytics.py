"""Code to ..."""

from scipy.optimize import fsolve


def define_drafting_decisions(segments, semi_draft_point=0.6, full_draft_point=0.9):
    num_segments = len(segments)

    if isinstance(semi_draft_point, float):
        semi_draft_segment = int(num_segments * semi_draft_point)
    elif isinstance(semi_draft_point, int):
        semi_draft_segment = semi_draft_point
    else:
        raise ValueError("The semi draft point must either be an integer or a float")

    if isinstance(full_draft_point, float):
        full_draft_segment = int(num_segments * full_draft_point)
    elif isinstance(full_draft_point, int):
        full_draft_segment = full_draft_point
    else:
        raise ValueError("The full draft point must either be an integer or a float")

    segments["drafting"] = ""

    for i in range(num_segments):
        if i < semi_draft_segment:
            segments.loc[i, "drafting"] = "Full Draft"
        elif i < full_draft_segment:
            segments.loc[i, "drafting"] = "Semi Draft"
        else:
            segments.loc[i, "drafting"] = "No Draft"

    return segments, semi_draft_segment, full_draft_segment


def find_velocity(
    total_power,
    air_density,
    cda_value,
    CRR,
    total_mass,
    gravity,
    length_segment_m,
    friction_loss,
    gravitational_power,
):
    def equations(velocity):
        air_resistance = 0.5 * air_density * cda_value * (velocity**3)
        rolling_resistance = CRR * total_mass * gravity * velocity
        time_sec = length_segment_m / velocity
        gravitational_power_watt = gravitational_power / time_sec
        total_power_watt = (1 + friction_loss) * (
            air_resistance + rolling_resistance + gravitational_power_watt
        )
        return total_power_watt - total_power

    velocity_initial_guess = 5  # Initial guess for velocity
    velocity_solution = fsolve(equations, velocity_initial_guess)
    return velocity_solution[0]


def calculate_climbing_duration(
    time_sec=None,
    relative_power=None,
    length_segment_km=None,
    elevation_gain_m=None,
    rider=None,
    drafting=None,
):
    # Constants
    air_density = 1.15
    CRR = 0.004
    gravity = 9.81  # m/s^2
    additional_mass = 7.8  # Additional mass for bike/equipment
    friction_loss = 0.02

    if (
        length_segment_km is None
        or elevation_gain_m is None
        or rider is None
        or drafting is None
    ):
        return "Please specify the length of the segment (in km), elevation gain, rider details, and drafting condition."

    # Convert length from kilometers to meters
    length_segment_m = length_segment_km * 1000

    # Extract rider details
    weight_rider = rider.get("weight_rider")
    cda_values = rider.get("cda_values", {})
    cda_value = cda_values.get(drafting, cda_values.get("Full Draft"))

    if weight_rider is None or cda_value is None:
        return "Please specify the weight of the rider and CdA values for the drafting condition."

    total_mass = (
        weight_rider + additional_mass
    )  # Total mass including rider and equipment

    if time_sec is not None:
        # Calculate velocity
        velocity = length_segment_m / time_sec

        # Air Resistance Calculation
        air_resistance_watt = 0.5 * air_density * cda_value * (velocity**3)

        # Rolling Resistance Calculation
        rolling_resistance_watt = CRR * total_mass * gravity * velocity

        # Gravitational Power Calculation
        gravitational_power_watt = (total_mass * gravity * elevation_gain_m) / time_sec

        # Total Power Calculation
        total_power_watt = (1 + friction_loss) * (
            air_resistance_watt + rolling_resistance_watt + gravitational_power_watt
        )

        # relative power Calculation
        relative_power_watt_per_kg = total_power_watt / weight_rider

        #         print("relative power (W/kg): " + str(relative_power_watt_per_kg))
        return relative_power_watt_per_kg

    elif relative_power is not None:
        # Calculate total power from relative power per kg
        total_power_watt = relative_power * weight_rider

        # Gravitational power portion
        gravitational_power = total_mass * gravity * elevation_gain_m

        velocity = find_velocity(
            total_power_watt,
            air_density,
            cda_value,
            CRR,
            total_mass,
            gravity,
            length_segment_m,
            friction_loss,
            gravitational_power,
        )

        # Calculate time required
        time_required = round(length_segment_m / velocity)

        #         print("Time Required (sec): " + str(time_required))
        return time_required

    else:
        return "Please specify either time in seconds or relative power, not both."


def apply_descending_duration(row, average_speed):
    return row["segment distance (km)"] * 3600 / average_speed


def apply_climbing_duration(row, rider_stats):
    # Define the logic for the negative elevation gain
    return calculate_climbing_duration(
        time_sec=None,
        relative_power=row["relative power"],
        length_segment_km=row["segment distance (km)"],
        elevation_gain_m=abs(row["end elevation (m)"] - row["start elevation (m)"]),
        rider=rider_stats,
        drafting=row["drafting"],
    )


def apply_duration(row, rider_stats, average_speed=50):
    if row["end elevation (m)"] >= row["start elevation (m)"]:
        return apply_climbing_duration(row, rider_stats)
    else:
        return apply_descending_duration(row, average_speed)


def compute_glycogen_level(segments, glycogen_start_level=100):
    new_column = []
    previous_value = glycogen_start_level

    for index, row in segments.iterrows():
        if index == 0:
            new_value = glycogen_start_level
        elif row["average slope (%)"] < 0:
            new_value = previous_value
        else:
            new_value = (
                previous_value * row["relative power"] / 6
            )  # Example function: summing previous value and parameter
        new_column.append(new_value)
        previous_value = new_value

    segments["glycogen level (%)"] = new_column
    return segments
