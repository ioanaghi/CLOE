
import pytest

from backend.processing.temporal_processing import analyze_timestamps


def test_regular_intervals():
    timestamps = [0, 16667, 33334, 50001]

    result = analyze_timestamps(timestamps)

    assert result["non_positive_intervals"] == 0
    assert result["large_gaps"] == []
    assert result["estimated_missing_samples"] == 0


def test_one_missing_sample():
    timestamps = [0, 16667, 50000]

    result = analyze_timestamps(timestamps)

    assert len(result["large_gaps"]) == 1
    assert result["estimated_missing_samples"] == 1


def test_two_missing_samples():
    timestamps = [0, 50000]

    result = analyze_timestamps(timestamps)

    assert result["estimated_missing_samples"] == 2


def test_duplicate_timestamp():
    timestamps = [0, 16667, 16667, 33334]

    result = analyze_timestamps(timestamps)

    assert result["non_positive_intervals"] == 1


def test_out_of_order_timestamps():
    timestamps = [0, 33334, 16667]

    result = analyze_timestamps(timestamps)

    assert result["non_positive_intervals"] == 1


def test_empty_input():
    result = analyze_timestamps([])

    assert result["intervals_us"] == []
    assert result["estimated_missing_samples"] == 0


def test_invalid_frequency():
    with pytest.raises(ValueError):
        analyze_timestamps([0, 16667], nominal_hz=0)
