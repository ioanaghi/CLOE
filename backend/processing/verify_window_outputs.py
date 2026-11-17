
import argparse
import csv
import hashlib
import json
import math
from collections import Counter
from pathlib import Path


STATES = ("LOW_VELOCITY", "HIGH_VELOCITY", "UNKNOWN")

WINDOW_COLUMNS = {
    "start_s", "end_s", "sample_count"
}

QUALITY_COLUMNS = {
    "start_s", "end_s", "status", "reasons"
}

OUTPUT_COLUMNS = {
    "start_s",
    "end_s",
    "threshold",
    "quality_gate_status",
    "quality_gate_reasons",
    "selected_interval_count",
    "feature_status",
    "feature_reason",
    "features_json",
}


def read_csv(path, required_columns):
    """Read CSV independently and reject malformed structure."""

    with Path(path).open(
        newline="", encoding="utf-8-sig"
    ) as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError(f"{path}: missing header")

        if len(reader.fieldnames) != len(set(reader.fieldnames)):
            raise ValueError(f"{path}: duplicate columns")

        if not required_columns.issubset(reader.fieldnames):
            raise ValueError(f"{path}: missing required columns")

        rows = list(reader)

    for index, row in enumerate(rows, start=2):
        if None in row or any(v is None for v in row.values()):
            raise ValueError(
                f"{path}: malformed CSV row {index}"
            )

    return rows


def read_json(path):
    with Path(path).open(encoding="utf-8") as file:
        return json.load(file)


def sha256_file(path):
    digest = hashlib.sha256()

    with Path(path).open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def finite_number(value, name):
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name}: invalid number") from exc

    require(
        math.isfinite(result),
        f"{name}: non-finite number"
    )
    return result


def nonnegative_integer(value, name):
    require(
        not isinstance(value, bool),
        f"{name}: boolean is not an integer count"
    )

    try:
        result = int(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{name}: invalid integer") from exc

    require(
        str(value) == str(result),
        f"{name}: non-canonical integer"
    )
    require(result >= 0, f"{name}: negative count")

    return result


def same_number(a, b):
    return math.isclose(
        finite_number(a, "first value"),
        finite_number(b, "second value"),
        rel_tol=0.0,
        abs_tol=1e-6,
    )


def validate_feature_payload(features, selected_count):
    """Validate saved movement summary accounting."""

    require(
        isinstance(features, dict),
        "AVAILABLE row has no feature object"
    )

    count = nonnegative_integer(
        features.get("total_intervals"),
        "features.total_intervals"
    )

    require(
        count == selected_count,
        "Feature interval count mismatch"
    )

    state_counts = features.get("interval_count_by_state")

    require(
        isinstance(state_counts, dict),
        "Missing interval_count_by_state"
    )

    require(
        set(state_counts) == set(STATES),
        "Unexpected movement states"
    )

    total = sum(
        nonnegative_integer(
            state_counts[state],
            f"interval_count_by_state.{state}"
        )
        for state in STATES
    )

    require(
        total == count,
        "Movement-state counts do not cover selected intervals"
    )

    shares = features.get("interval_share_by_state")

    require(
        isinstance(shares, dict) and set(shares) == set(STATES),
        "Invalid interval shares"
    )

    require(count > 0, "AVAILABLE row has zero intervals")

    for state in STATES:
        actual = finite_number(shares[state], f"share.{state}")
        expected = state_counts[state] / count

        require(
            0 <= actual <= 1
            and math.isclose(actual, expected, abs_tol=1e-9),
            f"Incorrect interval share for {state}"
        )

    segment_count = nonnegative_integer(
        features.get("segment_count"),
        "features.segment_count"
    )

    segment_counts = features.get("segment_count_by_state")

    require(
        isinstance(segment_counts, dict)
        and set(segment_counts) == set(STATES),
        "Invalid segment counts"
    )

    require(
        sum(
            nonnegative_integer(segment_counts[state], state)
            for state in STATES
        ) == segment_count,
        "Segment count mismatch"
    )

    require(
        nonnegative_integer(
            features.get("transition_count"),
            "transition_count"
        ) == segment_count - 1,
        "Transition count mismatch"
    )


def verify_window_outputs(
    raw_csv,
    window_csv,
    quality_csv,
    output_dir,
):
    """Independently verify T04-C persisted artifacts."""

    raw_csv = Path(raw_csv)
    window_csv = Path(window_csv)
    quality_csv = Path(quality_csv)
    output_dir = Path(output_dir)

    stem = raw_csv.stem

    require(
        window_csv.stem == stem + "_window_features",
        "Window CSV recording identifier mismatch"
    )
    require(
        quality_csv.stem == stem + "_quality_decisions",
        "Quality CSV recording identifier mismatch"
    )

    policy = read_json(
        output_dir / f"{stem}_window_policy.json"
    )

    summaries = read_json(
        output_dir / f"{stem}_window_summary.json"
    )

    require(isinstance(policy, dict), "Invalid policy JSON")
    require(isinstance(summaries, list), "Invalid summary JSON")

    require(
        policy.get("experiment") == "M0.4-T04-C",
        "Unexpected experiment identifier"
    )
    require(
        policy.get("recording") == raw_csv.name,
        "Source recording name mismatch"
    )

    for field, path in (
        ("raw_sha256", raw_csv),
        ("window_csv_sha256", window_csv),
        ("quality_csv_sha256", quality_csv),
    ):
        require(
            policy.get(field) == sha256_file(path),
            f"Source hash mismatch: {field}"
        )

    thresholds = policy.get("thresholds")

    require(
        isinstance(thresholds, list) and bool(thresholds),
        "Missing experimental thresholds"
    )

    for threshold in thresholds:
        require(
            isinstance(threshold, (int, float))
            and not isinstance(threshold, bool)
            and math.isfinite(threshold)
            and threshold > 0,
            "Invalid experimental threshold"
        )

    require(
        len(set(thresholds)) == len(thresholds),
        "Duplicate thresholds"
    )

    require(
        len(summaries) == len(thresholds),
        "Summary threshold count mismatch"
    )

    require(
        policy.get("alignment_method")
        == "fully_contained_velocity_intervals",
        "Unexpected temporal alignment method"
    )

    windows = read_csv(window_csv, WINDOW_COLUMNS)
    decisions = read_csv(quality_csv, QUALITY_COLUMNS)

    require(
        len(windows) == len(decisions),
        "Input window count mismatch"
    )

    require(
        nonnegative_integer(policy.get("windows"), "policy.windows")
        == len(decisions),
        "Policy window count mismatch"
    )

    expected_quality = Counter()

    for window, decision in zip(windows, decisions):
        require(
            same_number(window["start_s"], decision["start_s"])
            and same_number(window["end_s"], decision["end_s"]),
            "Original window boundaries are inconsistent"
        )

        require(
            decision["status"] in {"ELIGIBLE", "UNKNOWN"},
            "Invalid original Quality Gate status"
        )

        expected_quality[decision["status"]] += 1

    require(
        policy.get("quality_counts") == dict(expected_quality),
        "Policy Quality Gate counts mismatch"
    )

    require(
        nonnegative_integer(
            policy.get("velocity_intervals"),
            "policy.velocity_intervals"
        ) == max(
            0,
            nonnegative_integer(
                policy.get("samples"),
                "policy.samples"
            ) - 1
        ),
        "Policy sample/velocity counts mismatch"
    )

    baseline = None
    reports = []

    for index, threshold in enumerate(thresholds):
        label = str(threshold).replace(".", "p")

        csv_path = output_dir / f"{stem}_windows_{label}.csv"

        rows = read_csv(csv_path, OUTPUT_COLUMNS)

        require(
            len(rows) == len(decisions),
            f"Threshold {threshold}: wrong window count"
        )

        quality_counts = Counter()
        feature_counts = Counter()
        unavailable_reasons = Counter()
        alignment_signature = []

        for position, (row, decision) in enumerate(
            zip(rows, decisions)
        ):
            context = f"Threshold {threshold}, window {position}"

            require(
                same_number(row["start_s"], decision["start_s"])
                and same_number(row["end_s"], decision["end_s"]),
                f"{context}: changed window boundaries"
            )

            require(
                same_number(row["threshold"], threshold),
                f"{context}: incorrect threshold"
            )

            require(
                row["quality_gate_status"]
                == decision["status"],
                f"{context}: changed Quality Gate status"
            )

            require(
                row["quality_gate_reasons"]
                == decision["reasons"],
                f"{context}: changed Quality Gate reasons"
            )

            selected = nonnegative_integer(
                row["selected_interval_count"],
                f"{context}: selected_interval_count"
            )

            require(
                selected <= policy["velocity_intervals"],
                f"{context}: selected count exceeds recording"
            )

            quality_counts[row["quality_gate_status"]] += 1

            status = row["feature_status"]

            require(
                status in {"AVAILABLE", "UNAVAILABLE"},
                f"{context}: invalid feature status"
            )
            feature_counts[status] += 1

            if row["quality_gate_status"] == "UNKNOWN":
                require(
                    status == "UNAVAILABLE"
                    and row["feature_reason"]
                    == "QUALITY_GATE_UNKNOWN"
                    and row["features_json"] == "",
                    f"{context}: UNKNOWN quality exposed features"
                )

            if status == "AVAILABLE":
                require(
                    row["quality_gate_status"] == "ELIGIBLE",
                    f"{context}: AVAILABLE without eligibility"
                )

                require(
                    row["feature_reason"] == "",
                    f"{context}: AVAILABLE row has rejection reason"
                )

                try:
                    features = json.loads(row["features_json"])
                except json.JSONDecodeError as exc:
                    raise ValueError(
                        f"{context}: invalid features JSON"
                    ) from exc

                validate_feature_payload(features, selected)

            else:
                require(
                    row["features_json"] == "",
                    f"{context}: UNAVAILABLE row exposes features"
                )

                reason = row["feature_reason"]

                require(
                    reason in {
                        "QUALITY_GATE_UNKNOWN",
                        "NO_CONTAINED_INTERVALS",
                    },
                    f"{context}: unexpected unavailable reason"
                )

                unavailable_reasons[reason] += 1

            alignment_signature.append((
                row["start_s"],
                row["end_s"],
                row["quality_gate_status"],
                row["quality_gate_reasons"],
                selected,
                status,
                row["feature_reason"],
            ))

        if baseline is None:
            baseline = alignment_signature
        else:
            require(
                alignment_signature == baseline,
                "Window availability or alignment differs "
                "between thresholds"
            )

        saved_summary = summaries[index]

        require(
            same_number(saved_summary["threshold"], threshold),
            "Summary threshold order mismatch"
        )

        summary = saved_summary["summary"]

        require(
            summary["window_count"] == len(rows),
            "Summary window count mismatch"
        )

        require(
            summary["quality_gate_counts"]
            == dict(quality_counts),
            "Summary Quality Gate counts mismatch"
        )

        require(
            summary["feature_status_counts"]
            == dict(feature_counts),
            "Summary feature availability mismatch"
        )

        require(
            summary["unavailable_reasons"]
            == dict(unavailable_reasons),
            "Summary unavailability reasons mismatch"
        )

        reports.append({
            "threshold": threshold,
            "windows": len(rows),
            "available": feature_counts["AVAILABLE"],
            "unavailable": feature_counts["UNAVAILABLE"],
            "quality_unknown": quality_counts["UNKNOWN"],
        })

    return reports


def main():
    parser = argparse.ArgumentParser(
        description="Independently verify CLOE T04 window outputs"
    )

    parser.add_argument("raw_csv", type=Path)
    parser.add_argument("window_csv", type=Path)
    parser.add_argument("quality_csv", type=Path)

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/processed/window_oculomotor"),
    )

    args = parser.parse_args()

    try:
        reports = verify_window_outputs(
            args.raw_csv,
            args.window_csv,
            args.quality_csv,
            args.output_dir,
        )
    except (ValueError, KeyError, OSError, TypeError) as exc:
        print("\n--- CLOE T04-D Verification ---")
        print("Result: FAIL")
        print("Reason:", exc)
        raise SystemExit(1)

    print("\n--- CLOE T04-D Verification ---")

    for report in reports:
        print(
            f'Threshold {report["threshold"]}: '
            f'{report["windows"]} windows | '
            f'{report["available"]} AVAILABLE | '
            f'{report["unavailable"]} UNAVAILABLE | '
            f'{report["quality_unknown"]} Quality UNKNOWN'
        )

    print("Cross-threshold alignment: PASS")
    print("Source-file hash verification: PASS")
    print("CSV/JSON read-back: PASS")
    print("Result: PASS")


if __name__ == "__main__":
    main()
