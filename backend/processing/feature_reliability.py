
import csv
import json
import math
from pathlib import Path


STATES = ("LOW_VELOCITY", "HIGH_VELOCITY", "UNKNOWN")


def load_window_features(path):
    """
    Load one verified T04-C threshold dataset.

    Returns window records with parsed feature payloads.
    Does not modify the source CSV.
    """
    path = Path(path)

    required = {
        "start_s",
        "end_s",
        "threshold",
        "quality_gate_status",
        "selected_interval_count",
        "feature_status",
        "features_json",
    }

    with path.open(newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError("Missing CSV header")

        if len(reader.fieldnames) != len(set(reader.fieldnames)):
            raise ValueError("Duplicate CSV columns")

        if not required.issubset(reader.fieldnames):
            raise ValueError("Missing required feature columns")

        rows = list(reader)

    results = []

    for index, row in enumerate(rows):
        if None in row or any(v is None for v in row.values()):
            raise ValueError(f"Malformed CSV row {index}")

        start = float(row["start_s"])
        end = float(row["end_s"])
        threshold = float(row["threshold"])

        if not all(math.isfinite(x) for x in (start, end, threshold)):
            raise ValueError("Non-finite window or threshold")

        if start < 0 or end <= start or threshold <= 0:
            raise ValueError("Invalid window or threshold")

        if row["selected_interval_count"].startswith("+"):
            raise ValueError("Invalid interval count format")

        try:
            selected = int(row["selected_interval_count"])
        except ValueError as exc:
            raise ValueError("Invalid selected interval count") from exc

        if selected < 0 or str(selected) != row["selected_interval_count"]:
            raise ValueError("Invalid selected interval count")

        quality = row["quality_gate_status"]
        status = row["feature_status"]

        if quality not in {"ELIGIBLE", "UNKNOWN"}:
            raise ValueError("Invalid Quality Gate status")

        if status not in {"AVAILABLE", "UNAVAILABLE"}:
            raise ValueError("Invalid feature status")

        payload = row["features_json"]

        if status == "AVAILABLE":
            if quality != "ELIGIBLE":
                raise ValueError("Unavailable quality exposed features")

            if not payload:
                raise ValueError("AVAILABLE window missing features")

            features = json.loads(payload)

            if not isinstance(features, dict):
                raise ValueError("Invalid feature object")

        else:
            if payload:
                raise ValueError("UNAVAILABLE window exposed features")
            features = None

        results.append({
            "start_s": start,
            "end_s": end,
            "threshold": threshold,
            "quality_gate_status": quality,
            "feature_status": status,
            "selected_interval_count": selected,
            "features": features,
        })

    return results


def state_shares(window):
    """
    Return the three interval shares for an AVAILABLE window.

    Recalculate shares from counts rather than trusting
    saved floating-point share values.
    """
    if window["feature_status"] != "AVAILABLE":
        return None

    features = window["features"]
    counts = features["interval_count_by_state"]
    total = features["total_intervals"]

    if (
        isinstance(total, bool)
        or not isinstance(total, int)
        or total <= 0
        or total != window["selected_interval_count"]
    ):
        raise ValueError("Invalid feature interval count")

    if not isinstance(counts, dict) or set(counts) != set(STATES):
        raise ValueError("Invalid movement-state counts")

    for state in STATES:
        value = counts[state]

        if (
            isinstance(value, bool)
            or not isinstance(value, int)
            or value < 0
        ):
            raise ValueError("Invalid state count")

    if sum(counts.values()) != total:
        raise ValueError("State counts do not cover intervals")

    return {
        state: counts[state] / total
        for state in STATES
    }


def analyze_threshold_sensitivity(datasets):
    """
    Compare the same windows across different thresholds.

    datasets: {threshold: list_of_window_records}

    This describes parameter sensitivity, not physiological
    reliability or cognitive-load prediction accuracy.
    """
    if not datasets:
        raise ValueError("No threshold datasets supplied")

    thresholds = sorted(datasets)

    if any(
        isinstance(t, bool)
        or not isinstance(t, (int, float))
        or not math.isfinite(t)
        or t <= 0
        for t in thresholds
    ):
        raise ValueError("Invalid thresholds")

    baseline = datasets[thresholds[0]]
    window_count = len(baseline)

    for threshold in thresholds:
        rows = datasets[threshold]

        if len(rows) != window_count:
            raise ValueError("Different window counts")

        for index, (original, current) in enumerate(
            zip(baseline, rows)
        ):
            if not math.isclose(
                current["threshold"], threshold,
                rel_tol=0,
                abs_tol=1e-9,
            ):
                raise ValueError("Dataset threshold mismatch")

            for field in (
                "start_s",
                "end_s",
                "quality_gate_status",
                "feature_status",
                "selected_interval_count",
            ):
                if current[field] != original[field]:
                    raise ValueError(
                        f"Window {index}: cross-threshold mismatch"
                    )

    per_window = []

    for index in range(window_count):
        first = baseline[index]

        result = {
            "start_s": first["start_s"],
            "end_s": first["end_s"],
            "feature_status": first["feature_status"],
            "selected_interval_count": first[
                "selected_interval_count"
            ],
            "unknown_share": None,
            "low_share_range": None,
            "high_share_range": None,
        }

        if first["feature_status"] == "AVAILABLE":
            shares = [
                state_shares(datasets[t][index])
                for t in thresholds
            ]

            low = [s["LOW_VELOCITY"] for s in shares]
            high = [s["HIGH_VELOCITY"] for s in shares]
            unknown = [s["UNKNOWN"] for s in shares]

            if any(
                not math.isclose(
                    value, unknown[0],
                    rel_tol=0,
                    abs_tol=1e-12,
                )
                for value in unknown[1:]
            ):
                raise ValueError(
                    "UNKNOWN interval share changed with threshold"
                )

            if any(
                low[i] > low[i + 1] + 1e-12
                or high[i] < high[i + 1] - 1e-12
                for i in range(len(thresholds) - 1)
            ):
                raise ValueError(
                    "Movement shares violate threshold ordering"
                )

            result["unknown_share"] = unknown[0]
            result["low_share_range"] = max(low) - min(low)
            result["high_share_range"] = max(high) - min(high)

        per_window.append(result)

    available = [
        row for row in per_window
        if row["feature_status"] == "AVAILABLE"
    ]

    def mean_of(key):
        if not available:
            return None
        return sum(row[key] for row in available) / len(available)

    return {
        "thresholds": thresholds,
        "window_count": window_count,
        "available_count": len(available),
        "unavailable_count": window_count - len(available),
        "availability_rate": (
            len(available) / window_count
            if window_count else None
        ),
        "mean_unknown_share": mean_of("unknown_share"),
        "mean_low_share_range": mean_of("low_share_range"),
        "mean_high_share_range": mean_of("high_share_range"),
        "per_window": per_window,
    }
