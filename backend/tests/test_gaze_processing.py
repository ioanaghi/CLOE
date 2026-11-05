from pathlib import Path
import sys
import pytest



PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.processing.gaze_processing import is_valid_eye, combine_gaze

def test_valid_point():
    point = (0.5, 0.5)
    validity = 1
    assert is_valid_eye(point, validity) is True

def test_invalid_flag():
    point = (0.5, 0.5)
    validity = 0
    assert is_valid_eye(point, validity) is False

def test_nan_coordinates():
    point = (float('nan'), 0.5)
    validity = 1
    assert is_valid_eye(point, validity) is False

def test_infinite_coordinates():
    point = (float('inf'), 0.5)
    validity = 1
    assert is_valid_eye(point, validity) is False

def test_point_outside_screen():
    point = (1.05, 0.5)  # Assuming the screen coordinates are normalized between 0 and 1
    validity = 1
    assert is_valid_eye(point, validity) is True


def is_inside_screen(point):
    x, y = point
    return 0 <= x <= 1 and 0 <= y <= 1


def test_wrong_dimension():
    assert is_valid_eye((0.5, 0.5, 0.5), 1) is False 


def test_both_eyes_valid():
    point, source = combine_gaze(
        (0.5, 0.40), (0.52, 0.42), 1, 1
    )

    assert point == pytest.approx((0.51, 0.41))
    assert source == "BOTH"

def test_only_left_eye_valid():
    point, source = combine_gaze(
        (0.5, 0.40), (float('nan'), float('nan')), 1, 0
    )

    assert point == pytest.approx((0.5, 0.40))
    assert source == "LEFT"

def test_only_right_eye_valid():
    point, source = combine_gaze(
        (float('nan'), float('nan')), (0.52, 0.42), 0, 1
    )

    assert point == pytest.approx((0.52, 0.42))
    assert source == "RIGHT"

def test_no_valid_eyes():
    point, source = combine_gaze(
        (float('nan'), float('nan')), 
        (float('nan'), float('nan')), 0, 0
    )

    assert point is None
    assert source == "NONE"

