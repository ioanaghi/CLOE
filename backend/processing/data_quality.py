import math


def assess_window_quality(window,nominal_hz=60):
    """
    Calculate data-quality metrics for a feature window.

    This function does not estimate cognitive load.
    """

    if not math.isfinite(nominal_hz) or nominal_hz <= 0:
        raise ValueError("Nominal frequency must be positive and finite.")

    start_s = window["start_s"]
    end_s = window["end_s"]
    sample_count = window["sample_count"]
    invalid_count = window["invalid_sample_count"]
    availability = window["gaze_availability_rate"]


    if end_s <= start_s:
        raise ValueError("Window end time must be greater than start time.")
    
    if not isinstance(sample_count, int) or sample_count < 0:
        raise ValueError("Invalid sample count.")

    if not isinstance(invalid_count, int):
        raise ValueError("Invalid invalid sample count.")

    if not 0<= invalid_count <= sample_count:
        raise ValueError("Invalid sample count exceeds total samples")

    if sample_count == 0:
        if availability is not None:
            raise ValueError("Empty windows must have unknown availability")
    else:
        if availability is None or not math.isfinite(availability):
            raise ValueError("Non-empty windows require finite availability")

        expected_availability = (
            sample_count - invalid_count
        ) / sample_count

        if not math.isclose(availability, expected_availability):
            raise ValueError("Inconsistent availability rate")

    duration_s = end_s - start_s
    expected_samples = nominal_hz * duration_s

    usable_samples = sample_count - invalid_count

    nominal_sample_ratio = sample_count / expected_samples
    usable_nominal_ratio = usable_samples / expected_samples

    return {
        "start_s": start_s,
        "end_s": end_s,
        "sample_count": sample_count,
        "usable_sample_count": usable_samples,
        "gaze_availability_rate": availability,
        "nominal_sample_ratio": nominal_sample_ratio,
        "usable_nominal_ratio": usable_nominal_ratio,
        "has_data": sample_count > 0,
    }
