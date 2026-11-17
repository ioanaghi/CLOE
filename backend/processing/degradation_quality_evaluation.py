
import math

from backend.processing.window_features import (
    extract_window_features,
)
from backend.processing.data_quality import (
    assess_window_quality,
)
from backend.processing.quality_gate import (
    evaluate_quality,
    validate_policy,
)


VALID_SOURCES = {"BOTH", "LEFT", "RIGHT", "NONE"}



def evaluate_degraded_windows(
    timestamps,
    sources,
    reference_windows,
    recording_duration_s,
    policy,
    nominal_hz=60,
    reference_start_timestamp=None,
):

    """
    Recompute M0.3 quality decisions after degradation.

    The original window boundaries are authoritative.

    This function intentionally does NOT reuse saved
    Quality Gate decisions.
    """
    validate_policy(policy)

    if len(timestamps) != len(sources):
        raise ValueError("Timestamp/source count mismatch")

    if not reference_windows:
        raise ValueError("Reference windows are required")

    if not math.isfinite(recording_duration_s):
        raise ValueError("Invalid recording duration")

    if recording_duration_s <= 0:
        raise ValueError("Recording duration must be positive")

    if not timestamps:
        raise ValueError("Empty scenario timestamps")

    if any(source not in VALID_SOURCES for source in sources):
        raise ValueError("Unknown gaze source")

    if any(
        timestamps[i] <= timestamps[i - 1]
        for i in range(1, len(timestamps))
    ):
        raise ValueError("Timestamps must be strictly increasing")


    
    if reference_start_timestamp is not None:
        if (
            isinstance(reference_start_timestamp, bool)
            or not isinstance(reference_start_timestamp, int)
        ):
            raise ValueError(
                "Reference start timestamp must be an integer"
            )

        if timestamps[0] != reference_start_timestamp:
            raise ValueError(
                "Temporal alignment changed: "
                "first timestamp differs from reference"
            )


    # Existing M0.3 feature extraction.
    windows = extract_window_features(
        timestamps,
        sources,
        window_us=1_000_000,
        step_us=500_000,
        nominal_hz=nominal_hz,
    )

    if len(windows) != len(reference_windows):
        raise ValueError(
            "Degradation changed the window count"
        )

    results = []

    for index, (window, reference) in enumerate(
        zip(windows, reference_windows)
    ):
        if not (
            math.isclose(
                window["start_s"],
                reference["start_s"],
                rel_tol=0,
                abs_tol=1e-6,
            )
            and math.isclose(
                window["end_s"],
                reference["end_s"],
                rel_tol=0,
                abs_tol=1e-6,
            )
        ):
            raise ValueError(
                f"Window alignment changed at index {index}"
            )

        # Recalculate quality using the degraded data.
        quality = assess_window_quality(
            window,
            nominal_hz=nominal_hz,
        )

        # Use the ORIGINAL recording coverage, not a
        # degradation-dependent or scenario-relative end.
        #
        # This matches the observed-bounds proxy used in M0.3.
        window_complete = (
            window["end_s"]
            <= recording_duration_s + 1e-9
        )

        decision = evaluate_quality(
            quality,
            policy,
            window_complete=window_complete,
        )

        results.append({
            "start_s": window["start_s"],
            "end_s": window["end_s"],
            "sample_count": window["sample_count"],
            "invalid_sample_count": (
                window["invalid_sample_count"]
            ),
            "gaze_availability_rate": (
                quality["gaze_availability_rate"]
            ),
            "nominal_sample_ratio": (
                quality["nominal_sample_ratio"]
            ),
            "usable_nominal_ratio": (
                quality["usable_nominal_ratio"]
            ),
            "window_complete": window_complete,
            "status": decision["status"],
            "reasons": decision["reasons"],
        })

    return results


def compare_quality_decisions(baseline, degraded):
    """
    Compare recalculated Quality Gate outcomes.

    Report newly rejected and recovered windows separately.
    """
    if len(baseline) != len(degraded):
        raise ValueError("Window counts differ")

    newly_rejected = []
    recovered = []

    for original, current in zip(baseline, degraded):
        if (
            original["start_s"] != current["start_s"]
            or original["end_s"] != current["end_s"]
        ):
            raise ValueError("Window boundaries differ")

        if (
            original["status"] == "ELIGIBLE"
            and current["status"] == "UNKNOWN"
        ):
            newly_rejected.append({
                "start_s": current["start_s"],
                "end_s": current["end_s"],
                "reasons": current["reasons"],
            })

        elif (
            original["status"] == "UNKNOWN"
            and current["status"] == "ELIGIBLE"
        ):
            recovered.append({
                "start_s": current["start_s"],
                "end_s": current["end_s"],
            })

    return {
        "newly_rejected": newly_rejected,
        "recovered": recovered,
    }
