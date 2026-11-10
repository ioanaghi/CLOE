
import pytest

from backend.processing.data_quality import assess_window_quality


def make_window(samples, invalid, duration=1.0):
    return {
        "start_s": 0.0,
        "end_s": duration,
        "sample_count": samples,
        "invalid_sample_count": invalid,
        "gaze_availability_rate": (
            (samples - invalid) / samples
            if samples else None
        ),
    }


def test_full_valid_window():
    result = assess_window_quality(make_window(60, 0))

    assert result["gaze_availability_rate"] == 1.0
    assert result["nominal_sample_ratio"] == pytest.approx(1.0)
    assert result["usable_nominal_ratio"] == pytest.approx(1.0)


def test_low_availability():
    result = assess_window_quality(make_window(58, 31))

    assert result["usable_sample_count"] == 27
    assert result["gaze_availability_rate"] == pytest.approx(27 / 58)
    assert result["nominal_sample_ratio"] == pytest.approx(58 / 60)
    assert result["usable_nominal_ratio"] == pytest.approx(27 / 60)


def test_few_but_valid_samples():
    result = assess_window_quality(make_window(9, 0))

    assert result["gaze_availability_rate"] == 1.0
    assert result["nominal_sample_ratio"] == pytest.approx(0.15)
    assert result["usable_nominal_ratio"] == pytest.approx(0.15)


def test_all_invalid():
    result = assess_window_quality(make_window(60, 60))

    assert result["gaze_availability_rate"] == 0.0
    assert result["usable_nominal_ratio"] == 0.0


def test_empty_window():
    result = assess_window_quality(make_window(0, 0))

    assert result["has_data"] is False
    assert result["gaze_availability_rate"] is None
    assert result["nominal_sample_ratio"] == 0.0


def test_invalid_count_exceeds_samples():
    with pytest.raises(ValueError):
        assess_window_quality(make_window(5, 6))


def test_invalid_frequency():
    with pytest.raises(ValueError):
        assess_window_quality(make_window(60, 0), nominal_hz=0)


def test_inconsistent_availability():
    window = make_window(60, 5)
    window["gaze_availability_rate"] = 1.0

    with pytest.raises(ValueError):
        assess_window_quality(window)


def test_non_positive_window_duration():
    with pytest.raises(ValueError):
        assess_window_quality(make_window(60, 0, duration=0))


def test_different_window_duration():
    result = assess_window_quality(
        make_window(30, 0, duration=0.5)
    )

    assert result["nominal_sample_ratio"] == pytest.approx(1.0)
