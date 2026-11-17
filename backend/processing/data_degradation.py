
import math
from copy import deepcopy


INVALID_GAZE_REASON = "SIMULATED_INVALID_GAZE"
DROPPED_SAMPLE_REASON = "SIMULATED_DROPPED_SAMPLE_BRIDGE"


def validate_input(timestamps, velocity_results):
    """
    Validate a consecutive timestamp/velocity sequence.

    Timestamps are integer microseconds.
    Exactly N-1 velocity intervals are expected for N samples.
    """
    if len(velocity_results) != max(0, len(timestamps) - 1):
        raise ValueError("Timestamp/velocity count mismatch")

    for timestamp in timestamps:
        if isinstance(timestamp, bool) or not isinstance(timestamp, int):
            raise ValueError("Timestamps must be integer microseconds")

    if any(
        timestamps[i] <= timestamps[i - 1]
        for i in range(1, len(timestamps))
    ):
        raise ValueError("Timestamps must be strictly increasing")

    for interval in velocity_results:
        if not isinstance(interval, dict):
            raise ValueError("Velocity result must be a dictionary")

        if "velocity" not in interval:
            raise ValueError("Velocity result missing velocity field")

        value = interval["velocity"]

        if value is not None:
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
                or value < 0
            ):
                raise ValueError("Invalid velocity value")


def validate_indices(indices, sample_count):
    """
    Require unique integer indices within the sample sequence.
    """
    try:
        values = list(indices)
    except TypeError as exc:
        raise ValueError("Indices must be iterable") from exc

    if len(values) != len(set(map(repr, values))):
        raise ValueError("Duplicate sample indices")

    for index in values:
        if isinstance(index, bool) or not isinstance(index, int):
            raise ValueError("Sample index must be an integer")

        if index < 0 or index >= sample_count:
            raise ValueError("Sample index out of bounds")

    return set(values)


def simulate_invalid_gaze(
    timestamps,
    velocity_results,
    invalid_indices,
):
    """
    Simulate received samples with unusable gaze.

    Timestamps and sample count are preserved.
    Every velocity interval touching an invalidated sample
    becomes UNKNOWN.

    Existing UNKNOWN intervals are preserved.
    """
    validate_input(timestamps, velocity_results)

    selected = validate_indices(
        invalid_indices,
        len(timestamps),
    )

    degraded = deepcopy(velocity_results)

    for sample_index in selected:
        for interval_index in (
            sample_index - 1,
            sample_index,
        ):
            if 0 <= interval_index < len(degraded):
                degraded[interval_index]["velocity"] = None
                degraded[interval_index]["reason"] = (
                    INVALID_GAZE_REASON
                )

    return {
        "timestamps": list(timestamps),
        "velocity_results": degraded,
        "sample_count": len(timestamps),
        "modified_sample_count": len(selected),
        "scenario": "INVALID_GAZE",
    }


def simulate_sample_dropout(
    timestamps,
    velocity_results,
    dropped_indices,
):
    """
    Remove selected received samples.

    Existing velocity results are reused only when the
    surviving samples were consecutive in the original data.

    New intervals bridging removed samples are UNKNOWN:
    we do not estimate or fabricate their velocity.
    """
    validate_input(timestamps, velocity_results)

    dropped = validate_indices(
        dropped_indices,
        len(timestamps),
    )

    kept = [
        index
        for index in range(len(timestamps))
        if index not in dropped
    ]

    new_timestamps = [
        timestamps[index]
        for index in kept
    ]

    new_velocities = []

    for left_index, right_index in zip(kept, kept[1:]):
        if right_index == left_index + 1:
            # Original consecutive pair: safely reuse result.
            interval = deepcopy(
                velocity_results[left_index]
            )
        else:
            # At least one sample was removed between endpoints.
            interval = {
                "velocity": None,
                "reason": DROPPED_SAMPLE_REASON,
            }

        new_velocities.append(interval)

    return {
        "timestamps": new_timestamps,
        "velocity_results": new_velocities,
        "sample_count": len(new_timestamps),
        "modified_sample_count": len(dropped),
        "scenario": "SAMPLE_DROPOUT",
    }


def calculate_degradation_metrics(
    timestamps,
    velocity_results,
    nominal_hz=60.0,
    max_gap_ratio=1.5,
):
    """
    Calculate diagnostic availability and temporal-gap metrics.

    Large gaps are detected from received timestamps.
    They are not treated as proof of physical packet loss.
    """
    validate_input(timestamps, velocity_results)

    if (
        isinstance(nominal_hz, bool)
        or not isinstance(nominal_hz, (int, float))
        or not math.isfinite(nominal_hz)
        or nominal_hz <= 0
    ):
        raise ValueError("Invalid nominal frequency")

    if (
        isinstance(max_gap_ratio, bool)
        or not isinstance(max_gap_ratio, (int, float))
        or not math.isfinite(max_gap_ratio)
        or max_gap_ratio <= 1
    ):
        raise ValueError("Invalid maximum gap ratio")

    available = sum(
        interval["velocity"] is not None
        for interval in velocity_results
    )

    unknown = len(velocity_results) - available

    nominal_interval_us = 1_000_000 / nominal_hz
    gap_limit_us = nominal_interval_us * max_gap_ratio

    large_gaps = sum(
        timestamps[i + 1] - timestamps[i] > gap_limit_us
        for i in range(max(0, len(timestamps) - 1))
    )

    interval_count = len(velocity_results)

    return {
        "sample_count": len(timestamps),
        "interval_count": interval_count,
        "available_velocity_count": available,
        "unknown_velocity_count": unknown,
        "velocity_availability_rate": (
            available / interval_count
            if interval_count else None
        ),
        "large_temporal_gap_count": large_gaps,
    }
