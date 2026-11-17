
from copy import deepcopy

import pytest

from backend.processing.temporal_feature_stability import (
    calculate_overlap,
    compare_windows,
    analyze_temporal_stability,
)


def window(start, low, high, unknown=0, available=True):
    total = low + high + unknown

    return {
        "start_s": start,
        "end_s": start + 1.0,
        "threshold": 5.0,
        "quality_gate_status": (
            "ELIGIBLE" if available else "UNKNOWN"
        ),
        "feature_status": (
            "AVAILABLE" if available else "UNAVAILABLE"
        ),
        "selected_interval_count": total,
        "features": (
            {
                "total_intervals": total,
                "interval_count_by_state": {
                    "LOW_VELOCITY": low,
                    "HIGH_VELOCITY": high,
                    "UNKNOWN": unknown,
                },
            }
            if available else None
        ),
    }


def dataset():
    return [
        window(0.0, 8, 2),
        window(0.5, 7, 3),
        window(1.0, 6, 4),
        window(1.5, 0, 0, available=False),
    ]


def test_half_window_overlap():
    result = calculate_overlap(dataset()[0], dataset()[1])

    assert result["overlap_duration_s"] == pytest.approx(0.5)
    assert result["overlap_ratio"] == pytest.approx(0.5)


def test_no_overlap():
    result = calculate_overlap(dataset()[0], dataset()[2])

    assert result["overlap_duration_s"] == 0.0
    assert result["overlap_ratio"] == 0.0


def test_identical_state_distribution():
    first = window(0.0, 8, 2)
    second = window(0.5, 8, 2)

    result = compare_windows(first, second)

    assert result["pair_status"] == "COMPARABLE"
    assert result["mean_state_difference"] == 0.0


def test_state_difference():
    result = compare_windows(dataset()[0], dataset()[1])

    assert result["low_share_difference"] == pytest.approx(0.1)
    assert result["high_share_difference"] == pytest.approx(0.1)
    assert result["unknown_share_difference"] == 0.0
    assert result["mean_state_difference"] == pytest.approx(2 / 30)


def test_unavailable_pair():
    result = compare_windows(dataset()[2], dataset()[3])

    assert result["pair_status"] == "UNAVAILABLE"
    assert result["mean_state_difference"] is None


def test_consecutive_pairs():
    result = analyze_temporal_stability(dataset(), offset=1)

    assert result["pair_count"] == 3
    assert result["comparable_pairs"] == 2
    assert result["unavailable_pairs"] == 1
    assert result["mean_overlap_ratio"] == pytest.approx(0.5)


def test_nonoverlapping_pairs():
    result = analyze_temporal_stability(dataset(), offset=2)

    assert result["pair_count"] == 2
    assert result["comparable_pairs"] == 1
    assert result["unavailable_pairs"] == 1
    assert result["mean_overlap_ratio"] == 0.0


def test_empty_input():
    result = analyze_temporal_stability([])

    assert result["pair_count"] == 0
    assert result["comparable_pairs"] == 0
    assert result["mean_state_difference"] is None


def test_mixed_thresholds_rejected():
    rows = dataset()
    rows[1]["threshold"] = 10.0

    with pytest.raises(ValueError, match="Mixed thresholds"):
        analyze_temporal_stability(rows)


def test_unordered_windows_rejected():
    rows = dataset()
    rows[1]["start_s"] = -0.5

    with pytest.raises(ValueError):
        analyze_temporal_stability(rows)


def test_invalid_offset_rejected():
    with pytest.raises(ValueError):
        analyze_temporal_stability(dataset(), offset=0)


def test_input_not_modified():
    rows = dataset()
    original = deepcopy(rows)

    analyze_temporal_stability(rows)

    assert rows == original
