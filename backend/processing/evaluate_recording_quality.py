
import argparse
import csv
import json
from collections import Counter
from pathlib import Path

from backend.processing.analyze_invalid_gaze import read_recording
from backend.processing.data_quality import assess_window_quality
from backend.processing.quality_gate import (
    QualityPolicy,
    evaluate_quality,
)
from backend.processing.recording_boundaries import (
    is_within_recording_bounds,
)


REQUIRED_FEATURES = {
    "start_s",
    "end_s",
    "sample_count",
    "invalid_sample_count",
    "gaze_availability_rate",
}


def load_feature_windows(path):
    with path.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        if not REQUIRED_FEATURES.issubset(reader.fieldnames or []):
            raise ValueError("Missing required feature columns")

        windows = []

        for row in reader:
            windows.append({
                "start_s": float(row["start_s"]),
                "end_s": float(row["end_s"]),
                "sample_count": int(row["sample_count"]),
                "invalid_sample_count": int(
                    row["invalid_sample_count"]
                ),
                "gaze_availability_rate": (
                    float(row["gaze_availability_rate"])
                    if row["gaze_availability_rate"].strip()
                    else None
                ),
            })

        return windows


def recording_duration_seconds(path):
    rows = read_recording(path)

    if not rows:
        raise ValueError("Raw recording contains no samples")

    timestamps = [
        int(row["device_time_stamp"])
        for row in rows
    ]

    if any(
        timestamps[i] <= timestamps[i - 1]
        for i in range(1, len(timestamps))
    ):
        raise ValueError("Raw timestamps must be increasing")

    return (timestamps[-1] - timestamps[0]) / 1_000_000


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate real gaze feature windows"
    )

    parser.add_argument("raw_csv", type=Path)
    parser.add_argument("features_csv", type=Path)

    # Explicit experimental policy parameters
    parser.add_argument(
        "--min-availability", type=float, required=True
    )
    parser.add_argument(
        "--min-nominal-ratio", type=float, required=True
    )
    parser.add_argument(
        "--min-usable-ratio", type=float, required=True
    )

    args = parser.parse_args()

    for path in (args.raw_csv, args.features_csv):
        if not path.is_file():
            parser.error(f"File not found: {path}")

    policy = QualityPolicy(
        min_gaze_availability=args.min_availability,
        min_nominal_sample_ratio=args.min_nominal_ratio,
        min_usable_nominal_ratio=args.min_usable_ratio,
        require_complete_window=True,
    )

    duration_s = recording_duration_seconds(args.raw_csv)
    windows = load_feature_windows(args.features_csv)

    decisions = []

    for window in windows:
        quality = assess_window_quality(
            window,
            nominal_hz=60,
        )

        within_bounds = is_within_recording_bounds(
            window["start_s"],
            window["end_s"],
            duration_s,
        )

        # Boundary-based proxy, not proof of continuous acquisition
        decision = evaluate_quality(
            quality,
            policy,
            window_complete=within_bounds,
        )

        decisions.append({
            "start_s": window["start_s"],
            "end_s": window["end_s"],
            "sample_count": quality["sample_count"],
            "gaze_availability_rate": (
                quality["gaze_availability_rate"]
            ),
            "nominal_sample_ratio": (
                quality["nominal_sample_ratio"]
            ),
            "usable_nominal_ratio": (
                quality["usable_nominal_ratio"]
            ),
            "within_recording_bounds": within_bounds,
            "status": decision["status"],
            "reasons": "|".join(decision["reasons"]),
        })

    counts = Counter(row["status"] for row in decisions)

    print("\n--- CLOE Real Data Quality Evaluation ---")
    print("Raw recording:", args.raw_csv.name)
    print("Feature file:", args.features_csv.name)
    print(f"Observed recording span: {duration_s:.3f} s")
    print("Windows evaluated:", len(decisions))
    print("ELIGIBLE:", counts["ELIGIBLE"])
    print("UNKNOWN:", counts["UNKNOWN"])

    print("\n--- Window Decisions ---")

    for row in decisions:
        print(
            f"{row['start_s']:.2f}-{row['end_s']:.2f}s | "
            f"{row['status']} | "
            f"{row['reasons'] or 'No rejection reasons'}"
        )

    output_path = (
        Path("data")
        / "processed"
        / f"{args.raw_csv.stem}_quality_decisions.csv"
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if decisions:
        with output_path.open(
            "w", newline="", encoding="utf-8"
        ) as file:
            writer = csv.DictWriter(
                file,
                fieldnames=list(decisions[0].keys()),
            )
            writer.writeheader()
            writer.writerows(decisions)

    # Persist the explicit experimental policy.
    policy_path = output_path.with_suffix(".policy.json")

    with policy_path.open("w", encoding="utf-8") as file:
        json.dump({
            "experiment": "M0.3-T05-C",
            "raw_recording": args.raw_csv.name,
            "feature_file": args.features_csv.name,
            "nominal_hz": 60,
            "min_gaze_availability": args.min_availability,
            "min_nominal_sample_ratio": args.min_nominal_ratio,
            "min_usable_nominal_ratio": args.min_usable_ratio,
            "require_complete_window": True,
            "completeness_method": "observed_timestamp_bounds_proxy",
        }, file, indent=2)

    print("\nDecisions saved to:", output_path)
    print("Policy saved to:", policy_path)


if __name__ == "__main__":
    main()
