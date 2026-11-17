
import argparse
import json
from pathlib import Path

from backend.processing.data_degradation import (
    read_recording,
    write_recording,
    invalidate_gaze_samples,
    drop_samples,
    summarize_degradation,
    sha256_file,
    save_manifest,
)


def main():
    parser = argparse.ArgumentParser(
        description="CLOE controlled gaze data degradation"
    )

    parser.add_argument("raw_csv", type=Path)

    parser.add_argument(
        "--start-index",
        type=int,
        default=200,
    )

    parser.add_argument(
        "--count",
        type=int,
        default=30,
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/processed/degradation"),
    )

    args = parser.parse_args()

    if args.start_index < 0 or args.count <= 0:
        parser.error("Invalid selected sample range")

    fieldnames, original = read_recording(args.raw_csv)

    end_index = args.start_index + args.count

    if end_index > len(original):
        parser.error("Selected range exceeds recording size")

    indices = list(range(args.start_index, end_index))
    stem = args.raw_csv.stem

    scenarios = {
        "INVALID_GAZE": invalidate_gaze_samples(
            original, indices
        ),
        "DROPPED_SAMPLES": drop_samples(
            original, indices
        ),
    }

    manifest = {
        "experiment": "M0.4-T05-C",
        "source_file": args.raw_csv.name,
        "source_sha256": sha256_file(args.raw_csv),
        "start_index": args.start_index,
        "count": args.count,
        "scenarios": {},
    }

    print("\n--- CLOE Controlled Data Degradation ---")
    print("Source:", args.raw_csv.name)
    print("Original samples:", len(original))
    print("Selected indices:", args.start_index, "-", end_index - 1)

    for scenario, modified in scenarios.items():
        filename = (
            f"{stem}_degraded_{scenario.lower()}.csv"
        )

        output_path = args.output_dir / filename

        write_recording(
            output_path, fieldnames, modified
        )

        # Independent read-back of saved data
        _, saved_rows = read_recording(output_path)

        if saved_rows != modified:
            raise ValueError(
                f"{scenario}: exported data mismatch"
            )

        report = summarize_degradation(
            original,
            saved_rows,
            scenario,
            indices,
        )

        manifest["scenarios"][scenario] = {
            **report,
            "output_file": filename,
            "output_sha256": sha256_file(output_path),
        }

        print(f"\n--- {scenario} ---")
        print("Original samples:", report["original_samples"])
        print("Modified samples:", report["modified_samples"])

        print(
            "Invalid both:",
            report["original_invalid_both"],
            "->",
            report["modified_invalid_both"],
        )

        print(
            "Large gaps:",
            report["original_large_gaps"],
            "->",
            report["modified_large_gaps"],
        )

        print("CSV:", output_path)
        print("Read-back: PASS")

    manifest_path = (
        args.output_dir /
        f"{stem}_degradation_manifest.json"
    )

    save_manifest(manifest_path, manifest)

    print("\nManifest:", manifest_path)
    print("Result: PASS — Degraded copies generated")


if __name__ == "__main__":
    main()
