# CLOE — T01-A2 Experimental Protocol Design

**Project:** Cognitive Load Occlusion Engine (CLOE)  
**Task:** T01-A2 — Experimental Protocol Design  
**Version:** 0.1 (protocol draft; not preregistered or executed)  
**Prepared:** 2026-11-19  
**Status:** `IN PROGRESS — protocol designed, pilot/approvals pending`  
**Predecessor:** T01-A1 — targeted, source-audited literature review (`IN PROGRESS` pending formal search/supervisor approval)  
**Scope note:** This document *proposes* future studies. It contains **no newly collected experimental evidence**.

## 0. Scientific integrity and status labels

- `SUPPORTED`: a claim documented in a cited publication **within that study's conditions**.
- `PROPOSED`: a CLOE-specific design decision, parameter, threshold, study choice or workflow, not yet tested.
- `TO VALIDATE`: a hypothesis or engineering assertion to test during CLOE studies.
- `OBSERVED`: a result actually obtained in CLOE and supported by a stored log/artifact; **none is claimed for this protocol**.
- `BLOCKED`: requires ethics/institutional approval, supervisor review, hardware checks, completed stimuli or a justified analysis plan.

**Do not equate:** task difficulty, subjective workload (NASA-TLX), cognitive load, fatigue, visual search effort or gaze-derived features. Task difficulty is the **manipulated independent variable** in Phase A; NASA-TLX is a **task-level subjective response**, not a second-by-second ground-truth label.

## 1. Goal and research questions

### Phase A — Eye-signal feasibility (first study)

**Goal:** Determine whether eye-tracking signals from an available Tobii Pro Nano at 60 Hz are of usable quality, and whether selected ocular features covary with task demands and task-level self-reported workload during standardized coding and browser tasks. This is **not** yet a validated real-time overload classifier.

- **RQ-A1:** Do low- and high-demand task variants produce distinguishable NASA-TLX and performance outcomes within participants?
- **RQ-A2:** Which pre-specified pupil, fixation and ordinary saccade metrics show interpretable within-participant associations with NASA-TLX or demand condition, after considering task family and quality?
- **RQ-A3:** How much data survives the existing quality gate for each task family, and what artifacts/confounds explain failures?

**Exploratory hypotheses (TO VALIDATE):** higher-demand tasks will tend to yield higher task-level NASA-TLX; ocular metrics may relate to task demand, but **no fixed direction** is assumed for every metric across task families. Do not infer cognitive overload from one gaze signal.

### Phase B — Adaptive interface efficacy (later study, after implementation)

**Goal:** Compare static UI with CLOE's reversible adaptive occlusion/simplification while preserving task performance and user control.

- **RQ-B1:** Does CLOE change task-level perceived workload relative to static UI?
- **RQ-B2:** Does CLOE preserve accuracy and completion time within pre-agreed margins?
- **RQ-B3:** How often do adaptations interrupt work, mask necessary content, or need manual undo/override?

**Design separation:** Phase A runs with a **static UI**. Phase B must not begin until the sensing, adaptation, and fallback logic pass their own engineering tests. Do not evaluate Phase A predictions and Phase B benefit as though they were the same construct.

## 2. Relevant evidence from T01-A1

| Evidence ID | Supported source-level finding | Implication / CLOE status |
|---|---|---|
| S1 — Andrzejewska et al. (2020) | Eye-movement metrics differ across programming-comprehension task types; study had task/order limitations. | `PROPOSED`: matched programming tasks, controlled order. |
| S2 — Wu et al. (2024) | Tobii Pro Nano (60 Hz) collected pupil data in workload tasks; paper has an abstract/results correlation discrepancy (see T01-A1). | `PROPOSED`: collect pupil data, but do not treat pupil as workload ground truth. |
| S3 — Krejtz et al. (2018) | Microsaccade study used high-frequency EyeLink (500 Hz) and cautioned about detection of short microsaccades. | `PROPOSED`: **exclude microsaccades from 60 Hz MVP outcomes**. |
| S5 — Dunn et al. (2024) | Eye-tracking reporting guideline specifies calibration, validation, environment, data quality and preprocessing. | `PROPOSED`: keep full acquisition/quality metadata. |
| S6 — Biondi et al. (2023) | Webcam blink measurement agreement did not imply equivalent task-demand sensitivity. | `PROPOSED`: webcam blink is optional and separately evaluated. |
| S7 — Weber et al. (2023) | Adaptive IDE study highlights a balance between automated adaptation and user control. | `PROPOSED`: undo, bypass, cooldown, interruption metrics in Phase B. |
| S14/S15 — Chen et al. (2023), Jin et al. (2023) | Ocular associations can vary by cognitive/perceptual task demand; Jin is abstract-level in T01-A1. | `PROPOSED`: stratify by task family and constrain visual demand. |

See references in §14. The previously discussed **retracted** Holmqvist et al. publication is excluded from the methods justification; cite Dunn et al. instead.

## 3. Design and participants — Phase A

**Design (`PROPOSED`):** within-subject factorial feasibility study:
- `task_family`: **CODE** (VS Code) vs **BROWSER** (controlled local/offline documentation website).
- `demand`: **LOW** vs **HIGH**, defined by pilot-checked task variants.
- `variant`: **A** vs **B** of comparable difficulty within each task-family × demand cell.
- **8 trials per participant** = 2 families × 2 demands × 2 variants.
- Counterbalance block and within-block trial orders using reproducible assigned schedules and record `randomization_seed`/`sequence_id`. Avoid always presenting easiest tasks first. Each task's correctness key must be set **before** data collection.

**Recruitment (`PROPOSED`, not achieved):** voluntary **adults aged 18+** with basic text-editor/browser skills; record coding experience in broad categories. Pilot with **3–5** individuals **only to troubleshoot stimuli and procedure**; these numbers are **not** a power calculation. Main-study N and inferential scope will be fixed with supervisor/statistical input **after pilot-based variability/effect estimates**. Do not claim a confirmed sample or population generalizability.

**Exclusion and accessibility:** do not automatically exclude glasses or contacts; record when tracking/calibration succeeds or fails. Predefine excessive data-loss exclusions **before analysis**, report all exclusion reasons and counts. Provide a method to pause/withdraw without penalty. Use the institution's ethics and data-processing procedures prior to recruiting participants.

## 4. Apparatus, environment and privacy

**Observed in prior CLOE engineering logs (not rechecked in this task):** Tobii Pro Nano detected at 60 Hz; processing and quality checks have been developed. Re-run the device setup and calibration checklist at the experiment, do not assume earlier testing verifies new sessions.

**Fixed setup (`PROPOSED`):** the same machine, monitor, resolution, scaling, browser build, VS Code build, font size, theme, distance and seating instructions when practicable. Record screen width/height in pixels **and physical size**, estimated viewing distance and coordinate system if calculating degrees of visual angle. Fix luminance/brightness and lighting; if no lux meter is available, record the room, light source, time of day, blinds, monitor brightness and screen/theme settings, without inventing lux values. Keep high/low conditions similar in contrast/visual density, or explicitly measure/report differences.

**Signals:**
- **Core:** Tobii gaze (timestamps, binocular validity, points), pupil diameter where valid; task events, outcomes and quality metrics.
- **Exploratory:** webcam blinks/posture only with **separate explicit consent**, appropriate local processing, documented validation and a necessity justification. Not mandatory for Phase A.
- **Excluded from core:** detection of microsaccades at 60 Hz; diagnosis of any clinical state.

**Data handling (`PROPOSED`):** local processing, pseudonymous participant/session IDs, restricted folder permissions, no browsing to personal accounts, no proprietary code, no raw face video unless specifically approved and consented. Store consent forms separately from sensor data, provide deletion/withdrawal procedure, and set the precise retention period with supervisor/institution (not yet defined). Do not upload raw gaze/face data to public repositories.

## 5. Stimulus construction and difficulty manipulation

Task blueprint (8 IDs and their placeholders): `T01-A2-task-matrix.csv`. The **actual C++ snippets, controlled web pages, scoring keys and equivalence evidence still need authoring**.

- **CODE tasks:** a standardized editor project with a short C++ function and a question requiring locating a logical issue / predicting behavior; LOW/HIGH should primarily vary required reasoning depth, not unrelated syntax familiarity or the number of panels visible.
- **BROWSER tasks:** a **locally hosted or offline, version-frozen documentation mini-site**; identify a correct fact or compare two linked facts. LOW/HIGH should primarily vary reasoning and navigation demands, not ads, network delay or uncontrolled web-page changes.
- **Cross-family caveat:** tasks from CODE and BROWSER may differ visually even when called LOW/HIGH. Model **family × demand** and avoid interpreting unadjusted pooling as pure cognitive load.
- **Before main study:** independently review answer keys; pilot completion rates, error types, task times, ambiguities and visual characteristics. Revise tasks **before freezing stimuli**, log versions and revisions.

## 6. Session procedure — Phase A (`PROPOSED`)

1. **Pre-session:** ethics/consent check, pseudonymize participant, log broad experience and relevant display/tracking accommodations. No data collection before approval.
2. **Setup:** lock task versions/configuration, record screen geometry and lighting, verify clock alignment, device identity/frequency, webcam status, software/SDK versions.
3. **Calibration & validation:** use tracker calibration; run an independent gaze-point validation procedure and log outcomes. Recalibrate if outside a **predefined** acceptance rule; this rule is `TO VALIDATE` during pilot.
4. **Training:** provide a practice task excluded from analysis; verify understanding of both editor and browser tasks.
5. **Baseline:** capture a fixed **30–60 s neutral reference** under identical lighting before each task-family block; document its visual stimulus. This interval is a pilot choice, not a validated workload baseline.
6. **Trials:** 8 trials; start event → show frozen stimulus → capture timestamps/gaze → answer/timeout → end event. Initial **5-minute cap per task** (`PROPOSED`, pilot-adjustable before freeze).
7. **Post-trial ratings:** after **each** trial, administer the six NASA-TLX subscales using a single documented **Raw TLX** (unweighted) scoring variant, plus a separate simple self-rating of perceived difficulty. Ratings must not be requested while ocular outcomes for that task are being computed.
8. **Breaks:** at least a short break between trials; use scheduled longer breaks when tired. Record breaks, recals, interruptions, eye-tracker loss and screen/theme changes.
9. **Exit:** debrief, optional qualitative comments, withdrawal/deletion reminders; verify data completeness and secure storage.

**Estimated burden (`PROPOSED`, pilot to confirm):** eight trials × at most five minutes (≤40 min task time), questionnaires (~16 min at 2 min/task), setup/calibration/practice (~15 min), baselines/breaks (~10–20 min): roughly **80–95 minutes**. Keep fatigue effects in mind; shorten or split the session if pilot indicates excessive burden.

## 7. Outcome definitions and quality rules

### Primary Phase A outcome

**Manipulation check**: participant-level change in task-level **Raw TLX** between HIGH and LOW demand, with task family accounted for. Raw TLX is *unweighted*, unlike NASA's original weighted TLX; document exact subscale scales, direction of the performance item, and transformation to a common 0–100 metric **before collecting data**. Never mix scores from differently scaled forms. NASA describes the six dimensions and original weighted method: https://www.nasa.gov/human-systems-integration-division/nasa-task-load-index-tlx/.

### Secondary outcomes

- Correctness (`is_correct` from pre-specified scoring key), timed success/time to completion (with timeouts and incomplete tasks explicitly coded).
- Pupil features relative to recorded baseline (validity and illumination controlled); no assumption of causal interpretation.
- Fixation candidates and **ordinary** saccade candidates: counts/rates, median fixation duration; optional angular amplitude **only if** geometry is valid and conversion documented.
- Data completeness: percent valid both eyes / either eye / neither eye, missing samples, gap duration, window eligibility and `UNKNOWN` count.
- Exploratory, separate: camera blink event agreement and task-demand sensitivity; do **not** fold into primary workload outcome before validation.

### Preprocessing and data-quality gate

- Respect the actual Tobii sample timestamps (60 Hz nominal sampling implies ~16.7 ms per sample, but sampling intervals must be **measured**, not synthesized).
- Prefer two valid eyes when possible; if one-eye fallback is permitted, explicitly label the quality tier and preserve side-specific metadata.
- Do not impute through large data gaps, interpolate beyond the predefined rule, or convert lost tracking to `HIGH` workload.
- Use the existing CLOE quality-gate implementation. **Candidate** per-window minimum valid proportion **0.80** for an initial sensitivity analysis is `PROPOSED / TO VALIDATE`, **not** a literature-derived or locked acceptance threshold. Also report outcomes at alternative preregistered cutoffs after pilot. Log threshold, denominator, time-window length and eye-validity policy.
- Quality-failed windows are **`UNKNOWN` / excluded from inference**, with counts retained and a visible safe-state during real-time use.
- Fixation/saccade identification thresholds must explicitly declare units (px/s vs degrees/s), sampling limits and tests. Do not claim independent event validation until checked on quality-controlled traces.

## 8. Data specification and reproducibility

Expected **pseudonymous local** outputs (schemas are provisional; map onto current data structures rather than duplicating modules):

| File | Grain | Minimum fields |
|---|---|---|
| `participants.csv` | participant | `participant_id`, `experience_band`, `consent_version`, `withdrawn` (no real names) |
| `sessions.csv` | session | `session_id`, `participant_id`, `device_model`, `firmware`, `sdk_version`, `display_px`, `display_mm`, `viewing_distance_cm`, `lighting_notes`, `randomization_seed`, `sequence_id` |
| `trials.csv` | trial | `trial_id`, `session_id`, `task_id`, `family`, `demand`, `variant`, `start_time`, `end_time`, `timeout`, `is_correct`, `task_seconds`, `stimulus_version` |
| `gaze.csv` | gaze sample | `session_id`, `trial_id`, `device_timestamp`, `system_timestamp`, `left/right_valid`, `left/right_x/y`, `left/right_pupil` and per-field validity |
| `events.csv` | event | `session_id`, `trial_id`, `timestamp`, `event_type`, `metadata_schema_version` (no free-text personal data) |
| `ratings.csv` | trial | `trial_id`, six TLX item responses, `raw_tlx_0_100`, `difficulty_self_rating`, `form_version` |
| `quality.csv` | trial/window | `trial_id`, `window_start/end`, `valid_fraction`, `gate_status`, `unknown_reason`, `gate_configuration_version` |

**Time sync:** preserve tracker and host timestamps with documented conversion and error checks; provide monotonic event ordering; never align streams by row number. Record acquisition/processing code commit, Python/OS, dependency lock and all task/artifact versions.

## 9. Analysis plan — Phase A

1. **Feasibility first:** by participant and family report missingness, calibration validity, gate-eligible share, usable trial count and excluded data. If coverage is inadequate, address acquisition/quality before interpreting workload metrics.
2. **Manipulation check:** compare HIGH vs LOW Raw TLX and time/correctness **within participant**. Report descriptive plots/effect sizes and confidence intervals where justified; account for family, order, trial number and participant in models if sample size permits.
3. **Feature analysis:** aggregate pre-specified window features to trial level, then compare with **trial-level** TLX; analyze pupil/fixations/saccades as separate candidate associations. Do not label all windows in a high-TLX task as known `HIGH` ground truth.
4. **Confound analysis:** examine family, baseline lighting, visual density, participant experience, task order, fatigue/breaks, calibration quality and data-loss patterns.
5. **Prediction only if justified:** if building a model later, split by **participant or session**, not randomly by adjacent windows; fit all normalization inside training folds and report uncertainty, class balance and participant-level metrics. No definitive accuracy promised here.
6. **Interpretation:** absence of association is a valid result; distinguish statistical, practical and engineering feasibility. Retain all preregistered null and unfavorable findings.

**No post-hoc threshold tuning reported as confirmatory inference.** Any pilot-based modifications must be frozen and versioned before confirmatory data collection. Sample-size and analysis-model choices are `TO VALIDATE` with supervisor.

## 10. Phase B adaptive UI trial (`FUTURE / PROPOSED`)

**Conditions:** `STATIC` (unchanged application) vs `ADAPTIVE` (CLOE with reversible occlusion, manual override and conservative cooldown). Optional `MANUAL` arm can be included only if study burden and sample permit; otherwise compare manual preference separately without claiming a three-arm experiment.

**Design:** counterbalanced crossover with matched task variants and logged adaptation exposure. Never compare tasks of different difficulty by condition without accounting for that difference.

**Primary future outcomes:** task-level Raw TLX; task performance (correctness/time) as explicit co-endpoints. **Safety/user control outcomes:** erroneous occlusion, content blocked, undo/override use, interruptions, recovery time, adaptation frequency, preference and perceived predictability. Define a practical performance non-inferiority margin with the supervisor **before** conducting Phase B. No such validated margin exists in this draft.

**Fail-safe (`PROPOSED`):** when data fail the gate or state is uncertain, preserve/restore the normal UI; provide persistent manual reset, never trap the user in a simplified mode. Log adaptation decisions and reversals for auditing, without exposing private content.

## 11. Risk register

| Risk | Mitigation | Gate |
|---|---|---|
| Lighting drives pupil changes | fixed brightness/conditions; baseline per block; log deviations | before pilot |
| Poor eye-tracking samples | calibration validation, real timestamps, quality gate, UNKNOWN fallback | pilot |
| Task difficulty confounded with visual search | frozen stimuli, pilot difficulty check, task-family interaction | before main study |
| Practice/order/fatigue | alternate forms, assigned sequences, breaks, order covariates | before main study |
| Subjective TLX is not ground truth | task-level analysis + objective performance + cautious interpretation | analysis |
| Same participant windows in train and test | group splits by participant/session | any predictive work |
| UI hides needed tools | reversible overlay, immediate override, count interventions and errors | Phase B |
| Consent/privacy | approval, pseudonymization, local storage, explicit webcam opt-in, retention policy | before recruitment |
| Underpowered conclusions | pilot for feasibility only; approve main N and planned analysis | before main study |

## 12. Definition of Done and approvals

### T01-A2 protocol drafting (this iteration)
- [x] Define distinct Phase A vs Phase B goals and research questions.
- [x] Define factors, task family, candidate trial structure, baseline and session sequence.
- [x] Specify independent references and quantitative/qualitative outcome families.
- [x] Define data quality, UNKNOWN behavior, hardware restrictions and reproducibility fields.
- [x] Define confound control, privacy/consent boundaries and analysis plan.
- [x] Create stimulus/task matrix and experimenter run-sheet/checklist.

### Outstanding for **T01-A2 `PASSED`**
- [ ] Supervisor agrees on design, workload instrument, recruitment, analysis, and whether Phase B is in this thesis's available scope.
- [ ] Institutional ethics/data processing requirements determined and completed **before participant recruitment**.
- [ ] Actual code/browser stimuli and independent answer keys are authored and version-frozen.
- [ ] Randomization sequences/counterbalancing are generated, reviewed and stored.
- [ ] Pilot completed with logs, calibrations, TLX forms and feasibility analysis; inclusion/quality gate thresholds and N justified/frozen for main study.
- [ ] Approved protocol version and code/asset revision committed in repository.

**Current status:** `T01-A2 = IN PROGRESS`; this is a complete **first protocol draft** for review, **not** evidence that an experiment was run. T01-A1 retains its documented separate closure blockers. The study can be built incrementally, but data collection is blocked until the relevant approvals and safeguards are in place.

## 13. Suggested repository layout

```text
docs/research/
  T01-A1-literature-review.md
  T01-A1-evidence-matrix.csv
  T01-A1-search-log.md
  T01-A1-screening-decisions.csv
  T01-A2-experimental-protocol.md
  T01-A2-task-matrix.csv
  T01-A2-session-run-sheet.md
```

Do not store identifiable participant data, consent forms, face images or unfiltered raw streams in a public repository.

## 14. Bibliographic links (background, not experimental CLOE findings)

1. Andrzejewska et al. (2020). *Examining Students' Intrinsic Cognitive Load During Program Comprehension*. https://doi.org/10.1007/978-3-030-52240-7_5
2. Wu, Zhang & Zheng (2024). *Workload Assessment of Operators: Correlation Between NASA-TLX and Pupillary Responses*. https://doi.org/10.3390/app142411975
3. Krejtz et al. (2018). *Eye Tracking Cognitive Load Using Pupil Diameter and Microsaccades with Fixed Gaze*. https://doi.org/10.1371/journal.pone.0203629
4. Dunn et al. (2024). *Minimal reporting guideline for research involving eye tracking (2023 edition)*. https://doi.org/10.3758/s13428-023-02187-1 (2024 correction: https://doi.org/10.3758/s13428-024-02438-9)
5. Biondi et al. (2023). *On validating a generic camera-based blink detection system for cognitive load assessment*. https://doi.org/10.1049/ccs2.12088
6. Weber, Thiel & Mayer (2023). *Supporting Software Developers Through a Gaze-Based Adaptive IDE*. https://doi.org/10.1145/3603555.3603571
7. Chen, Epps & Paas (2023). *Pupillometric and blink measures of diverse task loads*. https://doi.org/10.1111/bjep.12577
8. Jin et al. (2023). Perceptual/cognitive load and ocular measures, abstract-level only in A1. https://doi.org/10.1080/00140139.2023.2223785
9. NASA. *NASA Task Load Index (TLX)*: official form and instruction manual. https://www.nasa.gov/human-systems-integration-division/nasa-task-load-index-tlx/
10. Tobii Pro Nano technical product description (60 Hz, timestamps, pupil signal). https://device.report/m/02bc898692f022c01f25e9c61b61626fb229ebb49be112fbf256468b328a9f9
