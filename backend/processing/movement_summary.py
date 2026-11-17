
import math


STATES = ("LOW_VELOCITY", "HIGH_VELOCITY", "UNKNOWN")
VALID_STATES = {"LOW_VELOCITY", "HIGH_VELOCITY"}


def summarize_movement_segments(segments, total_intervals):
    """
    Summarize a complete, ordered partition of velocity intervals.

    Expected input:
        Segments enriched with duration_ms by T03-A.

    Segment indices are inclusive and must cover exactly
    [0, total_intervals - 1], without gaps or overlaps.

    Durations represent observed timestamp spans,
    not validated physiological event durations.
    """

    if (
        isinstance(total_intervals, bool)
        or not isinstance(total_intervals, int)
        or total_intervals < 0
    ):
        raise ValueError("total_intervals must be a nonnegative integer")

    if total_intervals == 0:
        if segments:
            raise ValueError("Zero intervals require zero segments")
    elif not segments:
        raise ValueError("Nonempty intervals require segments")

    interval_counts = {state: 0 for state in STATES}
    segment_counts = {state: 0 for state in STATES}
    durations = {state: [] for state in STATES}

    expected_start = 0
    previous_state = None

    transition_count = 0
    direct_low_high_transitions = 0
    internal_unknown_runs = 0

    for index, segment in enumerate(segments):
        state = segment["state"]
        start = segment["start_interval_index"]
        end = segment["end_interval_index"]
        count = segment["interval_count"]
        duration = segment["duration_ms"]

        if state not in STATES:
            raise ValueError("Unknown movement state")

        if any(
            isinstance(value, bool) or not isinstance(value, int)
            for value in (start, end, count)
        ):
            raise ValueError("Segment indices must be integers")

        if start != expected_start:
            raise ValueError("Segments must be ordered and contiguous")

        if not (start <= end < total_intervals):
            raise ValueError("Segment boundaries are out of bounds")

        if count != end - start + 1:
            raise ValueError("Inconsistent segment interval count")

        if (
            isinstance(duration, bool)
            or not isinstance(duration, (int, float))
            or not math.isfinite(duration)
            or duration <= 0
        ):
            raise ValueError("Segment duration must be positive and finite")

        if previous_state == state:
            raise ValueError(
                "Adjacent segments must have different states"
            )

        interval_counts[state] += count
        segment_counts[state] += 1
        durations[state].append(duration)

        if previous_state is not None:
            transition_count += 1

            if (
                previous_state in VALID_STATES
                and state in VALID_STATES
            ):
                direct_low_high_transitions += 1

        if (
            state == "UNKNOWN"
            and index > 0
            and index < len(segments) - 1
            and segments[index - 1]["state"] in VALID_STATES
            and segments[index + 1]["state"] in VALID_STATES
        ):
            internal_unknown_runs += 1

        expected_start = end + 1
        previous_state = state

    if expected_start != total_intervals:
        raise ValueError("Segments do not cover all intervals")

    interval_shares = {
        state: (
            interval_counts[state] / total_intervals
            if total_intervals else None
        )
        for state in STATES
    }

    total_durations = {
        state: sum(durations[state])
        for state in STATES
    }

    mean_durations = {
        state: (
            sum(durations[state]) / len(durations[state])
            if durations[state] else None
        )
        for state in STATES
    }

    max_durations = {
        state: (
            max(durations[state])
            if durations[state] else None
        )
        for state in STATES
    }

    return {
        "total_intervals": total_intervals,
        "segment_count": len(segments),
        "interval_count_by_state": interval_counts,
        "interval_share_by_state": interval_shares,
        "segment_count_by_state": segment_counts,
        "total_duration_ms_by_state": total_durations,
        "mean_duration_ms_by_state": mean_durations,
        "max_duration_ms_by_state": max_durations,
        "transition_count": transition_count,
        "direct_low_high_transitions": (
            direct_low_high_transitions
        ),
        "internal_unknown_runs": internal_unknown_runs,
    }
