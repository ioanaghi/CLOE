
import pytest

from backend.processing.window_oculomotor import (
    extract_window_oculomotor_features,
)


def make_data():
    # Five samples, four consecutive 0.25-second intervals.
    timestamps = [
        1_000_000,
        1_250_000,
        1_500_000,
        1_750_000,
        2_000_000,
    ]

    velocities = [
        {"velocity": 2.0, "reason": None},
        {"velocity": 3.0, "reason": None},
        {"velocity": 12.0, "reason": None},
        {"velocity": 1.0, "reason": None},
    ]

    return timestamps, velocities


def evaluate(
    start=0.0,
    end=1.0,
    status="ELIGIBLE",
    threshold=5.0,
):
    timestamps, velocities = make_data()

    return extract_window_oculomotor_features(
        timestamps,
        velocities,
        start,
        end,
        threshold,
        status,
    )


def test_full_window():
    result = evaluate()

    assert result["feature_status"] == "AVAILABLE"
    assert result["selected_interval_count"] == 4
    assert result["features"]["total_intervals"] == 4
    assert result["features"]["segment_count"] == 3


def test_partial_window_interval_alignment():
    result = evaluate(start=0.25, end=0.75)

    assert result["feature_status"] == "AVAILABLE"
    assert result["selected_interval_count"] == 2

    counts = result["features"]["interval_count_by_state"]
    assert counts["LOW_VELOCITY"] == 1
    assert counts["HIGH_VELOCITY"] == 1


def test_boundary_crossing_intervals_excluded():
    result = evaluate(start=0.10, end=0.90)

    # Intervals [0.25, 0.50] and [0.50, 0.75] only.
    assert result["selected_interval_count"] == 2


def test_quality_gate_unknown():
    result = evaluate(status="UNKNOWN")

    assert result["feature_status"] == "UNAVAILABLE"
    assert result["feature_reason"] == "QUALITY_GATE_UNKNOWN"
    assert result["features"] is None


def test_no_contained_intervals():
    result = evaluate(start=0.10, end=0.20)

    assert result["feature_status"] == "UNAVAILABLE"
    assert result["feature_reason"] == "NO_CONTAINED_INTERVALS"
    assert result["features"] is None


def test_unknown_velocity_preserved():
    timestamps, velocities = make_data()
    velocities[1] = {
        "velocity": None,
        "reason": "INVALID_GAZE_POINT",
    }

    result = extract_window_oculomotor_features(
        timestamps, velocities,
        0.0, 1.0, 5.0, "ELIGIBLE",
    )

    counts = result["features"]["interval_count_by_state"]
    assert counts["UNKNOWN"] == 1


def test_invalid_quality_status():
    with pytest.raises(ValueError):
        evaluate(status="INVALID")


def test_invalid_window_boundaries():
    with pytest.raises(ValueError):
        evaluate(start=1.0, end=0.5)


def test_mismatched_velocity_count():
    timestamps, velocities = make_data()

    with pytest.raises(ValueError):
        extract_window_oculomotor_features(
            timestamps,
            velocities[:2],
            0.0,
            1.0,
            5.0,
            "ELIGIBLE",
        )


def test_duplicate_timestamps():
    timestamps, velocities = make_data()
    timestamps[2] = timestamps[1]

    with pytest.raises(ValueError):
        extract_window_oculomotor_features(
            timestamps,
            velocities,
            0.0,
            1.0,
            5.0,
            "ELIGIBLE",
        )


def test_unknown_result_does_not_expose_features():
    result = evaluate(
        start=0.25,
        end=0.75,
        status="UNKNOWN",
    )

    assert result["selected_interval_count"] == 2
    assert result["features"] is None


def test_threshold_changes_classification():
    low_threshold = evaluate(threshold=2.5)
    high_threshold = evaluate(threshold=15.0)

    low_counts = low_threshold["features"]["interval_count_by_state"]
    high_counts = high_threshold["features"]["interval_count_by_state"]

    assert low_counts["HIGH_VELOCITY"] > high_counts["HIGH_VELOCITY"]


def test_empty_recording():
    result = extract_window_oculomotor_features(
        [], [],
        0.0, 1.0, 5.0, "ELIGIBLE",
    )

    assert result["feature_status"] == "UNAVAILABLE"
    assert result["feature_reason"] == "NO_CONTAINED_INTERVALS"
    assert result["features"] is None
