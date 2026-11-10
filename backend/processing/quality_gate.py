
from dataclasses import dataclass
import math


@dataclass(frozen=True)
class QualityPolicy:
    min_gaze_availability: float | None = None
    min_nominal_sample_ratio: float | None = None
    min_usable_nominal_ratio: float | None = None
    require_complete_window: bool = True


def validate_policy(policy):
    thresholds = (
        policy.min_gaze_availability,
        policy.min_nominal_sample_ratio,
        policy.min_usable_nominal_ratio,
    )

    for value in thresholds:
        if value is None:
            continue

        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
            or not 0 <= value <= 1
        ):
            raise ValueError(
                "Quality thresholds must be finite values between 0 and 1"
            )

    if not isinstance(policy.require_complete_window, bool):
        raise ValueError("require_complete_window must be boolean")


def evaluate_quality(
    quality,
    policy,
    window_complete=None,
):
    """
    Determine whether a window satisfies a quality policy.

    This function does not estimate cognitive load.
    """

    validate_policy(policy)

    if window_complete is not None and not isinstance(
        window_complete, bool
    ):
        raise ValueError("window_complete must be True, False or None")

    reasons = []

    if not quality["has_data"]:
        reasons.append("NO_DATA")

    if policy.require_complete_window:
        if window_complete is None:
            reasons.append("WINDOW_COMPLETENESS_UNVERIFIED")
        elif not window_complete:
            reasons.append("PARTIAL_WINDOW")

    thresholds = {
        "gaze_availability_rate": (
            policy.min_gaze_availability,
            "LOW_AVAILABILITY",
        ),
        "nominal_sample_ratio": (
            policy.min_nominal_sample_ratio,
            "LOW_NOMINAL_SAMPLE_RATIO",
        ),
        "usable_nominal_ratio": (
            policy.min_usable_nominal_ratio,
            "LOW_USABLE_NOMINAL_RATIO",
        ),
    }

    configured = any(
        threshold is not None
        for threshold, _ in thresholds.values()
    )

    if not configured:
        reasons.append("POLICY_NOT_CONFIGURED")

    for metric_name, (threshold, reason) in thresholds.items():
        if threshold is None:
            continue

        value = quality[metric_name]

        if (
            value is None
            or not isinstance(value, (int, float))
            or isinstance(value, bool)
            or not math.isfinite(value)
            or value < 0
        ):
            reasons.append("METRIC_UNAVAILABLE")
        elif value < threshold:
            reasons.append(reason)

    return {
        "status": "UNKNOWN" if reasons else "ELIGIBLE",
        "reasons": list(dict.fromkeys(reasons)),
    }
