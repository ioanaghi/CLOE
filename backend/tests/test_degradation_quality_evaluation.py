
from types import SimpleNamespace

import pytest

from backend.processing.window_features import (
    extract_window_features,
)
from backend.processing.degradation_quality_evaluation import (
    evaluate_degraded_windows,
    compare_quality_decisions,
)


POLICY = SimpleNamespace(
    min_gaze_availability=0.80,
    min_nominal_sample_ratio=0.80,
    min_usable_nominal_ratio=0.70,
    require_complete_window=True,
)


def dataset():
    timestamps = [
        round(i * 1_000_000 / 60)
        for i in range(120)
    ]
    sources = ["BOTH"] * 120

    references = extract_window_features(
        timestamps,
        sources,
    )

    duration = (
        timestamps[-1] - timestamps[0]
    ) / 1_000_000

    return timestamps, sources, references, duration



def run(timestamps, sources, references, duration,
        reference_start_timestamp=None):

    if reference_start_timestamp is None:
        reference_start_timestamp = 0

    return evaluate_degraded_windows(
        timestamps,
        sources,
        references,
        duration,
        POLICY,
        reference_start_timestamp=reference_start_timestamp,
    )


def test_baseline_eligible():
    timestamps, sources, refs, duration = dataset()

    result = run(timestamps, sources, refs, duration)

    assert result[0]["status"] == "ELIGIBLE"
    assert result[0]["sample_count"] == 60


def test_invalid_gaze_reduces_availability():
    timestamps, sources, refs, duration = dataset()

    degraded = sources.copy()

    for index in range(20, 40):
        degraded[index] = "NONE"

    result = run(timestamps, degraded, refs, duration)

    assert result[0]["status"] == "UNKNOWN"
    assert "LOW_AVAILABILITY" in result[0]["reasons"]


def test_dropout_reduces_nominal_coverage():
    timestamps, sources, refs, duration = dataset()

    removed = set(range(20, 40))

    kept_timestamps = [
        timestamp
        for index, timestamp in enumerate(timestamps)
        if index not in removed
    ]

    kept_sources = [
        source
        for index, source in enumerate(sources)
        if index not in removed
    ]

    result = run(
        kept_timestamps,
        kept_sources,
        refs,
        duration,
    )

    assert result[0]["sample_count"] == 40
    assert result[0]["status"] == "UNKNOWN"
    assert "LOW_NOMINAL_SAMPLE_RATIO" in result[0]["reasons"]


def test_original_boundaries_preserved():
    timestamps, sources, refs, duration = dataset()

    result = run(timestamps, sources, refs, duration)

    assert len(result) == len(refs)

    for original, current in zip(refs, result):
        assert current["start_s"] == original["start_s"]
        assert current["end_s"] == original["end_s"]



def test_first_sample_dropout_rejected():
    timestamps, sources, refs, duration = dataset()

    with pytest.raises(ValueError, match="Temporal alignment"):
        run(
            timestamps[1:],
            sources[1:],
            refs,
            duration,
            reference_start_timestamp=timestamps[0],
        )



def test_newly_rejected_windows_reported():
    baseline = [{
        "start_s": 0.0,
        "end_s": 1.0,
        "status": "ELIGIBLE",
        "reasons": [],
    }]

    degraded = [{
        "start_s": 0.0,
        "end_s": 1.0,
        "status": "UNKNOWN",
        "reasons": ["LOW_AVAILABILITY"],
    }]

    result = compare_quality_decisions(
        baseline, degraded
    )

    assert len(result["newly_rejected"]) == 1
    assert result["recovered"] == []


def test_recovered_window_reported():
    baseline = [{
        "start_s": 0.0,
        "end_s": 1.0,
        "status": "UNKNOWN",
        "reasons": ["LOW_AVAILABILITY"],
    }]

    degraded = [{
        "start_s": 0.0,
        "end_s": 1.0,
        "status": "ELIGIBLE",
        "reasons": [],
    }]

    result = compare_quality_decisions(
        baseline, degraded
    )

    assert len(result["recovered"]) == 1


def test_mismatched_reference_rejected():
    timestamps, sources, refs, duration = dataset()

    with pytest.raises(ValueError):
        run(
            timestamps,
            sources,
            refs[:-1],
            duration,
        )
