
import math


def calculate_gaze_velocity(
    point1,
    point2,
    timestamp1,
    timestamp2,
    nominal_hz=60,
    max_gap_ratio=1.5,
):
    """
    Calculate average gaze displacement velocity.

    Coordinates: normalized display coordinates.
    Timestamps: microseconds.
    Velocity unit: normalized display units / second.

    Invalid or temporally unreliable pairs return
    velocity=None with an explanatory reason.
    """

    if not math.isfinite(nominal_hz) or nominal_hz <= 0:
        raise ValueError("Nominal frequency must be positive")

    if not math.isfinite(max_gap_ratio) or max_gap_ratio <= 1:
        raise ValueError("max_gap_ratio must be greater than 1")

    if timestamp2 <= timestamp1:
        return {
            "velocity": None,
            "reason": "NON_POSITIVE_INTERVAL",
        }

    def valid_point(point):
        return (
            isinstance(point, (tuple, list))
            and len(point) == 2
            and all(
                isinstance(value, (int, float))
                and not isinstance(value, bool)
                and math.isfinite(value)
                for value in point
            )
        )

    if not valid_point(point1) or not valid_point(point2):
        return {
            "velocity": None,
            "reason": "INVALID_GAZE_POINT",
        }

    delta_us = timestamp2 - timestamp1
    nominal_interval_us = 1_000_000 / nominal_hz

    if delta_us > max_gap_ratio * nominal_interval_us:
        return {
            "velocity": None,
            "reason": "TEMPORAL_GAP",
        }

    delta_seconds = delta_us / 1_000_000

    displacement = math.hypot(
        point2[0] - point1[0],
        point2[1] - point1[1],
    )

    velocity = displacement / delta_seconds

    return {
        "velocity": velocity,
        "reason": None,
    }
