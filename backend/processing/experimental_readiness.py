
import csv
import hashlib
import json
import math
from collections import Counter
from pathlib import Path


STEM = "tobii_20261029T143930551761Z"

SCENARIOS = (
    "BASELINE",
    "INVALID_3",
    "DROPOUT_3",
    "DROPOUT_10_PERCENT",
)

EVIDENCE_FILES = (
    "t05-feature-reliability-tests.png",
    "t05-real-feature-sensitivity.png",
    "t05-temporal-stability-tests.png",
    "t05-degradation-tests.png",
    "t05-c4-quality-reevaluation-a.png",
    "t05-c4-quality-reevaluation-b.png",
    "t05-c4-output-readback.png",
    "t05-c4-regression-tests.png",
)


def sha256_file(path):
    digest = hashlib.sha256()

    with Path(path).open("rb") as file:
        for chunk in iter(lambda: file.read(65536), b""):
            digest.update(chunk)

    return digest.hexdigest()


def read_csv(path, required_fields):
    with Path(path).open(
        newline="", encoding="utf-8-sig"
    ) as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError("Missing CSV header")

        if len(reader.fieldnames) != len(set(reader.fieldnames)):
            raise ValueError("Duplicate CSV columns")

        if not set(required_fields).issubset(reader.fieldnames):
            raise ValueError("Missing required CSV columns")

        rows = list(reader)

    for row in rows:
        if None in row or any(value is None for value in row.values()):
            raise ValueError("Malformed CSV row")

    return rows


def read_json(path):
    with Path(path).open(encoding="utf-8") as file:
        return json.load(file)


def verify_quality_artifacts(
    original_rows,
    degraded_rows,
    summary,
):
    """
    Verify saved T05-C4 decisions against the M0.3 baseline.

    Does not recompute gaze-processing algorithms.
    """
    required_scenarios = set(SCENARIOS)

    if set(summary.get("scenarios", {})) != required_scenarios:
        raise ValueError("Incorrect scenario set")

    if len(original_rows) != 20:
        raise ValueError("Expected 20 original windows")

    if len(degraded_rows) != 80:
        raise ValueError("Expected 80 degraded decision rows")

    original = [
        (
            float(row["start_s"]),
            float(row["end_s"]),
            row["status"],
            frozenset(filter(None, row["reasons"].split("|"))),
        )
        for row in original_rows
    ]

    if any(
        not math.isfinite(start)
        or not math.isfinite(end)
        or end <= start
        for start, end, _, _ in original
    ):
        raise ValueError("Invalid reference window boundaries")

    results = {}

    for scenario in SCENARIOS:
        rows = [
            row for row in degraded_rows
            if row["scenario"] == scenario
        ]

        if len(rows) != 20:
            raise ValueError(
                f"{scenario}: expected 20 windows"
            )

        counts = Counter(row["status"] for row in rows)

        if set(counts) - {"ELIGIBLE", "UNKNOWN"}:
            raise ValueError(
                f"{scenario}: invalid quality status"
            )

        reported = summary["scenarios"][scenario]

        if (
            counts["ELIGIBLE"] != reported["eligible"]
            or counts["UNKNOWN"] != reported["unknown"]
            or reported["windows"] != 20
        ):
            raise ValueError(
                f"{scenario}: CSV/JSON count mismatch"
            )

        for index, (row, reference) in enumerate(
            zip(rows, original)
        ):
            start = float(row["start_s"])
            end = float(row["end_s"])

            if not (
                math.isclose(
                    start, reference[0],
                    rel_tol=0, abs_tol=1e-6
                )
                and math.isclose(
                    end, reference[1],
                    rel_tol=0, abs_tol=1e-6
                )
            ):
                raise ValueError(
                    f"{scenario}: window alignment mismatch "
                    f"at index {index}"
                )

            if scenario == "BASELINE":
                reasons = frozenset(
                    filter(None, row["reasons"].split("|"))
                )

                if (
                    row["status"] != reference[2]
                    or reasons != reference[3]
                ):
                    raise ValueError(
                        f"Baseline mismatch at window {index}"
                    )

        results[scenario] = {
            "eligible": counts["ELIGIBLE"],
            "unknown": counts["UNKNOWN"],
            "windows": len(rows),
        }

    return results


def audit_project(root):
    """
    Audit selected M0.4 experimental artifacts.

    Original data and existing results are never modified.
    """
    root = Path(root)

    raw = root / "data/raw/tobii" / f"{STEM}.csv"
    processed = root / "data/processed"

    quality_csv = processed / f"{STEM}_quality_decisions.csv"
    quality_policy = processed / (
        f"{STEM}_quality_decisions.policy.json"
    )

    window_dir = processed / "window_oculomotor"
    c4_dir = processed / "degradation"

    c4_csv = c4_dir / "t05_c4_quality_decisions.csv"
    c4_json = c4_dir / "t05_c4_quality_summary.json"

    required_files = [
        raw,
        quality_csv,
        quality_policy,
        processed / f"{STEM}_window_features.csv",
        window_dir / f"{STEM}_window_summary.json",
        window_dir / f"{STEM}_window_policy.json",
        c4_csv,
        c4_json,
    ]

    for threshold in ("2p0", "5p0", "10p0"):
        required_files.append(
            window_dir / f"{STEM}_windows_{threshold}.csv"
        )

    checks = []
    warnings = []

    missing = [
        str(path.relative_to(root))
        for path in required_files
        if not path.is_file()
    ]

    checks.append({
        "name": "Required artifacts exist",
        "status": "FAIL" if missing else "PASS",
        "details": missing,
    })

    if missing:
        return {
            "status": "FAIL",
            "checks": checks,
            "warnings": warnings,
        }

    try:
        policy = read_json(quality_policy)
        window_policy = read_json(
            window_dir / f"{STEM}_window_policy.json"
        )
        window_summary = read_json(
            window_dir / f"{STEM}_window_summary.json"
        )

        if not all(
            isinstance(item, dict)
            for item in (policy, window_policy)
        ):
            raise ValueError("Invalid policy JSON structure")

        if not isinstance(window_summary, (dict, list)):
            raise ValueError("Invalid window summary structure")

        c4_summary = read_json(c4_json)

        if c4_summary.get("experiment") != "M0.4-T05-C4":
            raise ValueError("Unexpected experiment identifier")

        if c4_summary.get("reference_windows") != 20:
            raise ValueError("Invalid reference window count")

        if c4_summary.get("source_recording") != raw.name:
            raise ValueError("Source recording mismatch")

        original_rows = read_csv(
            quality_csv,
            ("start_s", "end_s", "status", "reasons"),
        )

        degraded_rows = read_csv(
            c4_csv,
            ("scenario", "start_s", "end_s",
             "status", "reasons"),
        )

        scenarios = verify_quality_artifacts(
            original_rows,
            degraded_rows,
            c4_summary,
        )

        checks.append({
            "name": "C4 CSV/JSON and M0.3 baseline consistency",
            "status": "PASS",
        })

    except (ValueError, TypeError, KeyError, OSError,
            json.JSONDecodeError) as exc:
        checks.append({
            "name": "C4 CSV/JSON and M0.3 baseline consistency",
            "status": "FAIL",
            "details": str(exc),
        })
        scenarios = None

    evidence_dir = root / "docs/evidence/M0-04"

    missing_evidence = [
        filename
        for filename in EVIDENCE_FILES
        if not (evidence_dir / filename).is_file()
    ]

    if missing_evidence:
        warnings.append({
            "name": "Missing expected evidence screenshots",
            "files": missing_evidence,
        })

    hashes = {
        str(path.relative_to(root)): sha256_file(path)
        for path in (raw, quality_csv, c4_csv, c4_json)
    }

    return {
        "status": (
            "PASS"
            if all(c["status"] == "PASS" for c in checks)
            else "FAIL"
        ),
        "checks": checks,
        "warnings": warnings,
        "scenario_results": scenarios,
        "source_sha256": hashes,
        "scientific_validation": "NOT_ESTABLISHED",
    }
