
import argparse
import csv
import math
from pathlib import Path


REQUIRED_COLUMNS = [
    "device_time_stamp",
    "system_time_stamp",
    "left_gaze_point_validity",
    "right_gaze_point_validity",
    "left_gaze_point_on_display_area_0",
    "left_gaze_point_on_display_area_1",
    "right_gaze_point_on_display_area_0",
    "right_gaze_point_on_display_area_1",
]

NOMINAL_INTERVAL_US = 1_000_000 / 60


def validate_csv(file_path, expected_rows=None):
    errors = []
    warnings = []
    timestamps = []
    row_count = 0
    invalid_left = 0
    invalid_right = 0
    nan_coordinates = 0

    with file_path.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        headers = reader.fieldnames or []

        missing = [
            name for name in REQUIRED_COLUMNS
            if name not in headers
        ]

        if missing:
            print("Missing columns:", missing)
            return False

        if len(headers) != len(set(headers)):
            print("FAIL: Duplicate column names.")
            return False

        for row_number, row in enumerate(reader, start=2):
            row_count += 1

            if None in row or any(v is None for v in row.values()):
                errors.append(f"Row {row_number}: Incorrect column count")
                continue

            try:
                timestamp = int(row["device_time_stamp"])
                int(row["system_time_stamp"])

                left_valid = int(row["left_gaze_point_validity"])
                right_valid = int(row["right_gaze_point_validity"])

                if left_valid not in (0, 1) or right_valid not in (0, 1):
                    raise ValueError("Invalid validity flag")

                left = (
                    float(row["left_gaze_point_on_display_area_0"]),
                    float(row["left_gaze_point_on_display_area_1"])
                )

                right = (
                    float(row["right_gaze_point_on_display_area_0"]),
                    float(row["right_gaze_point_on_display_area_1"])
                )

            except (ValueError, TypeError) as exc:
                errors.append(f"Row {row_number}: {exc}")
                continue

            timestamps.append(timestamp)

            if left_valid == 0:
                invalid_left += 1
            elif not all(math.isfinite(v) for v in left):
                errors.append(f"Row {row_number}: Valid left gaze has NaN/Inf")

            if right_valid == 0:
                invalid_right += 1
            elif not all(math.isfinite(v) for v in right):
                errors.append(f"Row {row_number}: Valid right gaze has NaN/Inf")

            nan_coordinates += sum(
                math.isnan(v) for v in (*left, *right)
            )

    if row_count == 0:
        errors.append("CSV contains no data rows")

    if expected_rows is not None and row_count != expected_rows:
        errors.append(
            f"Expected {expected_rows} rows, found {row_count}"
        )

    intervals = [
        current - previous
        for previous, current in zip(timestamps, timestamps[1:])
    ]

    non_positive = sum(dt <= 0 for dt in intervals)
    large_gaps = sum(dt > 1.5 * NOMINAL_INTERVAL_US for dt in intervals)

    if non_positive:
        errors.append(f"{non_positive} non-positive timestamp intervals")

    if large_gaps:
        warnings.append(f"{large_gaps} intervals exceed 1.5x nominal")

    print("\n--- CSV Integrity Report ---")
    print("File:", file_path.name)
    print("Rows:", row_count)
    print("Columns:", len(headers))
    print("Invalid left gaze:", invalid_left)
    print("Invalid right gaze:", invalid_right)
    print("NaN coordinate values:", nan_coordinates)
    print("Non-positive intervals:", non_positive)
    print("Large timestamp gaps:", large_gaps)

    for message in warnings:
        print("WARNING:", message)

    for message in errors[:10]:
        print("ERROR:", message)

    if len(errors) > 10:
        print(f"... and {len(errors) - 10} additional errors")

    status = "FAIL" if errors else "PASS"
    print("Final result:", status)

    return not errors


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Validate a CLOE Tobii gaze CSV file"
    )

    parser.add_argument("file", type=Path)
    parser.add_argument("--expected-rows", type=int, default=None)

    args = parser.parse_args()

    if not args.file.is_file():
        parser.error("CSV file does not exist")

    valid = validate_csv(args.file, args.expected_rows)
    raise SystemExit(0 if valid else 1)
