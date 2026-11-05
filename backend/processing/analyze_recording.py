import argparse
import csv
from pathlib import Path

from backend.processing.temporal_processing import analyze_timestamps


def load_timestamps(csv_path):
    timestamps = []

    with csv_path.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            timestamp = int(row["device_time_stamp"])
            timestamps.append(timestamp)

    return timestamps

def main():
    parser = argparse.ArgumentParser(description="Analyze timestamps from a CSV file.")
    parser.add_argument("csv_file", type=Path, help="Path to the CSV file containing timestamps.")
    
    args = parser.parse_args()
    csv_path = args.csv_file


    if not csv_path.is_file():
        parser.error(f"The file {csv_path} does not exist or is not a file.")

    timestamps = load_timestamps(csv_path)

    result = analyze_timestamps(
        timestamps,
        nominal_hz=60
    )

    print("\n--- CLOE Temporal Analysis ---")
    print("Recording:", csv_path.name)
    print("Samples:", len(timestamps))
    print(
        "Non-positive intervals:",
        result["non_positive_intervals"]
    )
    print("Large gaps:", len(result["large_gaps"]))
    print(
        "Estimated missing samples:",
        result["estimated_missing_samples"]
    )

    print("\n--- Individual Gaps ---")

    for gap in result["large_gaps"]:
        duration_ms = gap["duration_us"] / 1000

        print(
            f"Index: {gap['index']} | "
            f"Duration: {duration_ms:.3f} ms | "
            f"Estimated missing: {gap['estimated_missing']}"
        )


if __name__ == "__main__":
    main()