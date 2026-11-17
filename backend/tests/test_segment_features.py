
import pytest

from backend.processing.segment_features import (
    calculate_segment_durations,
)


def segment(state, start, end):
    return {
        "state": state,
        "start_interval_index": start,
        "end_interval_index": end,
        "interval_count": end - start + 1,
    }


def test_single_interval_duration():
    result = calculate_segment_durations(
        [segment("LOW_VELOCITY", 0, 0)],
        [0, 16667],
    )

    assert result[0]["duration_ms"] == pytest.approx(16.667)


def test_multiple_interval_duration():
    result = calculate_segment_durations(
        [segment("LOW_VELOCITY", 1, 2)],
        [0, 16667, 33334, 50001],
    )

    assert result[0]["duration_ms"] == pytest.approx(33.334)
    assert result[0]["start_timestamp_us"] == 16667
    assert result[0]["end_timestamp_us"] == 50001


def test_irregular_timestamps():
    result = calculate_segment_durations(
        [segment("HIGH_VELOCITY", 0, 1)],
        [0, 16667, 50000],
    )

    assert result[0]["duration_ms"] == pytest.approx(50.0)


def test_unknown_segment_has_observed_span():
    result = calculate_segment_durations(
        [segment("UNKNOWN", 0, 1)],
        [0, 20000, 40000],
    )

    assert result[0]["duration_ms"] == pytest.approx(40.0)


def test_multiple_segments():
    segments = [
        segment("LOW_VELOCITY", 0, 1),
        segment("HIGH_VELOCITY", 2, 2),
    ]

    result = calculate_segment_durations(
        segments,
        [0, 10000, 20000, 35000],
    )

    assert len(result) == 2
    assert result[0]["duration_ms"] == pytest.approx(20.0)
    assert result[1]["duration_ms"] == pytest.approx(15.0)


def test_empty_input():
    assert calculate_segment_durations([], []) == []


def test_segment_without_timestamps():
    with pytest.raises(ValueError):
        calculate_segment_durations(
            [segment("LOW_VELOCITY", 0, 0)],
            [],
        )


def test_out_of_order_timestamps():
    with pytest.raises(ValueError):
        calculate_segment_durations(
            [segment("LOW_VELOCITY", 0, 0)],
            [20000, 10000],
        )


def test_out_of_bounds_segment():
    with pytest.raises(ValueError):
        calculate_segment_durations(
            [segment("LOW_VELOCITY", 0, 2)],
            [0, 16667, 33334],
        )


def test_inconsistent_interval_count():
    invalid = segment("LOW_VELOCITY", 0, 1)
    invalid["interval_count"] = 5

    with pytest.raises(ValueError):
        calculate_segment_durations(
            [invalid],
            [0, 16667, 33334],
        )


def test_unknown_state_rejected():
    with pytest.raises(ValueError):
        calculate_segment_durations(
            [segment("FIXATION", 0, 0)],
            [0, 16667],
        )


def test_input_segment_not_modified():
    original = segment("LOW_VELOCITY", 0, 0)

    calculate_segment_durations([original], [0, 16667])

    assert "duration_ms" not in original
