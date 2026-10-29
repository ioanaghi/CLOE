import tobii_research as tr

trackers = tr.find_all_eyetrackers()

if not trackers:
    print("No eye trackers found.")
else:
    tracker = trackers[0]

    print("Eye tracker found!")
    print("Model:", tracker.model)
    print("Name:", tracker.device_name)
    print("Frequency:", tracker.get_gaze_output_frequency(), "Hz")