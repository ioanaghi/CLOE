
import csv
import math
from collections import Counter
from pathlib import Path

from backend.processing.movement_segmentation import (
    validate_velocity_threshold,
)
from backend.processing.window_oculomotor import (
    extract_window_oculomotor_features,
)


REQUIRED_COLUMNS = {
    "start_s",
    "end_s",
    "status",
    "reasons",
}

VALID_QUALITY_STATUSES = {"ELIGIBLE", "UNKNOWN"}


def load_quality_decisions(csv_path):
    """
    Read and validate M0.3 Quality Gate decisions.

    Expected CSV columns:
      start_s, end_s, status, reasons

    Additional columns are allowed.
    Original row order is preserved.
    """

    csv_path = Path(csv_path)

    with csv_path.open(
        "r", newline="", encoding="utf-8-sig"
    ) as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError("Quality decision CSV has no header")

        if len(reader.fieldnames) != len(set(reader.fieldnames)):
            raise ValueError("Duplicate CSV column names")

        if not REQUIRED_COLUMNS.issubset(reader.fieldnames):
            missing = REQUIRED_COLUMNS - set(reader.fieldnames)
            raise ValueError(f"Missing columns: {sorted(missing)}")

        decisions = []
        previous_start = None

        for row_number, row in enumerate(reader, start=2):
            if None in row:
                raise ValueError(
                    f"Row {row_number}: unexpected extra fields"
                )

            if any(value is None for value in row.values()):
                raise ValueError(
                    f"Row {row_number}: missing field values"
                )

            try:
                start_s = float(row["start_s"])
                end_s = float(row["end_s"])
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"Row {row_number}: invalid window boundaries"
                ) from exc

            if (
                not math.isfinite(start_s)
                or not math.isfinite(end_s)
                or start_s < 0
                or end_s <= start_s
            ):
                raise ValueError(
                    f"Row {row_number}: invalid window interval"
                )

            status = row["status"].strip()

            if status not in VALID_QUALITY_STATUSES:
                raise ValueError(
                    f"Row {row_number}: invalid quality status"
                )

            if (
                previous_start is not None
                and start_s <= previous_start
            ):
                raise ValueError(
                    "Quality windows must have increasing start times"
                )

            decisions.append({
                "start_s": start_s,
                "end_s": end_s,
                "quality_gate_status": status,
                "quality_gate_reasons": row["reasons"],
            })

            previous_start = start_s

    return decisions


def integrate_quality_windows(
    timestamps,
    velocity_results,
    quality_decisions,
    threshold,
):
    """
    Apply T04-A feature extraction to saved M0.3 decisions.

    Each input decision produces exactly one output record.
    Quality Gate reasons are preserved.
    """

    validate_velocity_threshold(threshold)

    results = []

    for decision in quality_decisions:
        feature_result = extract_window_oculomotor_features(
            timestamps=timestamps,
            velocity_results=velocity_results,
            start_s=decision["start_s"],
            end_s=decision["end_s"],
            threshold=threshold,
            quality_gate_status=decision["quality_gate_status"],
        )

        if (
            decision["quality_gate_status"] == "UNKNOWN"
            and (
                feature_result["feature_status"] != "UNAVAILABLE"
                or feature_result["features"] is not None
            )
        ):
            raise ValueError(
                "UNKNOWN quality window exposed usable features"
            )

        results.append({
            **feature_result,
            "quality_gate_reasons": (
                decision["quality_gate_reasons"]
            ),
        })

    return results


def summarize_feature_availability(results):
    """
    Summarize Quality Gate and feature availability statuses.
    """

    quality_counts = Counter(
        row["quality_gate_status"]
        for row in results
    )

    feature_counts = Counter(
        row["feature_status"]
        for row in results
    )

    unavailable_reasons = Counter(
        row["feature_reason"]
        for row in results
        if row["feature_reason"] is not None
    )

    return {
        "window_count": len(results),
        "quality_gate_counts": dict(quality_counts),
        "feature_status_counts": dict(feature_counts),
        "unavailable_reasons": dict(unavailable_reasons),
    }
