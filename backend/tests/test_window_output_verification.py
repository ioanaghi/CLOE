
import csv
import json

import pytest

from backend.processing.verify_window_outputs import (
    sha256_file,
    verify_window_outputs,
)


def write_csv(path, headers, rows):
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def create_fixture(tmp_path):
    stem = "synthetic"
    raw = tmp_path / f"{stem}.csv"
    windows = tmp_path / f"{stem}_window_features.csv"
    quality = tmp_path / f"{stem}_quality_decisions.csv"
    output = tmp_path / "outputs"
    output.mkdir()

    raw.write_text(
        "device_time_stamp\n0\n100000\n200000\n",
        encoding="utf-8",
    )

    write_csv(
        windows,
        ["start_s", "end_s", "sample_count"],
        [
            {"start_s": 0.0, "end_s": 0.5, "sample_count": 3},
            {"start_s": 0.5, "end_s": 1.0, "sample_count": 0},
        ],
    )

    write_csv(
        quality,
        ["start_s", "end_s", "status", "reasons"],
        [
            {
                "start_s": 0.0,
                "end_s": 0.5,
                "status": "ELIGIBLE",
                "reasons": "",
            },
            {
                "start_s": 0.5,
                "end_s": 1.0,
                "status": "UNKNOWN",
                "reasons": "LOW_AVAILABILITY",
            },
        ],
    )

    features = {
        "total_intervals": 2,
        "segment_count": 1,
        "interval_count_by_state": {
            "LOW_VELOCITY": 2,
            "HIGH_VELOCITY": 0,
            "UNKNOWN": 0,
        },
        "interval_share_by_state": {
            "LOW_VELOCITY": 1.0,
            "HIGH_VELOCITY": 0.0,
            "UNKNOWN": 0.0,
        },
        "segment_count_by_state": {
            "LOW_VELOCITY": 1,
            "HIGH_VELOCITY": 0,
            "UNKNOWN": 0,
        },
        "transition_count": 0,
    }

    output_headers = [
        "start_s", "end_s", "threshold",
        "quality_gate_status", "quality_gate_reasons",
        "selected_interval_count",
        "feature_status", "feature_reason",
        "features_json",
    ]

    for threshold in (2.0, 5.0):
        rows = [
            {
                "start_s": 0.0,
                "end_s": 0.5,
                "threshold": threshold,
                "quality_gate_status": "ELIGIBLE",
                "quality_gate_reasons": "",
                "selected_interval_count": 2,
                "feature_status": "AVAILABLE",
                "feature_reason": "",
                "features_json": json.dumps(features),
            },
            {
                "start_s": 0.5,
                "end_s": 1.0,
                "threshold": threshold,
                "quality_gate_status": "UNKNOWN",
                "quality_gate_reasons": "LOW_AVAILABILITY",
                "selected_interval_count": 0,
                "feature_status": "UNAVAILABLE",
                "feature_reason": "QUALITY_GATE_UNKNOWN",
                "features_json": "",
            },
        ]

        label = str(threshold).replace(".", "p")

        write_csv(
            output / f"{stem}_windows_{label}.csv",
            output_headers,
            rows,
        )

    summaries = [
        {
            "threshold": threshold,
            "summary": {
                "window_count": 2,
                "quality_gate_counts": {
                    "ELIGIBLE": 1,
                    "UNKNOWN": 1,
                },
                "feature_status_counts": {
                    "AVAILABLE": 1,
                    "UNAVAILABLE": 1,
                },
                "unavailable_reasons": {
                    "QUALITY_GATE_UNKNOWN": 1,
                },
            },
        }
        for threshold in (2.0, 5.0)
    ]

    policy = {
        "experiment": "M0.4-T04-C",
        "recording": raw.name,
        "raw_sha256": sha256_file(raw),
        "window_csv_sha256": sha256_file(windows),
        "quality_csv_sha256": sha256_file(quality),
        "samples": 3,
        "velocity_intervals": 2,
        "windows": 2,
        "quality_counts": {
            "ELIGIBLE": 1,
            "UNKNOWN": 1,
        },
        "thresholds": [2.0, 5.0],
        "alignment_method": "fully_contained_velocity_intervals",
    }

    (output / f"{stem}_window_summary.json").write_text(
        json.dumps(summaries),
        encoding="utf-8",
    )

    (output / f"{stem}_window_policy.json").write_text(
        json.dumps(policy),
        encoding="utf-8",
    )

    return raw, windows, quality, output


def run_verifier(paths):
    return verify_window_outputs(*paths)


def edit_csv(paths, filename, update):
    output = paths[3]
    path = output / filename

    with path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        headers = reader.fieldnames
        rows = list(reader)

    update(rows)

    write_csv(path, headers, rows)


def test_valid_artifacts_pass(tmp_path):
    paths = create_fixture(tmp_path)

    reports = run_verifier(paths)

    assert len(reports) == 2
    assert reports[0]["windows"] == 2
    assert reports[0]["available"] == 1
    assert reports[0]["unavailable"] == 1


def test_modified_source_hash_rejected(tmp_path):
    paths = create_fixture(tmp_path)

    with paths[0].open("a", encoding="utf-8") as file:
        file.write("300000\n")

    with pytest.raises(ValueError, match="hash mismatch"):
        run_verifier(paths)


def test_changed_quality_status_rejected(tmp_path):
    paths = create_fixture(tmp_path)

    edit_csv(
        paths,
        "synthetic_windows_2p0.csv",
        lambda rows: rows[1].update({
            "quality_gate_status": "ELIGIBLE"
        }),
    )

    with pytest.raises(ValueError, match="Quality Gate status"):
        run_verifier(paths)


def test_unknown_feature_leak_rejected(tmp_path):
    paths = create_fixture(tmp_path)

    edit_csv(
        paths,
        "synthetic_windows_2p0.csv",
        lambda rows: rows[1].update({
            "features_json": '{"total_intervals": 1}'
        }),
    )

    with pytest.raises(ValueError, match="exposed features"):
        run_verifier(paths)


def test_wrong_window_count_rejected(tmp_path):
    paths = create_fixture(tmp_path)

    edit_csv(
        paths,
        "synthetic_windows_2p0.csv",
        lambda rows: rows.pop(),
    )

    with pytest.raises(ValueError, match="wrong window count"):
        run_verifier(paths)


def test_invalid_feature_json_rejected(tmp_path):
    paths = create_fixture(tmp_path)

    edit_csv(
        paths,
        "synthetic_windows_2p0.csv",
        lambda rows: rows[0].update({
            "features_json": "{invalid json}"
        }),
    )

    with pytest.raises(ValueError, match="invalid features JSON"):
        run_verifier(paths)


def test_incorrect_feature_interval_count_rejected(tmp_path):
    paths = create_fixture(tmp_path)

    def corrupt(rows):
        features = json.loads(rows[0]["features_json"])
        features["total_intervals"] = 10
        rows[0]["features_json"] = json.dumps(features)

    edit_csv(paths, "synthetic_windows_2p0.csv", corrupt)

    with pytest.raises(ValueError, match="interval count mismatch"):
        run_verifier(paths)


def test_changed_threshold_rejected(tmp_path):
    paths = create_fixture(tmp_path)

    edit_csv(
        paths,
        "synthetic_windows_5p0.csv",
        lambda rows: rows[0].update({"threshold": 10.0}),
    )

    with pytest.raises(ValueError, match="incorrect threshold"):
        run_verifier(paths)


def test_modified_summary_rejected(tmp_path):
    paths = create_fixture(tmp_path)
    path = paths[3] / "synthetic_window_summary.json"

    summaries = json.loads(path.read_text(encoding="utf-8"))
    summaries[0]["summary"]["feature_status_counts"]["AVAILABLE"] = 2

    path.write_text(json.dumps(summaries), encoding="utf-8")

    with pytest.raises(ValueError, match="availability mismatch"):
        run_verifier(paths)


def test_changed_interval_selection_rejected(tmp_path):
    paths = create_fixture(tmp_path)

    def corrupt(rows):
        rows[0]["selected_interval_count"] = 1

        features = json.loads(rows[0]["features_json"])
        features["total_intervals"] = 1
        features["interval_count_by_state"]["LOW_VELOCITY"] = 1
        rows[0]["features_json"] = json.dumps(features)

    edit_csv(paths, "synthetic_windows_5p0.csv", corrupt)

    with pytest.raises(ValueError):
        run_verifier(paths)
