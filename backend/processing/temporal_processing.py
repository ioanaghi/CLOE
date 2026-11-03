
def analyze_timestamps(timestamps, nominal_hz=60):
    if nominal_hz <= 0:
        raise ValueError("Nominal frequency must be positive")

    if len(timestamps) < 2:
        return {
            "intervals_us": [],
            "non_positive_intervals": 0,
            "large_gaps": [],
            "estimated_missing_samples": 0,
        }

    nominal_interval_us = 1_000_000 / nominal_hz

    intervals = []
    large_gaps = []
    estimated_missing = 0
    non_positive = 0

    for i in range(1, len(timestamps)):
        dt = timestamps[i] - timestamps[i - 1]
        intervals.append(dt)

        if dt <= 0:
            non_positive += 1
            continue

        if dt > 1.5 * nominal_interval_us:
            estimated_count = max(
                0,
                round(dt / nominal_interval_us) - 1
            )

            large_gaps.append({
                "index": i,
                "duration_us": dt,
                "estimated_missing": estimated_count,
            })

            estimated_missing += estimated_count

    return {
        "intervals_us": intervals,
        "non_positive_intervals": non_positive,
        "large_gaps": large_gaps,
        "estimated_missing_samples": estimated_missing,
    }
