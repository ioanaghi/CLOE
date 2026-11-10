from backend.processing.invalid_gaze_processing import detect_invalid_runs
from backend.processing.temporal_processing import analyze_timestamps

VALID_SOURCES ={ "BOTH", "LEFT", "RIGHT", "NONE" }

def extract_window_features(timestamps, sources, window_us=1_000_000, step_us=500_000, nominal_hz=60):
    """
    Extract data-quality features from sliding time windows.

    Windows are defined as [start, end).
    Timestamps are expressed in microseconds.
    """

    if len(timestamps) != len(sources):
        raise ValueError("Timestamps and sources must have the same length.")

    if window_us<=0 or step_us <= 0:
        raise ValueError("Window and step sizes must be positive.")
    
    if nominal_hz <= 0:
        raise ValueError("Nominal frequency must be positive.")
    
    if any(source not in VALID_SOURCES for source in sources):
        raise ValueError("Unknown gaze source label")
    
    if any(
        timestamps[i] <= timestamps[i - 1] 
        for i in range(1, len(timestamps))
    ):
        raise ValueError("Timestamps must be in strictly increasing order.")

    if not timestamps:
        return []
    
    first_timestamp = timestamps[0]
    last_timestamp = timestamps[-1]

    results = []
    start = first_timestamp

    while start <= last_timestamp:
        end = start + window_us
        
        indeces=[
            i for i, timestamp in enumerate(timestamps)
            if start <= timestamp < end
        ]

        window_sources = [sources[i] for i in indeces]
        window_timestamps = [timestamps[i] for i in indeces]

        sample_count = len(indeces)

        usable_count = sum(
            source != "NONE"
            for source in window_sources
        )

        binocular_count = window_sources.count("BOTH")
        invalid_count = window_sources.count("NONE")

        invalid_runs = detect_invalid_runs(window_sources)

        longest_invalid_run = max( 
            (run["sample_count"] for run in invalid_runs),
            default=0,
        )

        temporal_result = analyze_timestamps(window_timestamps, nominal_hz=nominal_hz)

        results.append({
            "start_s": (start - first_timestamp) / 1_000_000,
            "end_s": (end - first_timestamp) / 1_000_000,
            "sample_count": sample_count,
            "gaze_availability_rate": (
                usable_count / sample_count
                if sample_count else None
            ),
            "binocular_availability_rate": (
                binocular_count / sample_count
                if sample_count else None
            ),
            "invalid_sample_count": invalid_count,
            "longest_invalid_run": longest_invalid_run,
            "temporal_gap_count": len(
                temporal_result["large_gaps"]
            ),
        })

        start += step_us

    return results