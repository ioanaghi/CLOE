
from copy import deepcopy

import pytest

from backend.processing.movement_summary import (
    summarize_movement_segments,
)


def segment(state, start, end, duration_ms):
    return {
        "state": state,
        "start_interval_index": start,
        "end_interval_index": end,
        "interval_count": end - start + 1,
        "duration_ms": duration_ms,
    }


def example_segments():
    return [
        segment("LOW_VELOCITY", 0, 2, 30.0),
        segment("HIGH_VELOCITY", 3, 4, 20.0),
        segment("UNKNOWN", 5, 5, 10.0),
        segment("LOW_VELOCITY", 6, 7, 20.0),
    ]


def test_total_segment_count():
    result = summarize_movement_segments(
        example_segments(), 8
    )

    assert result["segment_count"] == 4
    assert result["total_intervals"] == 8


def test_interval_distribution():
    result = summarize_movement_segments(
        example_segments(), 8
    )

    counts = result["interval_count_by_state"]
    shares = result["interval_share_by_state"]

    assert counts["LOW_VELOCITY"] == 5
    assert counts["HIGH_VELOCITY"] == 2
    assert counts["UNKNOWN"] == 1

    assert shares["LOW_VELOCITY"] == pytest.approx(5 / 8)
    assert shares["HIGH_VELOCITY"] == pytest.approx(2 / 8)
    assert shares["UNKNOWN"] == pytest.approx(1 / 8)


def test_segment_duration_statistics():
    result = summarize_movement_segments(
        example_segments(), 8
    )

    totals = result["total_duration_ms_by_state"]
    means = result["mean_duration_ms_by_state"]
    maxima = result["max_duration_ms_by_state"]

    assert totals["LOW_VELOCITY"] == pytest.approx(50.0)
    assert means["LOW_VELOCITY"] == pytest.approx(25.0)
    assert maxima["LOW_VELOCITY"] == pytest.approx(30.0)
    assert totals["UNKNOWN"] == pytest.approx(10.0)


def test_transition_counts():
    result = summarize_movement_segments(
        example_segments(), 8
    )

    assert result["transition_count"] == 3
    assert result["direct_low_high_transitions"] == 1


def test_internal_unknown_run():
    result = summarize_movement_segments(
        example_segments(), 8
    )

    assert result["internal_unknown_runs"] == 1


def test_empty_recording():
    result = summarize_movement_segments([], 0)

    assert result["segment_count"] == 0
    assert result["transition_count"] == 0
    assert result["interval_share_by_state"]["UNKNOWN"] is None
    assert result["mean_duration_ms_by_state"]["UNKNOWN"] is None


def test_nonempty_recording_without_segments():
    with pytest.raises(ValueError):
        summarize_movement_segments([], 5)


def test_missing_final_interval():
    with pytest.raises(ValueError):
        summarize_movement_segments(
            [segment("LOW_VELOCITY", 0, 2, 30.0)],
            4,
        )


def test_gap_between_segments():
    segments = [
        segment("LOW_VELOCITY", 0, 1, 20.0),
        segment("HIGH_VELOCITY", 3, 3, 10.0),
    ]

    with pytest.raises(ValueError):
        summarize_movement_segments(segments, 4)


def test_overlapping_segments():
    segments = [
        segment("LOW_VELOCITY", 0, 2, 30.0),
        segment("HIGH_VELOCITY", 2, 3, 20.0),
    ]

    with pytest.raises(ValueError):
        summarize_movement_segments(segments, 4)


def test_adjacent_duplicate_states():
    segments = [
        segment("LOW_VELOCITY", 0, 1, 20.0),
        segment("LOW_VELOCITY", 2, 3, 20.0),
    ]

    with pytest.raises(ValueError):
        summarize_movement_segments(segments, 4)


def test_inconsistent_interval_count():
    segments = example_segments()
    segments[0]["interval_count"] = 5

    with pytest.raises(ValueError):
        summarize_movement_segments(segments, 8)


def test_invalid_duration():
    segments = example_segments()
    segments[0]["duration_ms"] = float("nan")

    with pytest.raises(ValueError):
        summarize_movement_segments(segments, 8)


def test_invalid_state():
    segments = example_segments()
    segments[0]["state"] = "FIXATION"

    with pytest.raises(ValueError):
        summarize_movement_segments(segments, 8)


def test_invalid_total_intervals():
    with pytest.raises(ValueError):
        summarize_movement_segments([], -1)


def test_input_is_not_modified():
    original = example_segments()
    before = deepcopy(original)

    summarize_movement_segments(original, 8)

    assert original == before
