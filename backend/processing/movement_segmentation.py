
import math


LOW = "LOW_VELOCITY"
HIGH = "HIGH_VELOCITY"
UNKNOWN = "UNKNOWN"


def validate_velocity_threshold(threshold):
    if (
        isinstance(threshold, bool)
        or not isinstance(threshold, (int, float))
        or not math.isfinite(threshold)
        or threshold <= 0
    ):
        raise ValueError(
            "Velocity threshold must be positive and finite"
        )


def classify_velocity(velocity, threshold):
    """
    Classify a single gaze displacement velocity.

    Units: normalized display units per second.

    The threshold is experimental, not physiological.
    """
    validate_velocity_threshold(threshold)

    if velocity is None:
        return UNKNOWN

    if (
        isinstance(velocity, bool)
        or not isinstance(velocity, (int, float))
        or not math.isfinite(velocity)
    ):
        return UNKNOWN

    if velocity < 0:
        raise ValueError("Velocity cannot be negative")

    if velocity < threshold:
        return LOW

    return HIGH


def segment_velocity_states(
    velocity_results,
    threshold,
):
    """
    Group consecutive velocity classifications.

    Each input is a dictionary returned by
    calculate_gaze_velocity().

    Example input:
        [
            {"velocity": 2.0, "reason": None},
            {"velocity": None, "reason": "TEMPORAL_GAP"},
        ]

    Segment indices refer to velocity intervals,
    not directly to gaze sample indices.
    """

    validate_velocity_threshold(threshold)

    if not velocity_results:
        return []

    states = []

    for result in velocity_results:
        state = classify_velocity(
            result["velocity"],
            threshold,
        )
        states.append(state)

    segments = []
    start = 0
    current_state = states[0]

    for index in range(1, len(states)):
        if states[index] != current_state:
            segments.append({
                "state": current_state,
                "start_interval_index": start,
                "end_interval_index": index - 1,
                "interval_count": index - start,
            })

            start = index
            current_state = states[index]

    # The last segment must also be recorded.
    segments.append({
        "state": current_state,
        "start_interval_index": start,
        "end_interval_index": len(states) - 1,
        "interval_count": len(states) - start,
    })

    return segments
