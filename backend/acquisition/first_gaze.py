import time
import tobii_research as tr

samples= []

def gaze_callback(gaze_data):
    samples.append(gaze_data)


trackers = tr.find_all_eyetrackers()

if not trackers:
    raise RuntimeError("No eye trackers found.")

tracker = trackers[0]

tracker.subscribe_to(
    tr.EYETRACKER_GAZE_DATA,
    gaze_callback,
    as_dictionary=True
)

try:
    time.sleep(10)  # Collect gaze data for 10 seconds
finally:
    tracker.unsubscribe_from(
        tr.EYETRACKER_GAZE_DATA, 
        gaze_callback
    )

print("Acquisition finished.")
print("Samples collected:", len(samples))


total_samples = len(samples)

left_valid=0
right_valid=0
both_valid=0
either_valid=0

for sample in samples:
    left_ok = sample["left_gaze_point_validity"] == 1
    right_ok = sample["right_gaze_point_validity"] == 1

    if left_ok:
        left_valid += 1
    
    if right_ok:
        right_valid += 1

    if left_ok and right_ok:
        both_valid += 1
    
    if left_ok or right_ok:
        either_valid += 1

if total_samples > 0:
    print("Gaze data validity statistics:")
    print(f"Total samples: {total_samples}")
    print(f"Left valid: {left_valid / total_samples * 100:.2f}%")
    print(f"Right valid: {right_valid / total_samples * 100:.2f}%")
    print(f"Both valid: {both_valid / total_samples * 100:.2f}%")
    print(f"Either valid: {either_valid / total_samples * 100:.2f}%")
else:
    print("No samples collected.")


if len(samples) >=2:
    timestamps = [sample["device_time_stamp"] for sample in samples]

    intervals_ms = []

    for i in range(1, len(timestamps)):
        difference = timestamps[i] - timestamps[i - 1]

        if difference> 0:
            intervals_ms.append(difference / 1000)  # Convert microseconds to milliseconds

        
    if intervals_ms:

        mean_interval = sum(intervals_ms) / len(intervals_ms)

        duration_seconds = (timestamps[-1] - timestamps[0]) / 1_000_000  # Convert microseconds to seconds

        observed_frequency =(
            (len(timestamps) - 1) /duration_seconds

            if duration_seconds > 0 else 0
        )


        print("\n Sampling Analysis:")
        print(f"Duration: {duration_seconds:.3f} s")
        print(f"Mean positive interval: {mean_interval:.3f} ms")
        print(f"Observed frequency: {observed_frequency:.2f} Hz")
        print(f"Non-positive intervals: {(len(timestamps) - 1) - len(intervals_ms)}")