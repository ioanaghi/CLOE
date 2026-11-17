
import csv

import pytest

from backend.processing.quality_window_integration import (
    load_quality_decisions,
    integrate_quality_windows,
    summarize_feature_availability,
)


def make_csv(tmp_path, rows):
    path = tmp_path / "quality_decisions.csv"

    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["start_s", "end_s", "status", "reasons"],
        )
        writer.writeheader()
        writer.writerows(rows)

    return path


def decision(start, end, status, reasons=""):
    return {
        "start_s": start,
        "end_s": end,
        "status": status,
        "reasons": reasons,
    }


def make_gaze_data():
    timestamps = [
        0,
        250000,
        500000,
        750000,
        1000000,
    ]

    velocities = [
        {"velocity": 2.0, "reason": None},
        {"velocity": 3.0, "reason": None},
        {"velocity": 12.0, "reason": None},
        {"velocity": 1.0, "reason": None},
    ]

    return timestamps, velocities


def test_load_valid_decisions(tmp_path):
    path = make_csv(tmp_path, [
        decision(0.0, 0.5, "ELIGIBLE"),
        decision(0.5, 1.0, "UNKNOWN", "LOW_AVAILABILITY"),
    ])

    result = load_quality_decisions(path)

    assert len(result) == 2
    assert result[0]["quality_gate_status"] == "ELIGIBLE"
    assert result[1]["quality_gate_status"] == "UNKNOWN"


def test_rejection_reasons_preserved(tmp_path):
    reasons = "LOW_AVAILABILITY|LOW_USABLE_NOMINAL_RATIO"

    path = make_csv(tmp_path, [
        decision(0.0, 1.0, "UNKNOWN", reasons),
    ])

    result = load_quality_decisions(path)

    assert result[0]["quality_gate_reasons"] == reasons


def test_invalid_status_rejected(tmp_path):
    path = make_csv(tmp_path, [
        decision(0.0, 1.0, "REJECTED"),
    ])

    with pytest.raises(ValueError):
        load_quality_decisions(path)


def test_invalid_window_rejected(tmp_path):
    path = make_csv(tmp_path, [
        decision(1.0, 0.5, "ELIGIBLE"),
    ])

    with pytest.raises(ValueError):
        load_quality_decisions(path)


def test_unordered_windows_rejected(tmp_path):
    path = make_csv(tmp_path, [
        decision(0.5, 1.0, "ELIGIBLE"),
        decision(0.0, 0.5, "ELIGIBLE"),
    ])

    with pytest.raises(ValueError):
        load_quality_decisions(path)


def test_missing_column_rejected(tmp_path):
    path = tmp_path / "missing_column.csv"

    path.write_text(
        "start_s,end_s,status\n"
        "0.0,1.0,ELIGIBLE\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        load_quality_decisions(path)


def test_eligible_window_produces_features(tmp_path):
    path = make_csv(tmp_path, [
        decision(0.0, 1.0, "ELIGIBLE"),
    ])

    decisions = load_quality_decisions(path)
    timestamps, velocities = make_gaze_data()

    result = integrate_quality_windows(
        timestamps,
        velocities,
        decisions,
        threshold=5.0,
    )

    assert len(result) == 1
    assert result[0]["feature_status"] == "AVAILABLE"
    assert result[0]["features"] is not None


def test_unknown_window_blocks_features(tmp_path):
    path = make_csv(tmp_path, [
        decision(
            0.0,
            1.0,
            "UNKNOWN",
            "LOW_AVAILABILITY",
        ),
    ])

    decisions = load_quality_decisions(path)
    timestamps, velocities = make_gaze_data()

    result = integrate_quality_windows(
        timestamps,
        velocities,
        decisions,
        threshold=5.0,
    )

    assert result[0]["feature_status"] == "UNAVAILABLE"
    assert result[0]["features"] is None
    assert result[0]["feature_reason"] == "QUALITY_GATE_UNKNOWN"
    assert result[0]["quality_gate_reasons"] == "LOW_AVAILABILITY"


def test_all_windows_preserved(tmp_path):
    path = make_csv(tmp_path, [
        decision(0.0, 0.5, "ELIGIBLE"),
        decision(0.5, 1.0, "UNKNOWN", "LOW_AVAILABILITY"),
    ])

    decisions = load_quality_decisions(path)
    timestamps, velocities = make_gaze_data()

    results = integrate_quality_windows(
        timestamps,
        velocities,
        decisions,
        threshold=5.0,
    )

    assert len(results) == len(decisions)
    assert results[0]["start_s"] == 0.0
    assert results[1]["start_s"] == 0.5


def test_availability_summary(tmp_path):
    path = make_csv(tmp_path, [
        decision(0.0, 0.5, "ELIGIBLE"),
        decision(0.5, 1.0, "UNKNOWN", "LOW_AVAILABILITY"),
    ])

    timestamps, velocities = make_gaze_data()

    results = integrate_quality_windows(
        timestamps,
        velocities,
        load_quality_decisions(path),
        threshold=5.0,
    )

    summary = summarize_feature_availability(results)

    assert summary["window_count"] == 2
    assert summary["quality_gate_counts"]["ELIGIBLE"] == 1
    assert summary["quality_gate_counts"]["UNKNOWN"] == 1
    assert summary["feature_status_counts"]["AVAILABLE"] == 1
    assert summary["feature_status_counts"]["UNAVAILABLE"] == 1
