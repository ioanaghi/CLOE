
import csv
import json

import pytest

from backend.processing.analyze_real_windows import (
    validate_recording_identity,
    validate_window_alignment,
    evaluate_real_windows,
    export_results,
)


def make_window_csv(path, windows):
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["start_s", "end_s", "sample_count"],
        )
        writer.writeheader()
        for start, end in windows:
            writer.writerow({
                "start_s": start,
                "end_s": end,
                "sample_count": 3,
            })


def decisions():
    return [
        {
            "start_s": 0.0,
            "end_s": 0.5,
            "quality_gate_status": "ELIGIBLE",
            "quality_gate_reasons": "",
        },
        {
            "start_s": 0.5,
            "end_s": 1.0,
            "quality_gate_status": "UNKNOWN",
            "quality_gate_reasons": "LOW_AVAILABILITY",
        },
    ]


def gaze_data():
    timestamps = [
        1000000,
        1250000,
        1500000,
        1750000,
        2000000,
    ]
    velocities = [
        {"velocity": 2.0, "reason": None},
        {"velocity": 3.0, "reason": None},
        {"velocity": 12.0, "reason": None},
        {"velocity": 1.0, "reason": None},
    ]
    return timestamps, velocities


def test_matching_recording_identifiers():
    stem = validate_recording_identity(
        "data/raw/tobii/example.csv",
        "data/processed/example_window_features.csv",
        "data/processed/example_quality_decisions.csv",
    )
    assert stem == "example"


def test_mismatched_recording_identifier():
    with pytest.raises(ValueError):
        validate_recording_identity(
            "example.csv",
            "different_window_features.csv",
            "example_quality_decisions.csv",
        )


def test_window_alignment_passes(tmp_path):
    path = tmp_path / "windows.csv"
    make_window_csv(path, [(0.0, 0.5), (0.5, 1.0)])

    assert validate_window_alignment(path, decisions()) == 2


def test_window_alignment_mismatch(tmp_path):
    path = tmp_path / "windows.csv"
    make_window_csv(path, [(0.0, 0.5), (0.6, 1.0)])

    with pytest.raises(ValueError):
        validate_window_alignment(path, decisions())


def test_window_count_mismatch(tmp_path):
    path = tmp_path / "windows.csv"
    make_window_csv(path, [(0.0, 0.5)])

    with pytest.raises(ValueError):
        validate_window_alignment(path, decisions())


def test_quality_gate_blocks_real_window_pipeline():
    timestamps, velocities = gaze_data()

    evaluations = evaluate_real_windows(
        timestamps, velocities, decisions(), [5.0],
    )

    rows = evaluations[0]["windows"]

    assert len(rows) == 2
    assert rows[0]["feature_status"] == "AVAILABLE"
    assert rows[1]["feature_status"] == "UNAVAILABLE"
    assert rows[1]["features"] is None
    assert rows[1]["quality_gate_reasons"] == "LOW_AVAILABILITY"


def test_quality_counts_preserved_across_thresholds():
    timestamps, velocities = gaze_data()

    evaluations = evaluate_real_windows(
        timestamps,
        velocities,
        decisions(),
        [2.0, 5.0, 10.0],
    )

    assert len(evaluations) == 3

    for evaluation in evaluations:
        summary = evaluation["summary"]

        assert summary["window_count"] == 2
        assert summary["quality_gate_counts"]["ELIGIBLE"] == 1
        assert summary["quality_gate_counts"]["UNKNOWN"] == 1
        assert summary["feature_status_counts"]["UNAVAILABLE"] == 1


def test_duplicate_threshold_rejected():
    timestamps, velocities = gaze_data()

    with pytest.raises(ValueError):
        evaluate_real_windows(
            timestamps,
            velocities,
            decisions(),
            [5.0, 5.0],
        )


def test_export_readback(tmp_path):
    timestamps, velocities = gaze_data()

    evaluations = evaluate_real_windows(
        timestamps, velocities, decisions(), [5.0],
    )

    summary_path, policy_path = export_results(
        tmp_path,
        "synthetic",
        evaluations,
        {"experiment": "M0.4-T04-C"},
    )

    with summary_path.open(encoding="utf-8") as file:
        summaries = json.load(file)

    with policy_path.open(encoding="utf-8") as file:
        policy = json.load(file)

    csv_path = tmp_path / "synthetic_windows_5p0.csv"
    with csv_path.open(
        newline="", encoding="utf-8"
    ) as file:
        rows = list(csv.DictReader(file))

    assert len(summaries) == 1
    assert summaries[0]["summary"]["window_count"] == 2
    assert policy["experiment"] == "M0.4-T04-C"
    assert len(rows) == 2

    assert json.loads(rows[0]["features_json"]) is not None
    assert rows[1]["features_json"] == ""
    assert rows[1]["feature_status"] == "UNAVAILABLE"
