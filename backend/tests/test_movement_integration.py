
from backend.processing.analyze_movement import (
    build_velocity_results,
    evaluate_threshold,
)


def sample(timestamp, point):
    return {
        "timestamp": timestamp,
        "point": point,
        "source": "BOTH" if point is not None else "NONE",
    }


def test_one_velocity_per_consecutive_pair():
    samples = [
        sample(0, (0.1, 0.5)),
        sample(16667, (0.1, 0.5)),
        sample(33334, (0.2, 0.5)),
    ]

    results = build_velocity_results(samples)

    assert len(results) == 2
    assert results[0]["interval_index"] == 0
    assert results[1]["interval_index"] == 1


def test_invalid_sample_preserves_unknown_intervals():
    samples = [
        sample(0, (0.1, 0.5)),
        sample(16667, None),
        sample(33334, (0.2, 0.5)),
    ]

    results = build_velocity_results(samples)

    assert len(results) == 2
    assert all(result["velocity"] is None for result in results)
    assert all(
        result["reason"] == "INVALID_GAZE_POINT"
        for result in results
    )


def test_temporal_gap_is_preserved():
    samples = [
        sample(0, (0.1, 0.5)),
        sample(50000, (0.2, 0.5)),
    ]

    results = build_velocity_results(samples)

    assert len(results) == 1
    assert results[0]["velocity"] is None
    assert results[0]["reason"] == "TEMPORAL_GAP"


def test_threshold_does_not_change_unknown_count():
    samples = [
        sample(0, (0.1, 0.5)),
        sample(16667, (0.2, 0.5)),
        sample(33334, None),
        sample(50001, (0.3, 0.5)),
    ]

    results = build_velocity_results(samples)

    low_threshold = evaluate_threshold(results, 2.0)
    high_threshold = evaluate_threshold(results, 10.0)

    assert (
        low_threshold["state_counts"]["UNKNOWN"]
        == high_threshold["state_counts"]["UNKNOWN"]
    )


def test_segmentation_preserves_all_intervals():
    samples = [
        sample(0, (0.1, 0.5)),
        sample(16667, (0.1, 0.5)),
        sample(33334, (0.3, 0.5)),
        sample(50001, None),
    ]

    results = build_velocity_results(samples)
    evaluation = evaluate_threshold(results, 5.0)

    total_segment_intervals = sum(
        segment["interval_count"]
        for segment in evaluation["segments"]
    )

    assert total_segment_intervals == len(results)


def test_empty_recording():
    assert build_velocity_results([]) == []


def test_single_sample_has_no_velocity_intervals():
    samples = [sample(0, (0.5, 0.5))]

    assert build_velocity_results(samples) == []
