import pytest

from backend.processing.invalid_gaze_processing import detect_invalid_runs

def test_one_invalid_run():
    sources = ["BOTH", "NONE", "NONE", "LEFT"]

    assert detect_invalid_runs(sources) == [
        {
            "start_index": 1,
            "end_index": 2,
            "sample_count": 2,
        }
    ]


def test_multiple_invalid_runs():
    sources = [
        "BOTH", "NONE", "LEFT",
        "NONE", "NONE", "RIGHT"
    ]

    result = detect_invalid_runs(sources)

    assert len(result) == 2
    assert result[0]["sample_count"] == 1
    assert result[1]["sample_count"] == 2


def test_all_valid():
    sources = ["BOTH", "LEFT", "RIGHT"]

    assert detect_invalid_runs(sources) == []


def test_all_invalid():
    sources = ["NONE", "NONE", "NONE"]

    assert detect_invalid_runs(sources) == [
        {
            "start_index": 0,
            "end_index": 2,
            "sample_count": 3,
        }
    ]


def test_invalid_run_at_end():
    sources = ["BOTH", "NONE", "NONE"]

    result = detect_invalid_runs(sources)

    assert result[0]["start_index"] == 1
    assert result[0]["end_index"] == 2


def test_empty_input():
    assert detect_invalid_runs([]) == []


def test_unknown_source():
    with pytest.raises(ValueError):
        detect_invalid_runs(["BOTH", "UNKNOWN"])
