# ADR-001 — Handling Invalid and Single-Eye Gaze Samples

**Status:** Proposed  
**Date:** 2026-10-29  
**Project:** CLOE  
**Related experiment:** M0-02

## Context

The Tobii Pro Nano provides gaze-point coordinates and validity indicators for the left and right eyes independently.

During the initial acquisition experiment, both valid and invalid gaze measurements were observed.

CLOE requires a strategy for handling missing gaze information without introducing misleading coordinates into downstream processing.

## Decision

The initial gaze-processing implementation will follow these rules:

- If both eyes provide valid gaze points, calculate their arithmetic mean.
- If only the left eye provides valid data, use the left-eye gaze point.
- If only the right eye provides valid data, use the right-eye gaze point.
- If neither eye provides valid data, mark the combined gaze point as unavailable.

A gaze point will be considered usable only when its validity indicator is positive and its coordinates are finite.

Invalid measurements will not automatically be replaced with zero coordinates.

## Alternatives Considered

**Discard samples unless both eyes are valid**

Simple, but unnecessarily removes potentially useful single-eye measurements.

**Use only one eye throughout the recording**

Consistent processing, but ignores valid information from the other eye.

**Interpolate missing gaze positions**

Potentially useful for short gaps, but introduces estimated values that could hide actual gaze movements.

## Consequences

- More samples may remain usable when only one eye is tracked.
- Each sample should retain its original validity information.
- Combined gaze coordinates must be distinguishable from raw measurements.
- Arithmetic averaging may not always provide the most accurate binocular estimate.
- Interpolation requires separate validation before implementation.

## Validation Plan

The decision will be evaluated using controlled gaze recordings.

The implementation will be tested against samples representing all four combinations of left-eye and right-eye validity.

## Related Modules

- `backend/acquisition/first_gaze.py`
- `backend/processing/gaze_processing.py`

## Notes

This decision defines an initial processing strategy, not a scientifically validated gaze-fusion algorithm.

The strategy may be revised following experimental evaluation.