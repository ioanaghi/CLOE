
import math


def is_within_recording_bounds(
    window_start_s,
    window_end_s,
    recording_duration_s,
):
    """
    Check whether a window lies within the observed
    timestamp span of a recording.

    This does NOT prove continuous data acquisition.
    """

    values = (
        window_start_s,
        window_end_s,
        recording_duration_s,
    )

    if not all(math.isfinite(value) for value in values):
        raise ValueError("Time values must be finite")

    if recording_duration_s < 0:
        raise ValueError("Recording duration cannot be negative")

    if window_start_s < 0 or window_end_s <= window_start_s:
        raise ValueError("Invalid window boundaries")

    return window_end_s <= recording_duration_s
