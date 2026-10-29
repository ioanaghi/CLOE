import csv
import time
from datetime import datetime,timezone
from pathlib import Path

import tobii_research as tr

DURATION_SECONDS =10

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "data"/"raw"/"tobii"

samples =[]


def on_gaze_data(gaze_data):
    samples.append(gaze_data)

trackers = tr.find_all_eyetrackers()

if not trackers:
    raise RuntimeError("No eye trackers found.")

tracker = trackers[0]

print("Tracker:", tracker.model)
print("Frequency:", tracker.get_gaze_output_frequency(), "Hz")

print(f"Recording for {DURATION_SECONDS} seconds...")

tracker.subscribe_to(
    tr.EYETRACKER_GAZE_DATA,
    on_gaze_data,
    as_dictionary=True
)

try:
    time.sleep(DURATION_SECONDS)
finally:
    tracker.unsubscribe_from(
        tr.EYETRACKER_GAZE_DATA,
        on_gaze_data
    )

print("Samples collected:", len(samples))


def flatten_sample(sample):
    row={}

    for key, value in sample.items():
        if isinstance(value,(tuple,list)):
            for index, coordinate in enumerate(value):
                row[f"{key}_{index}"]=coordinate
        else:
            row[key]=value

    return row


if samples:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    recorded_at = datetime.now(timezone.utc)
    timestamp = recorded_at.strftime("%Y%m%dT%H%M%S%fZ")
    output_path = OUTPUT_DIR / f"tobii_{timestamp}.csv"

    rows = [flatten_sample(sample) for sample in samples]
    fieldnames = list(rows[0].keys())

    with output_path.open("x", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    with output_path.open("r", newline="", encoding="utf-8") as file:
        saved_rows = sum(1 for _ in csv.DictReader(file))
    
    print("CSV saved: ", output_path)
    print("Rows saved: ", saved_rows)
    print("Verification:", "PASS" if saved_rows == len(samples) else "FAIL")

else:
    print("No samples recieved. CSV not created.")