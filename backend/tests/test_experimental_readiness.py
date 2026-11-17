
import csv
import json

from backend.processing.experimental_readiness import (
    audit_project,
    verify_quality_artifacts,
)


STEM = "tobii_20261029T143930551761Z"


def write_csv(path, fields, rows):
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(
            file, fieldnames=fields
        )
        writer.writeheader()
        writer.writerows(rows)


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value),
        encoding="utf-8",
    )


def make_artifacts(root):
    processed = root / "data/processed"
    window_dir = processed / "window_oculomotor"
    degradation = processed / "degradation"

    raw = root / "data/raw/tobii" / f"{STEM}.csv"
    raw.parent.mkdir(parents=True, exist_ok=True)
    raw.write_text(
        "device_time_stamp\n1000\n",
        encoding="utf-8",
    )

    original = []
    degraded = []

    for index in range(20):
        status = (
            "ELIGIBLE" if index < 16 else "UNKNOWN"
        )

        reasons = (
            "" if status == "ELIGIBLE"
            else "LOW_AVAILABILITY"
        )

        base = {
            "start_s": f"{index * 0.5:.1f}",
            "end_s": f"{index * 0.5 + 1:.1f}",
            "status": status,
            "reasons": reasons,
        }

        original.append(base)

        for scenario in (
            "BASELINE",
            "INVALID_3",
            "DROPOUT_3",
            "DROPOUT_10_PERCENT",
        ):
            degraded.append({
                "scenario": scenario,
                **base,
            })

    write_csv(
        processed / f"{STEM}_quality_decisions.csv",
        ["start_s", "end_s", "status", "reasons"],
        original,
    )

    write_json(
        processed / f"{STEM}_quality_decisions.policy.json",
        {"min_gaze_availability": 0.8},
    )

    (processed / f"{STEM}_window_features.csv").write_text(
        "start_s,end_s\n",
        encoding="utf-8",
    )

    write_json(
        window_dir / f"{STEM}_window_summary.json",
        [],
    )

    write_json(
        window_dir / f"{STEM}_window_policy.json",
        {"experiment": "M0.4-T04-C"},
    )

    for threshold in ("2p0", "5p0", "10p0"):
        path = window_dir / (
            f"{STEM}_windows_{threshold}.csv"
        )
        path.write_text(
            "start_s,end_s\n",
            encoding="utf-8",
        )

    write_csv(
        degradation / "t05_c4_quality_decisions.csv",
        ["scenario", "start_s", "end_s",
         "status", "reasons"],
        degraded,
    )

    summary = {
        "experiment": "M0.4-T05-C4",
        "source_recording": f"{STEM}.csv",
        "reference_windows": 20,
        "scenarios": {
            name: {
                "windows": 20,
                "eligible": 16,
                "unknown": 4,
            }
            for name in (
                "BASELINE",
                "INVALID_3",
                "DROPOUT_3",
                "DROPOUT_10_PERCENT",
            )
        },
    }

    write_json(
        degradation / "t05_c4_quality_summary.json",
        summary,
    )

    return root


def test_complete_artifacts_pass(tmp_path):
    make_artifacts(tmp_path)

    result = audit_project(tmp_path)

    assert result["status"] == "PASS"
    assert result["scenario_results"]["BASELINE"] == {
        "eligible": 16,
        "unknown": 4,
        "windows": 20,
    }


def test_missing_artifact_fails(tmp_path):
    make_artifacts(tmp_path)

    path = (
        tmp_path / "data/processed/degradation"
        / "t05_c4_quality_summary.json"
    )
    path.unlink()

    result = audit_project(tmp_path)

    assert result["status"] == "FAIL"


def test_changed_baseline_status_fails(tmp_path):
    make_artifacts(tmp_path)

    path = (
        tmp_path / "data/processed/degradation"
        / "t05_c4_quality_decisions.csv"
    )

    with path.open(newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))

    baseline = next(
        row for row in rows
        if row["scenario"] == "BASELINE"
    )
    baseline["status"] = "UNKNOWN"

    write_csv(path, list(rows[0]), rows)

    result = audit_project(tmp_path)

    assert result["status"] == "FAIL"


def test_incorrect_summary_count_fails(tmp_path):
    make_artifacts(tmp_path)

    path = (
        tmp_path / "data/processed/degradation"
        / "t05_c4_quality_summary.json"
    )

    summary = json.loads(path.read_text())
    summary["scenarios"]["BASELINE"]["eligible"] = 15

    write_json(path, summary)

    result = audit_project(tmp_path)

    assert result["status"] == "FAIL"


def test_window_alignment_mismatch_fails(tmp_path):
    make_artifacts(tmp_path)

    path = (
        tmp_path / "data/processed/degradation"
        / "t05_c4_quality_decisions.csv"
    )

    with path.open(newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))

    rows[0]["start_s"] = "0.25"

    write_csv(path, list(rows[0]), rows)

    assert audit_project(tmp_path)["status"] == "FAIL"


def test_missing_screenshots_are_warnings(tmp_path):
    make_artifacts(tmp_path)

    result = audit_project(tmp_path)

    assert result["status"] == "PASS"
    assert len(result["warnings"]) == 1


def test_source_hashes_present(tmp_path):
    make_artifacts(tmp_path)

    result = audit_project(tmp_path)

    assert len(result["source_sha256"]) == 4
    assert all(
        len(digest) == 64
        for digest in result["source_sha256"].values()
    )


def test_audit_does_not_modify_sources(tmp_path):
    make_artifacts(tmp_path)

    source = (
        tmp_path / "data/raw/tobii"
        / f"{STEM}.csv"
    )

    before = source.read_bytes()

    audit_project(tmp_path)

    assert source.read_bytes() == before
