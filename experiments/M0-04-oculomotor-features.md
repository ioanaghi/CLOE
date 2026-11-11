# CLOE — M0.4: Oculomotor Feature Extraction

**Project:** Cognitive Load Occlusion Engine  
**Milestone:** M0.4 — Oculomotor Feature Extraction  
**Date opened:** 2026-11-11  
**Status:** IN PROGRESS

## 1. Milestone Objective

Develop and evaluate algorithms for extracting preliminary oculomotor features from Tobii Pro Nano gaze recordings.

The milestone builds upon the gaze validation, temporal processing, sliding-window feature extraction, and data-quality assessment components developed in M0.3.

Oculomotor features will not be treated as direct or independently validated measurements of cognitive load.

### T01 — Unit Testing and Regression Validation

**Date:** 2026-11-11  
**Status:** PASS — Software Validation

**Implementation:** `backend/processing/gaze_velocity.py`  
**Tests:** `backend/tests/test_gaze_velocity.py`

#### Objective

Verify that the gaze velocity calculation function behaves correctly for defined synthetic inputs and does not introduce regressions in the existing CLOE processing pipeline.

#### Observed Unit Test Results

| Test | Result |
|---|---|
| Stationary gaze | PASS |
| Horizontal movement | PASS |
| Diagonal movement | PASS |
| Invalid gaze point | PASS |
| NaN coordinates | PASS |
| Temporal gap | PASS |
| Duplicate timestamp | PASS |
| Invalid nominal frequency | PASS |
| Invalid temporal gap ratio | PASS |

**Unit tests:** 9/9 PASSED in 0.12 seconds.

#### Regression Testing

**Command:**

```powershell
py -3.10 -m pytest backend\tests -v
```

**Observed result:** 74/74 PASSED in 0.16 seconds.

**Environment:** Windows 11 Education, Python 3.10.11, pytest 9.2.0.

#### Interpretation

All nine velocity calculation tests passed, confirming the expected behavior for the defined synthetic scenarios.

The function calculates average displacement velocity using normalized display coordinates and device timestamps.

It rejects invalid measurements and temporally unreliable sample pairs according to the configured diagnostic rules.

The complete regression suite passed, indicating that the new implementation did not introduce regressions detectable by the existing tests.

#### Limitations

- The calculated velocity is expressed in normalized display units per second, not degrees per second.
- The implementation estimates average displacement velocity between consecutive gaze samples rather than instantaneous eye velocity.
- The temporal gap threshold is an engineering heuristic.
- The implementation has not been validated against ground-truth eye-movement events.
- Reliable saccade and fixation classification has not yet been established.

#### Conclusion

**Result: PASS — Unit Testing and Regression Validation**

T01 is ready for integration with real gaze recordings.

#### Evidence

**Velocity unit tests:**

![T01 gaze velocity tests](../docs/evidence/M0-04/t01-gaze-velocity-tests.png)

**Full regression suite:**

![T01 regression tests](../docs/evidence/M0-04/t01-regression-tests.png)