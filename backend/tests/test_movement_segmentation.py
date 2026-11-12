
import pytest

from backend.processing.movement_segmentation import (
    LOW,
    HIGH,
    UNKNOWN,
    classify_velocity,
    segment_velocity_states,
)


def make_results(velocities):
    return [
        {"velocity": value, "reason": None}
        for value in velocities
    ]


def test_low_velocity():
    assert classify_velocity(2.0, 10.0) == LOW


def test_high_velocity():
    assert classify_velocity(15.0, 10.0) == HIGH


def test_threshold_boundary():
    assert classify_velocity(10.0, 10.0) == HIGH


def test_unknown_velocity():
    assert classify_velocity(None, 10.0) == UNKNOWN


def test_nan_velocity():
    assert classify_velocity(float("nan"), 10.0) == UNKNOWN


def test_negative_velocity():
    with pytest.raises(ValueError):
        classify_velocity(-1.0, 10.0)


def test_invalid_threshold():
    with pytest.raises(ValueError):
        classify_velocity(5.0, 0.0)


def test_single_segment():
    segments = segment_velocity_states(
        make_results([2.0, 3.0, 1.0]),
        threshold=10.0,
    )

    assert segments == [{
        "state": LOW,
        "start_interval_index": 0,
        "end_interval_index": 2,
        "interval_count": 3,
    }]


def test_multiple_segments():
    segments = segment_velocity_states(
        make_results([
            2.0, 3.0, 1.0,
            12.0, 15.0,
            None,
            2.0, 3.0,
        ]),
        threshold=10.0,
    )

    assert [item["state"] for item in segments] == [
        LOW, HIGH, UNKNOWN, LOW
    ]

    assert [item["interval_count"] for item in segments] == [
        3, 2, 1, 2
    ]


def test_unknown_breaks_low_velocity_segment():
    segments = segment_velocity_states(
        make_results([2.0, None, 2.0]),
        threshold=10.0,
    )

    assert [item["state"] for item in segments] == [
        LOW, UNKNOWN, LOW
    ]


def test_empty_input():
    assert segment_velocity_states([], threshold=10.0) == []


def test_all_unknown():
    segments = segment_velocity_states(
        make_results([None, None]),
        threshold=10.0,
    )

    assert len(segments) == 1
    assert segments[0]["state"] == UNKNOWN
    assert segments[0]["interval_count"] == 2


def test_invalid_segment_threshold():
    with pytest.raises(ValueError):
        segment_velocity_states(
            make_results([2.0]),
            threshold=float("nan"),
        )
