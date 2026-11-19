# CLOE — T01-A2 Session Run Sheet (future participant study)

**Status:** `DRAFT / NOT USED` — duplicate this file for each session; complete only after approvals.  
**Session ID (pseudonym):** `________`  
**Participant ID (pseudonym):** `________`  
**Date / operator:** `________`  
**Protocol version / Git commit:** `________`

> This is an experimenter checklist, not a consent form or substitute for the institution's ethics review. Do not put participants' names, personal accounts, or sensitive data in this file.

## A. Before recruitment and collection

- [ ] Supervisor reviewed design and independent outcome definitions.
- [ ] Institution's ethics/consent and data governance requirements satisfied.
- [ ] NASA TLX form/scoring instructions confirmed, including performance item direction.
- [ ] Trial stimuli and independent correct answers approved and version-frozen.
- [ ] Sequence allocation and randomization seed prepared; task order does not systematically confound difficulty.
- [ ] Local storage path/permissions and retention/deletion procedure agreed.
- [ ] Webcam use disabled unless covered by separate explicit consent and validation plan.

## B. Technical setup (log actual, don't assume)

| Field | Value |
|---|---|
| Tobii device model / serial pseudonym | `________` |
| Firmware / Tobii SDK version | `________` |
| OS / Python / code commit | `________` |
| Measured sampling interval, median / range | `________` |
| Monitor dimensions physical (mm) / pixels | `________` |
| Viewing distance / display scaling | `________` |
| Brightness, theme, font size, lighting | `________` |
| Time sync method / checks | `________` |
| Tracker calibration / validation result | `________` |
| Quality gate configuration/version | `________` |
| Sequence ID / randomization seed | `________` |

- [ ] Device is detected; sample stream contains plausible monotonic timestamps.
- [ ] Both-eye valid and one-eye valid handling is logged.
- [ ] Calibration/independent validation result recorded; re-calibrate if acceptance rule fails.
- [ ] No personal browser accounts, notifications or unapproved applications are visible.
- [ ] Trial and questionnaire clock/events verified.

## C. Participant sequence

1. [ ] Consent and pseudonymous session creation completed.
2. [ ] Participant accessibility/comfort setup performed.
3. [ ] Practice CODE + BROWSER tasks completed (excluded from analysis).
4. [ ] Block baseline recorded under fixed lighting; baseline protocol version logged.
5. [ ] Assigned trial sequence run (fill below), **not** always ordered LOW → HIGH.
6. [ ] Six NASA-TLX ratings + separate perceived difficulty recorded **after each trial**.
7. [ ] Breaks, interruptions, recalibrations and configuration changes logged.
8. [ ] Participant debrief and withdrawal/deletion information provided.

| Order | Task ID (assigned) | Start/end stamps | Answer/time/timeout | TLX recorded | Calibration change / interruptions |
|---|---|---|---|---|---|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |
| 6 | | | | | |
| 7 | | | | | |
| 8 | | | | | |

## D. After-session QA (must be evidence backed)

- [ ] Device timestamps and host task markers synchronized / anomalies documented.
- [ ] Gaze events align with eight trial IDs, plus intentional practice and baseline IDs.
- [ ] Both/either/none validity and missingness summary generated per trial.
- [ ] Invalid windows are `UNKNOWN`, never silently treated as a load category.
- [ ] Six questionnaire items are present and scoring matches the frozen form.
- [ ] Trial correctness computed against approved independent answer key.
- [ ] No unapproved image/video or identifying data saved.
- [ ] Data stored locally in permission-controlled folder; public repo contains only aggregate/nonidentifying evidence.
- [ ] Exclusions, protocol deviations and revisions logged transparently.

## E. Pilot-only acceptance review (requires evidence)

| Question | Evidence path / finding / decision |
|---|---|
| Were LOW/HIGH tasks understood, non-ambiguous and feasibly different? | `________` |
| Did trial durations and participant burden fit? | `________` |
| Are calibration/gaze validity and usable windows sufficient? | `________` |
| Are lighting/layout confounds adequately controlled? | `________` |
| Is Raw TLX scoring reproducible and clearly task-level? | `________` |
| What changed after pilot, and when was protocol frozen? | `________` |
| Supervisor approval of final sample size, gate, and analysis? | `________` |

**Report as:** `OBSERVED` only when evidence paths and values exist. Until then: `TO VALIDATE / NOT RUN`.
