
from copy import deepcopy

import pytest

from backend.processing.data_degradation import (
    simulate_invalid_gaze,
    simulate_sample_dropout,
    calculate_degradation_metrics,
)


def make_data():
    timestamps = [
        0,
        16667,
        33334,
        50001,
        66668,
    ]

    velocities = [
        {"velocity": 1.0, "reason": None},
        {"velocity": 2.0, "reason": None},
        {"velocity": 3.0, "reason": None},
        {"velocity": 4.0, "reason": None},
    ]

    return timestamps, velocities


def test_baseline_metrics():
    timestamps, velocities = make_data()

    result = calculate_degradation_metrics(
        timestamps, velocities
    )

    assert result["sample_count"] == 5
    assert result["interval_count"] == 4
    assert result["available_velocity_count"] == 4
    assert result["unknown_velocity_count"] == 0
    assert result["velocity_availability_rate"] == 1.0
    assert result["large_temporal_gap_count"] == 0


def test_invalid_gaze_preserves_samples():
    timestamps, velocities = make_data()

    result = simulate_invalid_gaze(
        timestamps, velocities, [2]
    )

    assert result["timestamps"] == timestamps
    assert result["sample_count"] == 5
    assert len(result["velocity_results"]) == 4


def test_invalid_gaze_masks_adjacent_intervals():
    timestamps, velocities = make_data()

    result = simulate_invalid_gaze(
        timestamps, velocities, [2]
    )

    values = [
        item["velocity"]
        for item in result["velocity_results"]
    ]

    assert values == [1.0, None, None, 4.0]


def test_invalid_gaze_at_first_sample():
    timestamps, velocities = make_data()

    result = simulate_invalid_gaze(
        timestamps, velocities, [0]
    )

    values = [
        item["velocity"]
        for item in result["velocity_results"]
    ]

    assert values == [None, 2.0, 3.0, 4.0]


def test_invalid_gaze_consecutive_samples():
    timestamps, velocities = make_data()

    result = simulate_invalid_gaze(
        timestamps, velocities, [1, 2]
    )

    values = [
        item["velocity"]
        for item in result["velocity_results"]
    ]

    assert values == [None, None, None, 4.0]


def test_dropout_removes_sample():
    timestamps, velocities = make_data()

    result = simulate_sample_dropout(
        timestamps, velocities, [2]
    )

    assert result["timestamps"] == [
        0, 16667, 50001, 66668
    ]
    assert result["sample_count"] == 4


def test_dropout_bridge_is_unknown():
    timestamps, velocities = make_data()

    result = simulate_sample_dropout(
        timestamps, velocities, [2]
    )

    values = [
        item["velocity"]
        for item in result["velocity_results"]
    ]

    assert values == [1.0, None, 4.0]

    assert (
        result["velocity_results"][1]["reason"]
        == "SIMULATED_DROPPED_SAMPLE_BRIDGE"
    )


def test_dropout_creates_temporal_gap():
    timestamps, velocities = make_data()

    degraded = simulate_sample_dropout(
        timestamps, velocities, [2]
    )

    metrics = calculate_degradation_metrics(
        degraded["timestamps"],
        degraded["velocity_results"],
    )

    assert metrics["large_temporal_gap_count"] == 1
    assert metrics["unknown_velocity_count"] == 1


def test_invalid_gaze_does_not_create_gap():
    timestamps, velocities = make_data()

    degraded = simulate_invalid_gaze(
        timestamps, velocities, [2]
    )

    metrics = calculate_degradation_metrics(
        degraded["timestamps"],
        degraded["velocity_results"],
    )

    assert metrics["large_temporal_gap_count"] == 0
    assert metrics["unknown_velocity_count"] == 2


def test_multiple_dropouts():
    timestamps, velocities = make_data()

    degraded = simulate_sample_dropout(
        timestamps, velocities, [1, 2]
    )

    assert degraded["timestamps"] == [
        0, 50001, 66668
    ]

    assert len(degraded["velocity_results"]) == 2
    assert degraded["velocity_results"][0]["velocity"] is None
    assert degraded["velocity_results"][1]["velocity"] == 4.0


def test_invalid_index_rejected():
    timestamps, velocities = make_data()

    with pytest.raises(ValueError):
        simulate_invalid_gaze(
            timestamps, velocities, [20]
        )


def test_duplicate_indices_rejected():
    timestamps, velocities = make_data()

    with pytest.raises(ValueError):
        simulate_sample_dropout(
            timestamps, velocities, [2, 2]
        )


def test_mismatched_interval_count_rejected():
    timestamps, velocities = make_data()

    with pytest.raises(ValueError):
        simulate_invalid_gaze(
            timestamps, velocities[:2], [1]
        )


def test_input_not_modified():
    timestamps, velocities = make_data()

    original_timestamps = deepcopy(timestamps)
    original_velocities = deepcopy(velocities)

    simulate_invalid_gaze(
        timestamps, velocities, [2]
    )

    simulate_sample_dropout(
        timestamps, velocities, [2]
    )

    assert timestamps == original_timestamps
    assert velocities == original_velocities


def test_empty_input():
    result = calculate_degradation_metrics([], [])

    assert result["sample_count"] == 0
    assert result["interval_count"] == 0
    assert result["velocity_availability_rate"] is None
