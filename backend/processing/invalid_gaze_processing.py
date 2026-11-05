
def detect_invalid_runs(sources):
    """
    Detect consecutive runs of invalid gaze samples.
    """

    valid_sources = {"BOTH", "LEFT", "RIGHT", "NONE"}

    if any(source not in valid_sources for source in sources):
        raise ValueError("Unknown gaze source label")

    runs = []
    start = None

    for index, source in enumerate(sources):

        if source == "NONE":
            if start is None:
                start = index

        elif start is not None:
            runs.append({
                "start_index": start,
                "end_index": index - 1,
                "sample_count": index - start,
            })

            start = None

    # Handle an invalid run that reaches the end
    if start is not None:
        runs.append({
            "start_index": start,
            "end_index": len(sources) - 1,
            "sample_count": len(sources) - start,
        })

    return runs
