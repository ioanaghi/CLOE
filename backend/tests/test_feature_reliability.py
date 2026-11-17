
from copy import deepcopy

import pytest

from backend.processing.feature_reliability import (
    analyze_threshold_sensitivity,
    state_shares,
)


def make_window(threshold, low, high, unknown=1):
    total = low + high + unknown

    return {
        "start_s": 0.0,
        "end_s": 1.0,
        "threshold": threshold,
        "quality_gate_status": "ELIGIBLE",
        "feature_status": "AVAILABLE",
        "selected_interval_count": total,
        "features": {
            "total_intervals": total,
            "interval_count_by_state": {
                "LOW_VELOCITY": low,
                "HIGH_VELOCITY": high,
                "UNKNOWN": unknown,
            },
        },
    }


def make_unknown_window(threshold):
    return {
        "start_s": 0.5,
        "end_s": 1.5,
        "threshold": threshold,
        "quality_gate_status": "UNKNOWN",
        "feature_status": "UNAVAILABLE",
        "selected_interval_count": 8,
        "features": None,
    }


def example_datasets():
    return {
        2.0: [
            make_window(2.0, 6, 3),
            make_unknown_window(2.0),
        ],
        5.0: [
            make_window(5.0, 8, 1),
            make_unknown_window(5.0),
        ],
        10.0: [
            make_window(10.0, 9, 0),
            make_unknown_window(10.0),
        ],
    }


def test_state_shares():
    window = make_window(2.0, 6, 3)

    shares = state_shares(window)

    assert shares["LOW_VELOCITY"] == pytest.approx(0.6)
    assert shares["HIGH_VELOCITY"] == pytest.approx(0.3)
    assert shares["UNKNOWN"] == pytest.approx(0.1)


def test_unavailable_window_has_no_shares():
    assert state_shares(make_unknown_window(2.0)) is None


def test_availability_rate():
    result = analyze_threshold_sensitivity(
        example_datasets()
    )

    assert result["window_count"] == 2
    assert result["available_count"] == 1
    assert result["unavailable_count"] == 1
    assert result["availability_rate"] == pytest.approx(0.5)


def test_low_share_range():
    result = analyze_threshold_sensitivity(
        example_datasets()
    )

    assert result["mean_low_share_range"] == pytest.approx(0.3)


def test_high_share_range():
    result = analyze_threshold_sensitivity(
        example_datasets()
    )

    assert result["mean_high_share_range"] == pytest.approx(0.3)


def test_unknown_share_preserved():
    result = analyze_threshold_sensitivity(
        example_datasets()
    )

    assert result["mean_unknown_share"] == pytest.approx(0.1)


def test_unavailable_window_not_analyzed():
    result = analyze_threshold_sensitivity(
        example_datasets()
    )

    row = result["per_window"][1]

    assert row["feature_status"] == "UNAVAILABLE"
    assert row["low_share_range"] is None
    assert row["high_share_range"] is None


def test_changed_quality_status_rejected():
    data = example_datasets()
    data[5.0][1]["quality_gate_status"] = "ELIGIBLE"

    with pytest.raises(ValueError, match="cross-threshold"):
        analyze_threshold_sensitivity(data)


def test_changed_unknown_share_rejected():
    data = example_datasets()

    data[10.0][0]["features"][
        "interval_count_by_state"
    ] = {
        "LOW_VELOCITY": 8,
        "HIGH_VELOCITY": 0,
        "UNKNOWN": 2,
    }

    with pytest.raises(ValueError, match="UNKNOWN"):
        analyze_threshold_sensitivity(data)


def test_input_not_modified():
    data = example_datasets()
    original = deepcopy(data)

    analyze_threshold_sensitivity(data)

    assert data == original
