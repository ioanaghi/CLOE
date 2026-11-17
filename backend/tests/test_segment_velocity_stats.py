
import pytest

from backend.processing.segment_features import (
    calculate_segment_velocity_stats,
)


def make_segment(state, start, end):
    return {
        "state": state,
        "start_interval_index": start,
        "end_interval_index": end,
        "interval_count": end - start + 1,
    }


def make_velocities(values):
    return [{"velocity": value} for value in values]


def test_mean_velocity():
    result = calculate_segment_velocity_stats(
        [make_segment("LOW_VELOCITY", 0, 3)],
        make_velocities([2.0, 4.0, 6.0, 8.0]),
    )

    assert result[0]["mean_velocity"] == pytest.approx(5.0)


def test_min_max_velocity():
    result = calculate_segment_velocity_stats(
        [make_segment("HIGH_VELOCITY", 0, 2)],
        make_velocities([12.0, 20.0, 15.0]),
    )

    assert result[0]["min_velocity"] == 12.0
    assert result[0]["max_velocity"] == 20.0


def test_standard_deviation():
    result = calculate_segment_velocity_stats(
        [make_segment("LOW_VELOCITY", 0, 3)],
        make_velocities([2.0, 4.0, 6.0, 8.0]),
    )

    assert result[0]["std_velocity"] == pytest.approx(
        5 ** 0.5
    )


def test_single_interval():
    result = calculate_segment_velocity_stats(
        [make_segment("LOW_VELOCITY", 0, 0)],
        make_velocities([3.5]),
    )

    assert result[0]["mean_velocity"] == 3.5
    assert result[0]["std_velocity"] == 0.0
    assert result[0]["valid_velocity_count"] == 1


def test_unknown_segment():
    result = calculate_segment_velocity_stats(
        [make_segment("UNKNOWN", 0, 1)],
        make_velocities([None, None]),
    )

    assert result[0]["valid_velocity_count"] == 0
    assert result[0]["mean_velocity"] is None
    assert result[0]["min_velocity"] is None
    assert result[0]["max_velocity"] is None
    assert result[0]["std_velocity"] is None


def test_multiple_segments():
    segments = [
        make_segment("LOW_VELOCITY", 0, 1),
        make_segment("UNKNOWN", 2, 2),
        make_segment("HIGH_VELOCITY", 3, 4),
    ]

    result = calculate_segment_velocity_stats(
        segments,
        make_velocities([2.0, 4.0, None, 12.0, 18.0]),
    )

    assert len(result) == 3
    assert result[0]["mean_velocity"] == 3.0
    assert result[1]["mean_velocity"] is None
    assert result[2]["mean_velocity"] == 15.0


def test_empty_input():
    assert calculate_segment_velocity_stats([], []) == []


def test_invalid_velocity_in_valid_segment():
    with pytest.raises(ValueError):
        calculate_segment_velocity_stats(
            [make_segment("LOW_VELOCITY", 0, 1)],
            make_velocities([2.0, None]),
        )


def test_nan_velocity_rejected():
    with pytest.raises(ValueError):
        calculate_segment_velocity_stats(
            [make_segment("LOW_VELOCITY", 0, 0)],
            make_velocities([float("nan")]),
        )


def test_negative_velocity_rejected():
    with pytest.raises(ValueError):
        calculate_segment_velocity_stats(
            [make_segment("HIGH_VELOCITY", 0, 0)],
            make_velocities([-5.0]),
        )


def test_valid_velocity_in_unknown_segment():
    with pytest.raises(ValueError):
        calculate_segment_velocity_stats(
            [make_segment("UNKNOWN", 0, 0)],
            make_velocities([2.0]),
        )


def test_out_of_bounds_segment():
    with pytest.raises(ValueError):
        calculate_segment_velocity_stats(
            [make_segment("LOW_VELOCITY", 0, 3)],
            make_velocities([2.0, 3.0]),
        )


def test_inconsistent_interval_count():
    segment = make_segment("LOW_VELOCITY", 0, 1)
    segment["interval_count"] = 3

    with pytest.raises(ValueError):
        calculate_segment_velocity_stats(
            [segment],
            make_velocities([2.0, 3.0]),
        )


def test_input_not_modified():
    segment = make_segment("LOW_VELOCITY", 0, 0)
    velocities = make_velocities([2.0])

    result = calculate_segment_velocity_stats(
        [segment],
        velocities,
    )

    assert "mean_velocity" not in segment
    assert velocities == [{"velocity": 2.0}]
    assert result[0]["mean_velocity"] == 2.0


def test_duration_field_preserved():
    segment = make_segment("LOW_VELOCITY", 0, 0)
    segment["duration_ms"] = 16.667

    result = calculate_segment_velocity_stats(
        [segment],
        make_velocities([3.0]),
    )

    assert result[0]["duration_ms"] == pytest.approx(16.667)
    assert result[0]["mean_velocity"] == 3.0
