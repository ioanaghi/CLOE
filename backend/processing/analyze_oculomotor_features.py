
import argparse
import csv
import hashlib
import json
from pathlib import Path

from backend.processing.analyze_invalid_gaze import read_recording
from backend.processing.analyze_movement import (
    extract_gaze_samples,
    build_velocity_results,
)
from backend.processing.movement_segmentation import (
    segment_velocity_states,
    validate_velocity_threshold,
)
from backend.processing.segment_features import (
    calculate_segment_durations,
    calculate_segment_velocity_stats,
)
from backend.processing.movement_summary import (
    summarize_movement_segments,
)


SEGMENT_FIELDS = [
    "state",
    "start_interval_index",
    "end_interval_index",
    "interval_count",
    "start_timestamp_us",
    "end_timestamp_us",
    "duration_ms",
    "valid_velocity_count",
    "mean_velocity",
    "min_velocity",
    "max_velocity",
    "std_velocity",
]


def extract_features(samples, velocity_results, threshold):
    """
    Extract segment and recording-level features.

    All three T03 components operate sequentially.
    The original samples and velocity results are preserved.
    """

    validate_velocity_threshold(threshold)

    if len(velocity_results) != max(0, len(samples) - 1):
        raise ValueError(
            "Velocity interval count does not match sample count"
        )

    timestamps = [sample["timestamp"] for sample in samples]

    # T02 — Identify movement-state segments.
    segments = segment_velocity_states(
        velocity_results,
        threshold=threshold,
    )

    # T03-A — Calculate observed segment durations.
    with_durations = calculate_segment_durations(
        segments,
        timestamps,
    )

    # T03-B — Add descriptive velocity statistics.
    enriched_segments = calculate_segment_velocity_stats(
        with_durations,
        velocity_results,
    )

    # T03-C — Validate and summarize the full segmentation.
    summary = summarize_movement_segments(
        enriched_segments,
        total_intervals=len(velocity_results),
    )

    # Additional integration invariants.
    covered_intervals = sum(
        segment["interval_count"]
        for segment in enriched_segments
    )

    if covered_intervals != len(velocity_results):
        raise ValueError("Incomplete interval coverage")

    available = sum(
        result["velocity"] is not None
        for result in velocity_results
    )

    unknown = summary["interval_count_by_state"]["UNKNOWN"]

    if available + unknown != len(velocity_results):
        raise ValueError("Velocity availability mismatch")

    return {
        "threshold": threshold,
        "segments": enriched_segments,
        "summary": summary,
    }


def analyze_samples(samples, thresholds):
    """
    Calculate velocities once, then compare
    multiple explicitly configured thresholds.
    """

    if not thresholds:
        raise ValueError("At least one threshold is required")

    for threshold in thresholds:
        validate_velocity_threshold(threshold)

    if len(set(thresholds)) != len(thresholds):
        raise ValueError("Thresholds must be unique")

    velocity_results = build_velocity_results(samples)

    evaluations = [
        extract_features(samples, velocity_results, threshold)
        for threshold in thresholds
    ]

    return velocity_results, evaluations


def save_analysis(output_dir, stem, evaluations, metadata):
    """
    Export enriched segment CSVs, summary JSON,
    and experiment metadata.
    """

    output_dir.mkdir(parents=True, exist_ok=True)

    for evaluation in evaluations:
        threshold = evaluation["threshold"]
        label = str(threshold).replace(".", "p")

        path = output_dir / f"{stem}_features_{label}.csv"

        with path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=SEGMENT_FIELDS,
            )
            writer.writeheader()
            writer.writerows(evaluation["segments"])

    summary_path = output_dir / f"{stem}_oculomotor_summary.json"

    summaries = [
        {
            "threshold": evaluation["threshold"],
            "features": evaluation["summary"],
        }
        for evaluation in evaluations
    ]

    with summary_path.open("w", encoding="utf-8") as file:
        json.dump(summaries, file, indent=2)

    metadata_path = output_dir / f"{stem}_oculomotor_policy.json"

    with metadata_path.open("w", encoding="utf-8") as file:
        json.dump(metadata, file, indent=2)

    return summary_path, metadata_path


def file_sha256(path):
    """Calculate a digest without modifying the source file."""

    digest = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(
        description="Extract oculomotor features from Tobii recordings"
    )

    parser.add_argument("raw_csv", type=Path)
    parser.add_argument(
        "--thresholds",
        type=float,
        nargs="+",
        required=True,
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/processed/oculomotor"),
    )

    args = parser.parse_args()

    if not args.raw_csv.is_file():
        parser.error(f"Recording not found: {args.raw_csv}")

    # Read and process the original recording.
    rows = read_recording(args.raw_csv)
    samples = extract_gaze_samples(rows)

    velocity_results, evaluations = analyze_samples(
        samples,
        args.thresholds,
    )

    available_count = sum(
        result["velocity"] is not None
        for result in velocity_results
    )
    unknown_count = len(velocity_results) - available_count

    metadata = {
        "experiment": "M0.4-T03-D",
        "source_recording": args.raw_csv.name,
        "source_sha256": file_sha256(args.raw_csv),
        "sample_count": len(samples),
        "velocity_interval_count": len(velocity_results),
        "available_velocity_count": available_count,
        "unknown_velocity_count": unknown_count,
        "nominal_hz": 60,
        "max_gap_ratio": 1.5,
        "thresholds": args.thresholds,
        "velocity_unit": "normalized_display_units_per_second",
        "duration_unit": "milliseconds",
        "duration_method": "device_timestamp_difference",
        "threshold_status": "illustrative_not_validated",
    }

    print("\n--- CLOE Oculomotor Feature Extraction ---")
    print("Recording:", args.raw_csv.name)
    print("Gaze samples:", len(samples))
    print("Velocity intervals:", len(velocity_results))
    print("Available velocities:", available_count)
    print("UNKNOWN velocities:", unknown_count)

    for evaluation in evaluations:
        summary = evaluation["summary"]
        counts = summary["interval_count_by_state"]

        print(f"\n--- Threshold {evaluation['threshold']} ---")
        print("Segments:", summary["segment_count"])
        print("LOW intervals:", counts["LOW_VELOCITY"])
        print("HIGH intervals:", counts["HIGH_VELOCITY"])
        print("UNKNOWN intervals:", counts["UNKNOWN"])

        print("Total durations (ms):")
        for state, duration in (
            summary["total_duration_ms_by_state"].items()
        ):
            print(f"  {state}: {duration:.3f}")

        print("Transitions:", summary["transition_count"])
        print(
            "Direct LOW/HIGH transitions:",
            summary["direct_low_high_transitions"],
        )
        print(
            "Internal UNKNOWN runs:",
            summary["internal_unknown_runs"],
        )

    summary_path, metadata_path = save_analysis(
        args.output_dir,
        args.raw_csv.stem,
        evaluations,
        metadata,
    )

    print("\nSummary saved:", summary_path)
    print("Policy saved:", metadata_path)
    print("Segment CSV files saved in:", args.output_dir)


if __name__ == "__main__":
    main()
