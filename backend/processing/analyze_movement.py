
import argparse
import csv
import json
from collections import Counter
from pathlib import Path

from backend.processing.analyze_invalid_gaze import read_recording
from backend.processing.gaze_processing import combine_gaze
from backend.processing.gaze_velocity import calculate_gaze_velocity
from backend.processing.movement_segmentation import (
    classify_velocity,
    segment_velocity_states,
)


def extract_gaze_samples(rows):
    """Preserve every raw row and its original order."""
    samples = []

    for row in rows:
        left = (
            float(row["left_gaze_point_on_display_area_0"]),
            float(row["left_gaze_point_on_display_area_1"]),
        )

        right = (
            float(row["right_gaze_point_on_display_area_0"]),
            float(row["right_gaze_point_on_display_area_1"]),
        )

        point, source = combine_gaze(
            left,
            right,
            int(row["left_gaze_point_validity"]),
            int(row["right_gaze_point_validity"]),
        )

        samples.append({
            "timestamp": int(row["device_time_stamp"]),
            "point": point,
            "source": source,
        })

    return samples


def build_velocity_results(samples):
    """Calculate one velocity result per consecutive pair."""
    results = []

    for index in range(len(samples) - 1):
        first = samples[index]
        second = samples[index + 1]

        result = calculate_gaze_velocity(
            first["point"],
            second["point"],
            first["timestamp"],
            second["timestamp"],
            nominal_hz=60,
            max_gap_ratio=1.5,
        )

        results.append({
            "interval_index": index,
            "velocity": result["velocity"],
            "reason": result["reason"],
        })

    return results


def evaluate_threshold(velocity_results, threshold):
    """Summarize movement states for one experimental threshold."""
    segments = segment_velocity_states(
        velocity_results,
        threshold=threshold,
    )

    states = [
        classify_velocity(result["velocity"], threshold)
        for result in velocity_results
    ]

    state_counts = Counter(states)
    segment_counts = Counter(
        segment["state"] for segment in segments
    )

    return {
        "threshold": threshold,
        "states": states,
        "segments": segments,
        "state_counts": state_counts,
        "segment_counts": segment_counts,
    }


def save_results(output_dir, stem, velocity_results, evaluations):
    output_dir.mkdir(parents=True, exist_ok=True)

    intervals_path = output_dir / f"{stem}_velocity_intervals.csv"

    with intervals_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["interval_index", "velocity", "reason"],
        )
        writer.writeheader()
        writer.writerows(velocity_results)

    for evaluation in evaluations:
        threshold = evaluation["threshold"]
        threshold_label = str(threshold).replace(".", "p")

        segment_path = (
            output_dir / f"{stem}_segments_threshold_{threshold_label}.csv"
        )

        with segment_path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=[
                    "state",
                    "start_interval_index",
                    "end_interval_index",
                    "interval_count",
                ],
            )
            writer.writeheader()
            writer.writerows(evaluation["segments"])

    metadata_path = output_dir / f"{stem}_movement_policy.json"

    with metadata_path.open("w", encoding="utf-8") as file:
        json.dump({
            "experiment": "M0.4-T02-C",
            "recording": stem,
            "nominal_hz": 60,
            "max_gap_ratio": 1.5,
            "thresholds": [
                evaluation["threshold"]
                for evaluation in evaluations
            ],
            "velocity_unit": "normalized_display_units_per_second",
        }, file, indent=2)

    return intervals_path, metadata_path


def main():
    parser = argparse.ArgumentParser(
        description="Analyze gaze movement states in a Tobii CSV"
    )
    parser.add_argument("csv_file", type=Path)
    parser.add_argument(
        "--thresholds",
        type=float,
        nargs="+",
        required=True,
    )

    args = parser.parse_args()

    if not args.csv_file.is_file():
        parser.error(f"Recording not found: {args.csv_file}")

    rows = read_recording(args.csv_file)
    samples = extract_gaze_samples(rows)
    velocity_results = build_velocity_results(samples)

    evaluations = [
        evaluate_threshold(velocity_results, threshold)
        for threshold in args.thresholds
    ]

    reasons = Counter(
        result["reason"]
        for result in velocity_results
        if result["reason"] is not None
    )

    valid_count = sum(
        result["velocity"] is not None
        for result in velocity_results
    )

    print("\n--- CLOE Movement Analysis ---")
    print("Recording:", args.csv_file.name)
    print("Gaze samples:", len(samples))
    print("Velocity intervals:", len(velocity_results))
    print("Available velocities:", valid_count)
    print("Unknown velocities:", len(velocity_results) - valid_count)

    print("\n--- Unavailable Velocity Reasons ---")
    for reason, count in sorted(reasons.items()):
        print(f"{reason}: {count}")

    for evaluation in evaluations:
        print(f"\n--- Threshold: {evaluation['threshold']} ---")

        for state in ("LOW_VELOCITY", "HIGH_VELOCITY", "UNKNOWN"):
            print(
                f"{state}: "
                f"{evaluation['state_counts'][state]} intervals, "
                f"{evaluation['segment_counts'][state]} segments"
            )

        print("Total segments:", len(evaluation["segments"]))

    output_dir = Path("data") / "processed" / "movement"

    intervals_path, metadata_path = save_results(
        output_dir,
        args.csv_file.stem,
        velocity_results,
        evaluations,
    )

    print("\nVelocity intervals saved to:", intervals_path)
    print("Movement policy saved to:", metadata_path)
    print("Segment CSV files saved to:", output_dir)


if __name__ == "__main__":
    main()
