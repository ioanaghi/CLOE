
import argparse
import csv
from pathlib import Path

from backend.processing.analyze_invalid_gaze import (
    read_recording,
    build_sources,
)
from backend.processing.window_features import (
    extract_window_features,
)


def main():
    parser = argparse.ArgumentParser(
        description="Extract sliding-window gaze quality features"
    )

    parser.add_argument(
        "csv_file",
        type=Path,
        help="Path to the raw Tobii CSV recording"
    )

    parser.add_argument(
        "--window-us",
        type=int,
        default=1_000_000
    )

    parser.add_argument(
        "--step-us",
        type=int,
        default=500_000
    )

    args = parser.parse_args()

    if not args.csv_file.is_file():
        parser.error(f"File not found: {args.csv_file}")

    # Step 1: Read the original recording
    rows = read_recording(args.csv_file)

    # Step 2: Build gaze source labels and timestamps
    sources, timestamps = build_sources(rows)

    # Step 3: Extract sliding-window features
    features = extract_window_features(
        timestamps,
        sources,
        window_us=args.window_us,
        step_us=args.step_us,
        nominal_hz=60,
    )

    # Step 4: Display results
    print("\n--- CLOE Sliding Window Feature Extraction ---")
    print("Recording:", args.csv_file.name)
    print("Input samples:", len(rows))
    print("Windows generated:", len(features))

    print("\n--- Window Results ---")

    for window in features:
        availability = window["gaze_availability_rate"]

        availability_text = (
            f"{availability:.2%}"
            if availability is not None
            else "UNKNOWN"
        )

        print(
            f"{window['start_s']:.2f}-"
            f"{window['end_s']:.2f}s | "
            f"Samples: {window['sample_count']} | "
            f"Availability: {availability_text} | "
            f"Invalid: {window['invalid_sample_count']} | "
            f"Gaps: {window['temporal_gap_count']}"
        )

    # Step 5: Save processed features separately
    output_path = (
        Path("data")
        / "processed"
        / f"{args.csv_file.stem}_window_features.csv"
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    if features:
        with output_path.open(
            "w",
            newline="",
            encoding="utf-8"
        ) as file:
            writer = csv.DictWriter(
                file,
                fieldnames=list(features[0].keys())
            )

            writer.writeheader()
            writer.writerows(features)

        print("\nFeatures saved to:", output_path)
    else:
        print("\nNo feature windows generated.")


if __name__ == "__main__":
    main()
