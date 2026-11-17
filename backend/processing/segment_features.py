
import math
import statistics


VALID_STATES = {
    "LOW_VELOCITY",
    "HIGH_VELOCITY",
    "UNKNOWN",
}


def calculate_segment_durations(segments, timestamps):
    """
    Attach timestamp-based durations to movement segments.

    Segment indices refer to velocity intervals.
    For a segment [start, end], the timestamp span is:
        timestamps[end + 1] - timestamps[start]

    Timestamps: microseconds.
    Output duration: milliseconds.

    For UNKNOWN segments, duration is an observed
    timestamp span, not confirmed tracking-loss duration.
    """

    if not timestamps:
        if segments:
            raise ValueError("Segments require timestamps")
        return []

    if any(
        isinstance(t, bool)
        or not isinstance(t, int)
        for t in timestamps
    ):
        raise ValueError("Timestamps must be integer microseconds")

    if any(
        timestamps[i] <= timestamps[i - 1]
        for i in range(1, len(timestamps))
    ):
        raise ValueError("Timestamps must be strictly increasing")

    interval_total = len(timestamps) - 1
    results = []

    for segment in segments:
        state = segment["state"]
        start = segment["start_interval_index"]
        end = segment["end_interval_index"]
        count = segment["interval_count"]

        if state not in VALID_STATES:
            raise ValueError("Unknown movement state")

        if any(
            isinstance(value, bool)
            or not isinstance(value, int)
            for value in (start, end, count)
        ):
            raise ValueError("Segment indices must be integers")

        if not (
            0 <= start <= end < interval_total
        ):
            raise ValueError("Segment indices are out of bounds")

        if count != end - start + 1:
            raise ValueError("Inconsistent interval count")

        start_us = timestamps[start]
        end_us = timestamps[end + 1]

        duration_ms = (end_us - start_us) / 1000.0

        results.append({
            **segment,
            "start_timestamp_us": start_us,
            "end_timestamp_us": end_us,
            "duration_ms": duration_ms,
        })

    return results


def calculate_segment_velocity_stats(segments, velocity_results):
    """
    Calculate per-segment velocity statistics.

    Segments use velocity interval indices.
    velocity_results contains dictionaries with a
    'velocity' field, potentially set to None.

    LOW/HIGH segments require finite, nonnegative
    velocities for all included intervals.

    UNKNOWN segments require unavailable velocities.

    Statistics are arithmetic (not time-weighted).
    The original inputs are not modified.
    """

    results = []

    for segment in segments:
        state = segment["state"]
        start = segment["start_interval_index"]
        end = segment["end_interval_index"]
        count = segment["interval_count"]

        if state not in VALID_STATES:
            raise ValueError("Unknown movement state")

        if any(
            isinstance(value, bool) or not isinstance(value, int)
            for value in (start, end, count)
        ):
            raise ValueError("Segment indices must be integers")

        if not 0 <= start <= end < len(velocity_results):
            raise ValueError("Segment indices are out of bounds")

        if count != end - start + 1:
            raise ValueError("Inconsistent interval count")

        values = [
            item["velocity"]
            for item in velocity_results[start:end + 1]
        ]

        if state == "UNKNOWN":
            if any(value is not None for value in values):
                raise ValueError(
                    "UNKNOWN segments must contain unavailable velocities"
                )

            stats = {
                "valid_velocity_count": 0,
                "mean_velocity": None,
                "min_velocity": None,
                "max_velocity": None,
                "std_velocity": None,
            }

        else:
            for value in values:
                if (
                    isinstance(value, bool)
                    or not isinstance(value, (int, float))
                    or not math.isfinite(value)
                    or value < 0
                ):
                    raise ValueError(
                        "LOW/HIGH segments require valid velocities"
                    )

            stats = {
                "valid_velocity_count": len(values),
                "mean_velocity": statistics.fmean(values),
                "min_velocity": min(values),
                "max_velocity": max(values),
                "std_velocity": statistics.pstdev(values),
            }

        results.append({
            **segment,
            **stats,
        })

    return results
