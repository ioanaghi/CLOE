
import math

from backend.processing.feature_reliability import state_shares


STATES = ("LOW_VELOCITY", "HIGH_VELOCITY", "UNKNOWN")


def calculate_overlap(first, second):
    """
    Calculate temporal intersection between two windows.

    The overlap ratio is normalized by the shorter window.
    It measures temporal overlap, not shared sample count.
    """
    duration_a = first["end_s"] - first["start_s"]
    duration_b = second["end_s"] - second["start_s"]

    if duration_a <= 0 or duration_b <= 0:
        raise ValueError("Window durations must be positive")

    overlap = max(
        0.0,
        min(first["end_s"], second["end_s"])
        - max(first["start_s"], second["start_s"]),
    )

    return {
        "overlap_duration_s": overlap,
        "overlap_ratio": overlap / min(duration_a, duration_b),
    }


def compare_windows(first, second):
    """
    Compare two windows from the same threshold dataset.

    Unavailable windows are preserved as non-comparable.
    """
    if not math.isclose(
        first["threshold"],
        second["threshold"],
        rel_tol=0,
        abs_tol=1e-9,
    ):
        raise ValueError("Cannot compare different thresholds")

    overlap = calculate_overlap(first, second)

    result = {
        "first_start_s": first["start_s"],
        "second_start_s": second["start_s"],
        **overlap,
        "pair_status": "UNAVAILABLE",
        "low_share_difference": None,
        "high_share_difference": None,
        "unknown_share_difference": None,
        "mean_state_difference": None,
    }

    if (
        first["feature_status"] != "AVAILABLE"
        or second["feature_status"] != "AVAILABLE"
    ):
        return result

    shares_a = state_shares(first)
    shares_b = state_shares(second)

    differences = {
        state: abs(shares_a[state] - shares_b[state])
        for state in STATES
    }

    result.update({
        "pair_status": "COMPARABLE",
        "low_share_difference": differences["LOW_VELOCITY"],
        "high_share_difference": differences["HIGH_VELOCITY"],
        "unknown_share_difference": differences["UNKNOWN"],
        "mean_state_difference": (
            sum(differences.values()) / len(STATES)
        ),
    })

    return result


def analyze_temporal_stability(windows, offset=1):
    """
    Compare windows separated by a fixed index offset.

    offset=1: consecutive windows
    offset=2: windows separated by one window

    Input window order is preserved.
    """
    if (
        isinstance(offset, bool)
        or not isinstance(offset, int)
        or offset < 1
    ):
        raise ValueError("Offset must be a positive integer")

    for index, window in enumerate(windows):
        start = window["start_s"]
        end = window["end_s"]
        threshold = window["threshold"]

        if any(
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
            for value in (start, end, threshold)
        ):
            raise ValueError("Invalid window value")

        if start < 0 or end <= start or threshold <= 0:
            raise ValueError("Invalid window boundaries or threshold")

        if index > 0:
            previous = windows[index - 1]

            if start <= previous["start_s"]:
                raise ValueError(
                    "Windows must have increasing start times"
                )

            if not math.isclose(
                threshold,
                previous["threshold"],
                rel_tol=0,
                abs_tol=1e-9,
            ):
                raise ValueError("Mixed thresholds in one dataset")

    comparisons = [
        compare_windows(windows[index], windows[index + offset])
        for index in range(max(0, len(windows) - offset))
    ]

    comparable = [
        pair for pair in comparisons
        if pair["pair_status"] == "COMPARABLE"
    ]

    def mean(key):
        if not comparable:
            return None

        return sum(
            pair[key] for pair in comparable
        ) / len(comparable)

    return {
        "offset": offset,
        "window_count": len(windows),
        "pair_count": len(comparisons),
        "comparable_pairs": len(comparable),
        "unavailable_pairs": (
            len(comparisons) - len(comparable)
        ),
        "mean_overlap_ratio": (
            sum(
                pair["overlap_ratio"]
                for pair in comparisons
            ) / len(comparisons)
            if comparisons else None
        ),
        "mean_low_difference": mean("low_share_difference"),
        "mean_high_difference": mean("high_share_difference"),
        "mean_unknown_difference": mean("unknown_share_difference"),
        "mean_state_difference": mean("mean_state_difference"),
        "comparisons": comparisons,
    }
