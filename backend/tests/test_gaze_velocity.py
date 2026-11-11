
import pytest

from backend.processing.gaze_velocity import (
    calculate_gaze_velocity,
)


def test_stationary_gaze():
    result = calculate_gaze_velocity(
        (0.5, 0.5), (0.5, 0.5),
        0, 16667
    )

    assert result["velocity"] == 0.0
    assert result["reason"] is None


def test_horizontal_movement():
    result = calculate_gaze_velocity(
        (0.2, 0.5), (0.3, 0.5),
        0, 20000
    )

    assert result["velocity"] == pytest.approx(5.0)


def test_diagonal_movement():
    result = calculate_gaze_velocity(
        (0.0, 0.0), (0.3, 0.4),
        0, 20000
    )

    assert result["velocity"] == pytest.approx(25.0)


def test_invalid_gaze_point():
    result = calculate_gaze_velocity(
        None, (0.5, 0.5),
        0, 16667
    )

    assert result["velocity"] is None
    assert result["reason"] == "INVALID_GAZE_POINT"


def test_nan_coordinates():
    result = calculate_gaze_velocity(
        (float("nan"), 0.5), (0.5, 0.5),
        0, 16667
    )

    assert result["reason"] == "INVALID_GAZE_POINT"


def test_temporal_gap():
    result = calculate_gaze_velocity(
        (0.2, 0.5), (0.3, 0.5),
        0, 50000
    )

    assert result["velocity"] is None
    assert result["reason"] == "TEMPORAL_GAP"


def test_duplicate_timestamp():
    result = calculate_gaze_velocity(
        (0.2, 0.5), (0.3, 0.5),
        16667, 16667
    )

    assert result["reason"] == "NON_POSITIVE_INTERVAL"


def test_invalid_nominal_frequency():
    with pytest.raises(ValueError):
        calculate_gaze_velocity(
            (0.2, 0.5), (0.3, 0.5),
            0, 16667,
            nominal_hz=0,
        )


def test_invalid_gap_ratio():
    with pytest.raises(ValueError):
        calculate_gaze_velocity(
            (0.2, 0.5), (0.3, 0.5),
            0, 16667,
            max_gap_ratio=0.5,
        )
