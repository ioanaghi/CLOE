
import math

from backend.processing.movement_segmentation import (
    segment_velocity_states,
    validate_velocity_threshold,
)
from backend.processing.segment_features import (
    calculate_segment_durations,
    calculate_segment_velocity_stats,
)
from backend.processing.movement_summary import (
    summarize_movement_segments,
)


def extract_window_oculomotor_features(
    timestamps,
    velocity_results,
    start_s,
    end_s,
    threshold,
    quality_gate_status,
):
    """
    Extract features from velocity intervals fully contained
    within a window.

    timestamps: original device timestamps (microseconds)
    velocity_results: one result per consecutive sample pair
    start_s, end_s: seconds relative to the first timestamp
    threshold: normalized display units per second
    quality_gate_status: ELIGIBLE or UNKNOWN

    UNKNOWN quality windows do not produce usable features.
    """

    validate_velocity_threshold(threshold)

    if quality_gate_status not in ("ELIGIBLE", "UNKNOWN"):
        raise ValueError("Invalid Quality Gate status")

    if any(
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
        for value in (start_s, end_s)
    ):
        raise ValueError("Window boundaries must be finite numbers")

    if start_s < 0 or end_s <= start_s:
        raise ValueError("Invalid window boundaries")

    if any(
        isinstance(t, bool) or not isinstance(t, int)
        for t in timestamps
    ):
        raise ValueError("Timestamps must be integer microseconds")

    if any(
        timestamps[i] <= timestamps[i - 1]
        for i in range(1, len(timestamps))
    ):
        raise ValueError("Timestamps must be strictly increasing")

    if len(velocity_results) != max(0, len(timestamps) - 1):
        raise ValueError("Velocity interval count mismatch")

    # First recorded timestamp defines the relative time origin.
    origin_us = timestamps[0] if timestamps else 0

    selected_indices = []

    for index in range(len(velocity_results)):
        interval_start_s = (
            timestamps[index] - origin_us
        ) / 1_000_000

        interval_end_s = (
            timestamps[index + 1] - origin_us
        ) / 1_000_000

        if (
            interval_start_s >= start_s
            and interval_end_s <= end_s
        ):
            selected_indices.append(index)

    base_result = {
        "start_s": start_s,
        "end_s": end_s,
        "threshold": threshold,
        "quality_gate_status": quality_gate_status,
        "selected_interval_count": len(selected_indices),
        "feature_status": "UNAVAILABLE",
        "feature_reason": None,
        "features": None,
    }

    # M0.3 Quality Gate takes precedence.
    if quality_gate_status == "UNKNOWN":
        base_result["feature_reason"] = "QUALITY_GATE_UNKNOWN"
        return base_result

    if not selected_indices:
        base_result["feature_reason"] = "NO_CONTAINED_INTERVALS"
        return base_result

    # With increasing timestamps and a continuous time window,
    # fully contained intervals form one consecutive slice.
    first = selected_indices[0]
    last = selected_indices[-1]

    if selected_indices != list(range(first, last + 1)):
        raise ValueError("Selected intervals are not contiguous")

    local_velocities = velocity_results[first:last + 1]
    local_timestamps = timestamps[first:last + 2]

    segments = segment_velocity_states(
        local_velocities,
        threshold=threshold,
    )

    with_durations = calculate_segment_durations(
        segments,
        local_timestamps,
    )

    with_statistics = calculate_segment_velocity_stats(
        with_durations,
        local_velocities,
    )

    summary = summarize_movement_segments(
        with_statistics,
        total_intervals=len(local_velocities),
    )

    base_result["feature_status"] = "AVAILABLE"
    base_result["features"] = summary

    return base_result
