
import pytest

from backend.processing.data_quality import assess_window_quality
from backend.processing.quality_gate import (
    QualityPolicy,
    evaluate_quality,
)


def make_quality(samples=60, invalid=0):
    window = {
        "start_s": 0.0,
        "end_s": 1.0,
        "sample_count": samples,
        "invalid_sample_count": invalid,
        "gaze_availability_rate": (
            (samples - invalid) / samples
            if samples else None
        ),
    }

    return assess_window_quality(window)


def example_policy():
    # Experimental demonstration, not a validated threshold policy.
    return QualityPolicy(
        min_gaze_availability=0.80,
        min_nominal_sample_ratio=0.80,
        min_usable_nominal_ratio=0.70,
    )


def test_eligible_window():
    decision = evaluate_quality(
        make_quality(60, 0),
        example_policy(),
        window_complete=True,
    )

    assert decision["status"] == "ELIGIBLE"
    assert decision["reasons"] == []


def test_low_availability():
    decision = evaluate_quality(
        make_quality(58, 31),
        example_policy(),
        window_complete=True,
    )

    assert decision["status"] == "UNKNOWN"
    assert "LOW_AVAILABILITY" in decision["reasons"]
    assert "LOW_USABLE_NOMINAL_RATIO" in decision["reasons"]


def test_sparse_but_valid_samples():
    decision = evaluate_quality(
        make_quality(9, 0),
        example_policy(),
        window_complete=True,
    )

    assert decision["status"] == "UNKNOWN"
    assert "LOW_NOMINAL_SAMPLE_RATIO" in decision["reasons"]
    assert "LOW_USABLE_NOMINAL_RATIO" in decision["reasons"]


def test_empty_window():
    decision = evaluate_quality(
        make_quality(0, 0),
        example_policy(),
        window_complete=True,
    )

    assert decision["status"] == "UNKNOWN"
    assert "NO_DATA" in decision["reasons"]


def test_partial_window():
    decision = evaluate_quality(
        make_quality(9, 0),
        example_policy(),
        window_complete=False,
    )

    assert decision["status"] == "UNKNOWN"
    assert "PARTIAL_WINDOW" in decision["reasons"]


def test_unverified_window_completeness():
    decision = evaluate_quality(
        make_quality(60, 0),
        example_policy(),
    )

    assert decision["status"] == "UNKNOWN"
    assert "WINDOW_COMPLETENESS_UNVERIFIED" in decision["reasons"]


def test_unconfigured_policy():
    decision = evaluate_quality(
        make_quality(60, 0),
        QualityPolicy(),
        window_complete=True,
    )

    assert decision["status"] == "UNKNOWN"
    assert "POLICY_NOT_CONFIGURED" in decision["reasons"]


def test_invalid_threshold():
    policy = QualityPolicy(
        min_gaze_availability=1.5,
    )

    with pytest.raises(ValueError):
        evaluate_quality(
            make_quality(),
            policy,
            window_complete=True,
        )


def test_nan_threshold():
    policy = QualityPolicy(
        min_gaze_availability=float("nan"),
    )

    with pytest.raises(ValueError):
        evaluate_quality(
            make_quality(),
            policy,
            window_complete=True,
        )


def test_threshold_boundary():
    policy = QualityPolicy(
        min_gaze_availability=0.80,
    )

    decision = evaluate_quality(
        make_quality(60, 12),
        policy,
        window_complete=True,
    )

    assert decision["status"] == "ELIGIBLE"


def test_window_completeness_can_be_optional():
    policy = QualityPolicy(
        min_gaze_availability=0.80,
        require_complete_window=False,
    )

    decision = evaluate_quality(
        make_quality(60, 0),
        policy,
        window_complete=None,
    )

    assert decision["status"] == "ELIGIBLE"


def test_invalid_completeness_type():
    with pytest.raises(ValueError):
        evaluate_quality(
            make_quality(),
            example_policy(),
            window_complete="yes",
        )
