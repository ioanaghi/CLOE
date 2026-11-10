
import pytest

from backend.processing.recording_boundaries import (
    is_within_recording_bounds,
)


def test_window_inside_recording():
    assert is_within_recording_bounds(2.0, 3.0, 9.64) is True


def test_window_crosses_recording_end():
    assert is_within_recording_bounds(9.0, 10.0, 9.64) is False


def test_window_equals_recording_end():
    assert is_within_recording_bounds(8.0, 9.64, 9.64) is True


def test_zero_start_is_allowed():
    assert is_within_recording_bounds(0.0, 1.0, 9.64) is True


def test_negative_window_start():
    with pytest.raises(ValueError):
        is_within_recording_bounds(-0.5, 0.5, 9.64)


def test_invalid_window_duration():
    with pytest.raises(ValueError):
        is_within_recording_bounds(1.0, 1.0, 9.64)


def test_negative_recording_duration():
    with pytest.raises(ValueError):
        is_within_recording_bounds(0.0, 1.0, -1.0)


def test_non_finite_duration():
    with pytest.raises(ValueError):
        is_within_recording_bounds(
            0.0, 1.0, float("nan")
        )
