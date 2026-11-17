
import csv
import json

import pytest

from backend.processing.analyze_oculomotor_features import (
    analyze_samples,
    extract_features,
    save_analysis,
)


def sample(timestamp, point):
    return {
        "timestamp": timestamp,
        "point": point,
        "source": "BOTH" if point is not None else "NONE",
    }


def valid_samples():
    return [
        sample(0, (0.20, 0.50)),
        sample(16667, (0.21, 0.50)),
        sample(33334, (0.41, 0.50)),
        sample(50001, (0.42, 0.50)),
    ]


def test_full_pipeline():
    velocities, evaluations = analyze_samples(
        valid_samples(), [5.0]
    )

    assert len(velocities) == 3
    assert len(evaluations) == 1

    summary = evaluations[0]["summary"]
    segments = evaluations[0]["segments"]

    assert summary["total_intervals"] == 3
    assert summary["segment_count"] == 3
    assert [s["state"] for s in segments] == [
        "LOW_VELOCITY",
        "HIGH_VELOCITY",
        "LOW_VELOCITY",
    ]


def test_duration_coverage():
    samples = valid_samples()
    _, evaluations = analyze_samples(samples, [5.0])

    total_duration = sum(
        s["duration_ms"]
        for s in evaluations[0]["segments"]
    )

    observed_span = (
        samples[-1]["timestamp"] - samples[0]["timestamp"]
    ) / 1000

    assert total_duration == pytest.approx(observed_span)
    assert total_duration == pytest.approx(50.001)


def test_velocity_statistics_integration():
    _, evaluations = analyze_samples(valid_samples(), [5.0])

    segments = evaluations[0]["segments"]

    assert segments[0]["valid_velocity_count"] == 1
    assert segments[0]["mean_velocity"] is not None
    assert segments[1]["max_velocity"] > segments[0]["max_velocity"]
    assert segments[1]["std_velocity"] == 0.0


def test_unknown_intervals_are_preserved():
    samples = [
        sample(0, (0.2, 0.5)),
        sample(16667, (0.2, 0.5)),
        sample(33334, None),
        sample(50001, (0.3, 0.5)),
    ]

    velocities, evaluations = analyze_samples(samples, [5.0])

    summary = evaluations[0]["summary"]

    assert len(velocities) == 3
    assert summary["interval_count_by_state"]["UNKNOWN"] == 2

    unknown_segments = [
        s for s in evaluations[0]["segments"]
        if s["state"] == "UNKNOWN"
    ]

    assert len(unknown_segments) == 1
    assert unknown_segments[0]["mean_velocity"] is None


def test_unknown_count_invariant_across_thresholds():
    _, evaluations = analyze_samples(
        valid_samples() + [sample(66668, None)],
        [2.0, 5.0, 10.0],
    )

    counts = [
        e["summary"]["interval_count_by_state"]["UNKNOWN"]
        for e in evaluations
    ]

    assert counts == [1, 1, 1]


def test_empty_recording():
    velocities, evaluations = analyze_samples([], [5.0])

    assert velocities == []
    assert evaluations[0]["segments"] == []
    assert evaluations[0]["summary"]["total_intervals"] == 0


def test_mismatched_velocity_count():
    with pytest.raises(ValueError):
        extract_features(valid_samples(), [], 5.0)


def test_duplicate_thresholds_rejected():
    with pytest.raises(ValueError):
        analyze_samples(valid_samples(), [5.0, 5.0])


def test_export_readback(tmp_path):
    _, evaluations = analyze_samples(valid_samples(), [5.0])

    metadata = {
        "experiment": "M0.4-T03-D",
        "thresholds": [5.0],
    }

    summary_path, policy_path = save_analysis(
        tmp_path,
        "synthetic",
        evaluations,
        metadata,
    )

    with summary_path.open(encoding="utf-8") as file:
        summaries = json.load(file)

    with policy_path.open(encoding="utf-8") as file:
        policy = json.load(file)

    segment_path = tmp_path / "synthetic_features_5p0.csv"

    with segment_path.open(
        newline="", encoding="utf-8"
    ) as file:
        saved_segments = list(csv.DictReader(file))

    assert len(summaries) == 1
    assert summaries[0]["features"]["total_intervals"] == 3
    assert policy["thresholds"] == [5.0]
    assert len(saved_segments) == 3
