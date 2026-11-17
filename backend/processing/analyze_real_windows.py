
import argparse
import csv
import hashlib
import json
import math
from collections import Counter
from pathlib import Path

from backend.processing.analyze_invalid_gaze import read_recording
from backend.processing.analyze_movement import (
    extract_gaze_samples,
    build_velocity_results,
)
from backend.processing.quality_window_integration import (
    load_quality_decisions,
    integrate_quality_windows,
    summarize_feature_availability,
)
from backend.processing.movement_segmentation import (
    validate_velocity_threshold,
)


def sha256_file(path):
    digest = hashlib.sha256()

    with Path(path).open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def validate_recording_identity(raw_path, window_path, quality_path):
    """
    Check that all three filenames refer to the same recording.

    This is an identifier consistency check, not proof that
    the files were generated from the same data.
    """
    stem = Path(raw_path).stem

    if Path(window_path).stem != stem + "_window_features":
        raise ValueError("Window features recording ID mismatch")

    if Path(quality_path).stem != stem + "_quality_decisions":
        raise ValueError("Quality decisions recording ID mismatch")

    return stem


def validate_window_alignment(window_csv, decisions):
    """
    Compare saved M0.3 window boundaries with quality decisions.

    Overlapping windows are allowed.
    Order and start/end boundaries must match.
    """
    with Path(window_csv).open(
        newline="", encoding="utf-8-sig"
    ) as file:
        reader = csv.DictReader(file)

        required = {"start_s", "end_s"}

        if reader.fieldnames is None:
            raise ValueError("Window feature CSV has no header")

        if len(reader.fieldnames) != len(set(reader.fieldnames)):
            raise ValueError("Duplicate window feature columns")

        if not required.issubset(reader.fieldnames):
            raise ValueError("Missing window boundary columns")

        windows = list(reader)

    if len(windows) != len(decisions):
        raise ValueError("Window and quality decision counts differ")

    for index, (window, decision) in enumerate(
        zip(windows, decisions)
    ):
        try:
            start = float(window["start_s"])
            end = float(window["end_s"])
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"Invalid window boundaries at row {index}"
            ) from exc

        if not (
            math.isfinite(start)
            and math.isfinite(end)
            and math.isclose(
                start, decision["start_s"],
                rel_tol=0,
                abs_tol=1e-6,
            )
            and math.isclose(
                end, decision["end_s"],
                rel_tol=0,
                abs_tol=1e-6,
            )
        ):
            raise ValueError(
                f"Window alignment mismatch at index {index}"
            )

    return len(windows)


def evaluate_real_windows(
    timestamps,
    velocity_results,
    decisions,
    thresholds,
):
    """
    Run window-level extraction for multiple thresholds.

    Original quality decisions remain unchanged.
    """
    if not thresholds:
        raise ValueError("At least one threshold is required")

    for threshold in thresholds:
        validate_velocity_threshold(threshold)

    if len(set(thresholds)) != len(thresholds):
        raise ValueError("Duplicate experimental thresholds")

    evaluations = []

    for threshold in thresholds:
        results = integrate_quality_windows(
            timestamps,
            velocity_results,
            decisions,
            threshold,
        )

        if len(results) != len(decisions):
            raise ValueError("Window count changed during processing")

        for decision, result in zip(decisions, results):
            if (
                result["start_s"] != decision["start_s"]
                or result["end_s"] != decision["end_s"]
                or result["quality_gate_status"]
                   != decision["quality_gate_status"]
                or result["quality_gate_reasons"]
                   != decision["quality_gate_reasons"]
            ):
                raise ValueError("Quality decision alignment changed")

            if decision["quality_gate_status"] == "UNKNOWN":
                if (
                    result["feature_status"] != "UNAVAILABLE"
                    or result["features"] is not None
                ):
                    raise ValueError(
                        "UNKNOWN quality window exposed features"
                    )

        evaluations.append({
            "threshold": threshold,
            "windows": results,
            "summary": summarize_feature_availability(results),
        })

    return evaluations


def export_results(output_dir, stem, evaluations, metadata):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    columns = [
        "start_s",
        "end_s",
        "threshold",
        "quality_gate_status",
        "quality_gate_reasons",
        "selected_interval_count",
        "feature_status",
        "feature_reason",
        "features_json",
    ]

    for evaluation in evaluations:
        label = str(evaluation["threshold"]).replace(".", "p")
        path = output_dir / f"{stem}_windows_{label}.csv"

        with path.open(
            "w", newline="", encoding="utf-8"
        ) as file:
            writer = csv.DictWriter(file, fieldnames=columns)
            writer.writeheader()

            for row in evaluation["windows"]:
                writer.writerow({
                    **{key: row[key] for key in columns[:-1]},
                    "features_json": (
                        json.dumps(row["features"])
                        if row["features"] is not None
                        else ""
                    ),
                })

    summary_path = output_dir / f"{stem}_window_summary.json"
    policy_path = output_dir / f"{stem}_window_policy.json"

    summaries = [
        {
            "threshold": item["threshold"],
            "summary": item["summary"],
        }
        for item in evaluations
    ]

    with summary_path.open("w", encoding="utf-8") as file:
        json.dump(summaries, file, indent=2)

    with policy_path.open("w", encoding="utf-8") as file:
        json.dump(metadata, file, indent=2)

    return summary_path, policy_path


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate real Tobii window-level features"
    )

    parser.add_argument("raw_csv", type=Path)
    parser.add_argument("window_csv", type=Path)
    parser.add_argument("quality_csv", type=Path)

    parser.add_argument(
        "--thresholds",
        type=float,
        nargs="+",
        required=True,
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/processed/window_oculomotor"),
    )

    args = parser.parse_args()

    for path in (
        args.raw_csv,
        args.window_csv,
        args.quality_csv,
    ):
        if not path.is_file():
            parser.error(f"Input file not found: {path}")

    stem = validate_recording_identity(
        args.raw_csv,
        args.window_csv,
        args.quality_csv,
    )

    decisions = load_quality_decisions(args.quality_csv)
    aligned_count = validate_window_alignment(
        args.window_csv,
        decisions,
    )

    raw_rows = read_recording(args.raw_csv)
    samples = extract_gaze_samples(raw_rows)

    timestamps = [
        sample["timestamp"] for sample in samples
    ]

    velocity_results = build_velocity_results(samples)

    if len(velocity_results) != max(0, len(samples) - 1):
        raise ValueError("Unexpected velocity interval count")

    evaluations = evaluate_real_windows(
        timestamps,
        velocity_results,
        decisions,
        args.thresholds,
    )

    quality_counts = Counter(
        row["quality_gate_status"]
        for row in decisions
    )

    print("\n--- CLOE Real Window Oculomotor Evaluation ---")
    print("Recording:", args.raw_csv.name)
    print("Gaze samples:", len(samples))
    print("Velocity intervals:", len(velocity_results))
    print("Aligned windows:", aligned_count)
    print("Quality ELIGIBLE:", quality_counts["ELIGIBLE"])
    print("Quality UNKNOWN:", quality_counts["UNKNOWN"])

    for evaluation in evaluations:
        summary = evaluation["summary"]
        statuses = summary["feature_status_counts"]

        print(f"\n--- Threshold {evaluation['threshold']} ---")
        print("Windows:", summary["window_count"])
        print("Feature AVAILABLE:", statuses.get("AVAILABLE", 0))
        print("Feature UNAVAILABLE:", statuses.get("UNAVAILABLE", 0))
        print("Reasons:", summary["unavailable_reasons"])

        print("\nWindow results:")
        for row in evaluation["windows"]:
            print(
                f'{row["start_s"]:.2f}-{row["end_s"]:.2f}s',
                "| Quality:", row["quality_gate_status"],
                "| Feature:", row["feature_status"],
                "| Intervals:", row["selected_interval_count"],
                "| Reason:", row["feature_reason"],
            )

    metadata = {
        "experiment": "M0.4-T04-C",
        "recording": args.raw_csv.name,
        "raw_sha256": sha256_file(args.raw_csv),
        "window_csv_sha256": sha256_file(args.window_csv),
        "quality_csv_sha256": sha256_file(args.quality_csv),
        "samples": len(samples),
        "velocity_intervals": len(velocity_results),
        "windows": aligned_count,
        "quality_counts": dict(quality_counts),
        "thresholds": args.thresholds,
        "nominal_hz": 60,
        "max_gap_ratio": 1.5,
        "alignment_method": "fully_contained_velocity_intervals",
        "velocity_unit": "normalized_display_units_per_second",
        "threshold_status": "illustrative_not_validated",
    }

    summary_path, policy_path = export_results(
        args.output_dir,
        stem,
        evaluations,
        metadata,
    )

    print("\nSummary saved:", summary_path)
    print("Policy saved:", policy_path)
    print("Window CSV files saved in:", args.output_dir)


if __name__ == "__main__":
    main()
