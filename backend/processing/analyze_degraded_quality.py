
import argparse
import csv
import json
import math
from collections import Counter
from pathlib import Path
from types import SimpleNamespace

from backend.processing.combine_gaze import is_valid_eye
from backend.processing.window_features import extract_window_features
from backend.processing.degradation_quality_evaluation import (
    evaluate_degraded_windows,
    compare_quality_decisions,
)


DEFAULT_STEM = "tobii_20261029T143930551761Z"


def load_recording(path):
    """Load raw gaze samples without changing the source file."""
    with Path(path).open(
        newline="", encoding="utf-8-sig"
    ) as file:
        rows = list(csv.DictReader(file))

    if not rows:
        raise ValueError("Empty Tobii recording")

    timestamps = []
    sources = []

    for index, row in enumerate(rows):
        timestamp = int(row["device_time_stamp"])

        if timestamps and timestamp <= timestamps[-1]:
            raise ValueError(
                f"Non-increasing timestamp at row {index}"
            )

        left = (
            float(row["left_gaze_point_on_display_area_0"]),
            float(row["left_gaze_point_on_display_area_1"]),
        )
        right = (
            float(row["right_gaze_point_on_display_area_0"]),
            float(row["right_gaze_point_on_display_area_1"]),
        )

        left_valid = is_valid_eye(
            left,
            int(row["left_gaze_point_validity"]),
        )
        right_valid = is_valid_eye(
            right,
            int(row["right_gaze_point_validity"]),
        )

        if left_valid and right_valid:
            source = "BOTH"
        elif left_valid:
            source = "LEFT"
        elif right_valid:
            source = "RIGHT"
        else:
            source = "NONE"

        timestamps.append(timestamp)
        sources.append(source)

    return timestamps, sources


def load_original_quality(path):
    """Read the original M0.3 decisions as reference evidence."""
    with Path(path).open(
        newline="", encoding="utf-8-sig"
    ) as file:
        rows = list(csv.DictReader(file))

    required = {"start_s", "end_s", "status", "reasons"}

    if not rows or not required.issubset(rows[0]):
        raise ValueError("Invalid original Quality Gate CSV")

    return [
        {
            "start_s": float(row["start_s"]),
            "end_s": float(row["end_s"]),
            "status": row["status"],
            "reasons": [
                value for value in row["reasons"].split("|")
                if value
            ],
        }
        for row in rows
    ]


def load_policy(path):
    """Reuse the exact saved M0.3 experimental policy."""
    with Path(path).open(encoding="utf-8") as file:
        data = json.load(file)

    keys = (
        "min_gaze_availability",
        "min_nominal_sample_ratio",
        "min_usable_nominal_ratio",
        "require_complete_window",
    )

    if any(key not in data for key in keys):
        raise ValueError("Incomplete M0.3 policy JSON")

    return SimpleNamespace(
        **{key: data[key] for key in keys}
    )


def check_baseline(recomputed, original):
    """Fail if the original M0.3 outcomes are not reproduced."""
    if len(recomputed) != len(original):
        raise ValueError("Baseline window count mismatch")

    for index, (actual, expected) in enumerate(
        zip(recomputed, original)
    ):
        if not (
            math.isclose(
                actual["start_s"], expected["start_s"],
                rel_tol=0, abs_tol=1e-6
            )
            and math.isclose(
                actual["end_s"], expected["end_s"],
                rel_tol=0, abs_tol=1e-6
            )
        ):
            raise ValueError(
                f"Baseline window {index}: boundary mismatch"
            )

        if actual["status"] != expected["status"]:
            raise ValueError(
                f"Baseline window {index}: status mismatch "
                f"({actual['status']} vs {expected['status']})"
            )

        if set(actual["reasons"]) != set(expected["reasons"]):
            raise ValueError(
                f"Baseline window {index}: reasons mismatch "
                f"({actual['reasons']} vs {expected['reasons']})"
            )


def make_scenarios(timestamps, sources):
    """Create deterministic, non-destructive perturbations."""
    invalid_sources = list(sources)

    for index in (100, 101, 102):
        invalid_sources[index] = "NONE"

    small_drop = {100, 101, 102}

    periodic_drop = set(
        range(10, len(timestamps) - 1, 10)
    )

    def drop(indices):
        return (
            [
                timestamp
                for index, timestamp in enumerate(timestamps)
                if index not in indices
            ],
            [
                source
                for index, source in enumerate(sources)
                if index not in indices
            ],
        )

    return {
        "BASELINE": (
            list(timestamps), list(sources), 0
        ),
        "INVALID_3": (
            list(timestamps), invalid_sources, 3
        ),
        "DROPOUT_3": (
            *drop(small_drop), len(small_drop)
        ),
        "DROPOUT_10_PERCENT": (
            *drop(periodic_drop), len(periodic_drop)
        ),
    }


def save_reports(output_dir, reports, metadata):
    """Export derived results without touching original data."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    csv_path = output_dir / "t05_c4_quality_decisions.csv"
    json_path = output_dir / "t05_c4_quality_summary.json"

    fields = [
        "scenario",
        "start_s",
        "end_s",
        "sample_count",
        "invalid_sample_count",
        "gaze_availability_rate",
        "nominal_sample_ratio",
        "usable_nominal_ratio",
        "window_complete",
        "status",
        "reasons",
    ]

    with csv_path.open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()

        for scenario, rows in reports.items():
            for row in rows:
                writer.writerow({
                    **row,
                    "scenario": scenario,
                    "reasons": "|".join(row["reasons"]),
                })

    with json_path.open(
        "w", encoding="utf-8"
    ) as file:
        json.dump(metadata, file, indent=2)

    return csv_path, json_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--stem", default=DEFAULT_STEM
    )
    parser.add_argument(
        "--output-dir",
        default="data/processed/degradation",
    )
    args = parser.parse_args()

    stem = args.stem

    raw_path = Path("data/raw/tobii") / f"{stem}.csv"
    quality_path = Path("data/processed") / (
        f"{stem}_quality_decisions.csv"
    )
    policy_path = Path("data/processed") / (
        f"{stem}_quality_decisions.policy.json"
    )

    timestamps, sources = load_recording(raw_path)
    original_decisions = load_original_quality(quality_path)
    policy = load_policy(policy_path)

    original_start = timestamps[0]
    recording_duration = (
        timestamps[-1] - original_start
    ) / 1_000_000

    reference_windows = extract_window_features(
        timestamps, sources,
        nominal_hz=60,
    )

    scenarios = make_scenarios(timestamps, sources)

    reports = {}
    summaries = {}

    print("\n--- CLOE T05-C4 Quality Gate Re-evaluation ---")
    print("Original samples:", len(timestamps))
    print("Reference windows:", len(reference_windows))

    for name, (
        scenario_timestamps,
        scenario_sources,
        modified_count,
    ) in scenarios.items():

        results = evaluate_degraded_windows(
            scenario_timestamps,
            scenario_sources,
            reference_windows,
            recording_duration,
            policy,
            nominal_hz=60,
            reference_start_timestamp=original_start,
        )

        if name == "BASELINE":
            check_baseline(
                results,
                original_decisions,
            )
            print("\nBaseline M0.3 reproduction: PASS")

        reports[name] = results
        counts = Counter(
            row["status"] for row in results
        )

        summaries[name] = {
            "modified_samples": modified_count,
            "received_samples": len(scenario_timestamps),
            "windows": len(results),
            "eligible": counts["ELIGIBLE"],
            "unknown": counts["UNKNOWN"],
        }

        print(f"\n--- {name} ---")
        print("Modified samples:", modified_count)
        print("Received samples:", len(scenario_timestamps))
        print("Windows:", len(results))
        print("ELIGIBLE:", counts["ELIGIBLE"])
        print("UNKNOWN:", counts["UNKNOWN"])

        for row in results:
            if row["status"] == "UNKNOWN":
                print(
                    f'  {row["start_s"]:.2f}-'
                    f'{row["end_s"]:.2f}s | '
                    + "|".join(row["reasons"])
                )

    baseline = reports["BASELINE"]

    for name in (
        "INVALID_3",
        "DROPOUT_3",
        "DROPOUT_10_PERCENT",
    ):
        comparison = compare_quality_decisions(
            baseline,
            reports[name],
        )

        summaries[name]["newly_rejected"] = (
            comparison["newly_rejected"]
        )
        summaries[name]["recovered"] = (
            comparison["recovered"]
        )

        print(f"\n--- Comparison: {name} ---")
        print(
            "Newly rejected:",
            len(comparison["newly_rejected"])
        )
        print(
            "Recovered:",
            len(comparison["recovered"])
        )

        for item in comparison["newly_rejected"]:
            print(
                f'  NEW UNKNOWN: '
                f'{item["start_s"]:.2f}-'
                f'{item["end_s"]:.2f}s | '
                + "|".join(item["reasons"])
            )

    csv_path, json_path = save_reports(
        args.output_dir,
        reports,
        {
            "experiment": "M0.4-T05-C4",
            "source_recording": raw_path.name,
            "original_start_timestamp": original_start,
            "recording_duration_s": recording_duration,
            "reference_windows": len(reference_windows),
            "policy": vars(policy),
            "scenarios": summaries,
        },
    )

    print("\nDecisions CSV:", csv_path)
    print("Summary JSON:", json_path)
    print("Result: PASS")


if __name__ == "__main__":
    main()
