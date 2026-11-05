import argparse
import csv
from collections import Counter
from pathlib import Path


from backend.processing.gaze_processing import combine_gaze
from backend.processing.invalid_gaze_processing import detect_invalid_runs


REQUIRED_COLUMNS = [
    "left_gaze_point_on_display_area_0",
    "left_gaze_point_on_display_area_1",
    "left_gaze_point_validity",
    "right_gaze_point_on_display_area_0",
    "right_gaze_point_on_display_area_1",
    "right_gaze_point_validity",
    "device_time_stamp",
]

def read_recording(csv_path):
   with csv_path.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError("CSV file has no header row.")

        missing =[
            name for name in REQUIRED_COLUMNS 
            if name not in reader.fieldnames
        ]

        if missing:
            raise ValueError(
                f"Missing CSV columns: {missing}\n"
                f"Available columns: {reader.fieldnames}"
            )
        
        return list(reader)


def build_sources(rows):
    sources = []
    timestamps = []

    for row in rows:
        left =(
            float(row["left_gaze_point_on_display_area_0"]),
            float(row["left_gaze_point_on_display_area_1"])
        )

        right =(
            
            float(row["right_gaze_point_on_display_area_0"]),
            float(row["right_gaze_point_on_display_area_1"])
        )

        left_valid = int(row["left_gaze_point_validity"])
        right_valid = int(row["right_gaze_point_validity"])

        _, source = combine_gaze(left, right, left_valid, right_valid)

        sources.append(source)
        timestamps.append(int(row["device_time_stamp"]))

    return sources, timestamps



def main():
    parser = argparse.ArgumentParser(
        description="Analyze invalid gaze runs in a Tobii CSV"
    )

    parser.add_argument("csv_file", type=Path)
    args = parser.parse_args()

    if not args.csv_file.is_file():
        parser.error(f"File not found: {args.csv_file}")

    rows = read_recording(args.csv_file)
    sources, timestamps = build_sources(rows)

    counts = Counter(sources)
    runs = detect_invalid_runs(sources)

    total = len(sources)
    invalid_total = counts["NONE"]

    print("\n--- CLOE Invalid Gaze Analysis ---")
    print("Recording:", args.csv_file.name)
    print("Total samples:", total)

    print("\n--- Source Distribution ---")
    for label in ("BOTH", "LEFT", "RIGHT", "NONE"):
        count = counts[label]
        percentage = 100 * count / total if total else 0
        print(f"{label}: {count} ({percentage:.2f}%)")

    print("\n--- Invalid Runs ---")
    print("Invalid samples:", invalid_total)
    print("Number of runs:", len(runs))

    longest = max(
        (run["sample_count"] for run in runs),
        default=0
    )
    print("Longest run (samples):", longest)

    for run in runs:
        start = run["start_index"]
        end = run["end_index"]

        # Observed span between first and last invalid sample.
        span_ms = (
            timestamps[end] - timestamps[start]
        ) / 1000

        print(
            f"Start: {start} | "
            f"End: {end} | "
            f"Samples: {run['sample_count']} | "
            f"Observed span: {span_ms:.3f} ms"
        )


if __name__ == "__main__":
    main()   