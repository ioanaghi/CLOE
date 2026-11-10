
import pytest

from backend.processing.window_features import extract_window_features


def test_single_window():
    timestamps = [0, 16667, 33334, 50001]
    sources = ["BOTH", "NONE", "LEFT", "NONE"]

    result = extract_window_features(timestamps, sources)

    first = result[0]

    assert first["sample_count"] == 4
    assert first["gaze_availability_rate"] == pytest.approx(0.5)
    assert first["binocular_availability_rate"] == pytest.approx(0.25)
    assert first["invalid_sample_count"] == 2
    assert first["longest_invalid_run"] == 1
    assert first["temporal_gap_count"] == 0


def test_overlapping_windows():
    timestamps = [
        0, 250000, 500000,
        750000, 1000000, 1250000
    ]
    sources = [
        "BOTH", "NONE", "LEFT",
        "NONE", "BOTH", "NONE"
    ]

    result = extract_window_features(
        timestamps,
        sources,
        window_us=1_000_000,
        step_us=500_000
    )

    assert len(result) == 3

    assert result[0]["sample_count"] == 4
    assert result[1]["sample_count"] == 4
    assert result[2]["sample_count"] == 2

    assert result[0]["start_s"] == 0.0
    assert result[1]["start_s"] == 0.5
    assert result[2]["start_s"] == 1.0


def test_consecutive_invalid_samples():
    timestamps = [0, 16667, 33334, 50001]
    sources = ["BOTH", "NONE", "NONE", "LEFT"]

    result = extract_window_features(timestamps, sources)

    assert result[0]["longest_invalid_run"] == 2


def test_temporal_gap():
    timestamps = [0, 16667, 50000, 66667]
    sources = ["BOTH"] * 4

    result = extract_window_features(timestamps, sources)

    assert result[0]["temporal_gap_count"] == 1


def test_empty_input():
    assert extract_window_features([], []) == []


def test_mismatched_lengths():
    with pytest.raises(ValueError):
        extract_window_features([0, 16667], ["BOTH"])


def test_out_of_order_timestamps():
    with pytest.raises(ValueError):
        extract_window_features(
            [0, 33334, 16667],
            ["BOTH", "BOTH", "BOTH"]
        )


def test_invalid_window_size():
    with pytest.raises(ValueError):
        extract_window_features(
            [0], ["BOTH"], window_us=0
        )


def test_invalid_source():
    with pytest.raises(ValueError):
        extract_window_features([0], ["UNKNOWN"])


def test_single_sample():
    result = extract_window_features([500000], ["NONE"])

    assert len(result) == 1
    assert result[0]["sample_count"] == 1
    assert result[0]["gaze_availability_rate"] == 0.0
    assert result[0]["longest_invalid_run"] == 1


def test_empty_window_keeps_unknown_rates():
    result = extract_window_features(
        [0, 3_000_000],
        ["BOTH", "BOTH"],
        window_us=1_000_000,
        step_us=1_000_000
    )

    assert result[1]["sample_count"] == 0
    assert result[1]["gaze_availability_rate"] is None
    assert result[1]["binocular_availability_rate"] is None
