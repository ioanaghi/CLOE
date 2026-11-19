# CLOE — T01-A1 Literature and Methodology Review

**Project:** Cognitive Load Occlusion Engine (CLOE)  
**Milestone / task:** T01-A1 — Literature and Methodology Review  
**Revision:** A1.4 targeted-search reproducibility and source audit, 2026-11-19  
**Status:** **IN PROGRESS** (A1.4 source audit and bounded web-search protocol completed; systematic database exports and supervisor sign-off not completed)  
**Scope:** Eye tracking and cognitive workload in desktop/software tasks, plus evidence for adaptive interface design and evaluation.

> **Methodology claim:** This is a *targeted, source-audited narrative review* with a documented, reproducible **shortlist-level** screening record. It is **not** a PRISMA systematic review. Search engines did not supply a complete stable result census, and no exhaustive ACM/IEEE/Scopus export was performed.

## 1. Questions and conceptual distinctions

- **RQ1 — sensing:** Which eye-tracking metrics have shown associations with workload in defined tasks, and under what measurement conditions?
- **RQ2 — reference measures:** How did studies assess difficulty/workload independently of those eye signals?
- **RQ3 — adaptive interface:** What evaluation risks arise when an interface changes automatically in response to inferred user state?
- **RQ4 — transferability:** Which findings plausibly transfer to Tobii Pro Nano (60 Hz), webcam signals and VS Code/browser tasks, and which require new experiments?

**Cognitive workload**, **intrinsic cognitive load**, **task difficulty**, **visual search effort**, **attention**, and **fatigue** are *not interchangeable*. Task difficulty manipulates conditions; NASA-TLX captures retrospective subjective workload; neither independently establishes moment-to-moment biological ground truth.

**Labels:** `SUPPORTED` = explicitly documented in an audited source *within its study setting*; `PROPOSED` = proposed CLOE method; `TO VALIDATE` = empirical question for future tests; `OBSERVED` = CLOE measurement backed by logs. This document makes **no new CLOE experimental observations**. A `RETRACTED` source is excluded as evidence.

## 2. Search integrity and selection

Searches took place 2026-11-19 across a general scholarly web index with publisher and public repository pages. The A1.4 pass also attempted direct database query interfaces for PubMed, ACM Digital Library and IEEE Xplore; the dynamic result pages could not be retrieved, so database hit/export counts remain UNKNOWN. Queries, source URLs and per-record decisions are recorded in [`T01-A1-search-log.md`](./T01-A1-search-log.md). Sources below are numbered persistently and structured fields are in [`T01-A1-evidence-matrix.csv`](./T01-A1-evidence-matrix.csv).

**Shortlist adjudication:** **15 included sources** **S1–S3, S5–S16**; **1 excluded** **S4** due to publisher retraction; **3 deferred** **D01–D03** due to access/scope limitations. Screening decisions for all 19 named candidates are in [`T01-A1-screening-decisions.csv`](./T01-A1-screening-decisions.csv). These numbers describe **only manually tracked named candidates**, *not* search-engine hit totals or an exhaustive evidence base.

**Minimum inclusion:** primary experiment or credible synthesis/guideline relevant to measurement or adaptive interaction; identifiable venue/DOI or archival record; directly inspectable abstract or full text; limitations recorded. **Flag, do not infer:** sample size, software context, workload validation, numerical statistics and any transferability not explicitly documented. Study design levels differ; entries marked abstract-only must not support numerical claims.

## 3. Matrix summary (verifiable in accompanying CSV)

| ID | Study and population | Independent reference | Main finding / caveat | Relevance |
|---|---|---|---|---|
| **S1** | Andrzejewska et al. 2020, 31 analyzed, C++ debugging | Difficulty report; correctness; time | Logical-versus-syntax condition: longer fixation duration and shorter saccades; fixed-order/task confounds | Relevant programming paradigm, not universal direction |
| **S2** | Wu et al. 2024, 15 + 22, Nano 60 Hz | NASA-TLX; task performance | Raw pupil ↔ TLX weak positive r=0.312; adjusted ↔ TLX non-significant r=0.103; abstract's r=0.513 is inconsistent | Hardware feasibility; beware illumination and task mixing |
| **S3** | Krejtz et al. 2018, 13 analyzed, EyeLink 500 Hz | Modified NASA-TLX; arithmetic accuracy | Difficulty affected workload reports and microsaccade/pupil metrics; authors caution short microsaccades require ≥300 Hz | **No microsaccade MVP dependency on Nano 60 Hz** |
| **S4** | Holmqvist et al. 2023 | N/A | **RETRACTED**; intentionally excluded from evidentiary support | Audit trace only |
| **S5** | Dunn et al. 2024 reporting guideline | N/A | Eye tracking reporting standards; separate author correction adds funding information | Methods checklist |
| **S6** | Biondi et al. 2023, 25 volunteers, webcam vs GP3 | Response time; subjective demand | Blink demand effect observed with eye tracker, not webcam; aggregate agreement does not imply workload discrimination | Separate webcam validation |
| **S7** | Weber et al. 2023, N=6 capture + N=6 evaluation | Developer qualitative feedback | Gaze-adaptive Visual Studio prototype favored unobtrusive changes and override; **not** cognitive-load classification | Closest adaptive IDE analogue |
| **S8** | Yanez et al. 2025, review of 91 papers | Review of evaluations | Adaptive visuals can increase overload through dynamic change; protect control and privacy | Architectural/evaluation framework |
| **S9** | Findlater & Gajos 2009, evaluation framework | N/A | Report algorithm properties, task and user characteristics, appropriate outcomes | Study-design guidance |
| **S10** | Gajos et al. 2008, empirical adaptive UI (abstract inspected) | Usability/performance | Accuracy and predictability affect satisfaction and performance in study | Pre-register adaptation accuracy and intrusiveness; **abstract-only** |
| **S11** | Darejeh et al. 2026, review of 87 studies | Literature synthesis | Common methods include performance, NASA-TLX, fixations; frequency ≠ validity | Multimethod evaluation |
| **S12** | Sun & Liao 2025, 36 analyzed in 2 AR substudies | NASA-TLX; task time | Physiology-triggered breaks reduced their *CSCR proxy* but did not establish a task-time improvement | Trade-off between assistance and disruption |
| **S13** | Medeiros et al. 2021, 26 analyzed programmers | Modified NASA-TLX; code understanding | EEG/gaze reference aids workload localization; ascending fixed task order | Reference-measure triangulation, not an EEG requirement |
| **S14** | Chen, Epps & Paas 2023, 20 recruited / **19 eye datasets** | 9-point perceived effort + completion time | Pupil and blink associations differed across cognitive, perceptual, communicative and physical demands | Critical task-type confound; full text reviewed |
| **S15** | Jin et al. 2023, N **not verified** | NASA-TLX + performance (abstract) | Blink frequency dependence on cognitive load varied by perceptual load | Perceptual versus cognitive distinction; **abstract-only** |
| **S16** | VL/HCC 2024 programming study, 28 participants | Workload assessments + performance (abstract) | IDE behavior and workload differed with code-provenance knowledge | Realistic code-task design; **abstract-only** |

### 3.1 S2 — Wu et al. 2024: verified numerical inconsistency

**Source:** https://doi.org/10.3390/app142411975, Results **§4.1–4.4** and Abstract; author reports both task groups and the **Tobii Pro Nano at 60 Hz** (Methods §3). There were **15 visual-tracking** and **22 laparoscopic** participants.

| Correlation identified in Results §4.2 | Pearson *r* | Reported *p* |
|---|---:|---:|
| Original mean pupil diameter ↔ NASA-TLX | **0.312** | <0.001 |
| Adjusted pupil diameter ↔ NASA-TLX | **0.103** | 0.11 (not significant) |
| Original mean pupil diameter ↔ adjusted pupil | **0.513** | <0.001 |

**Source discrepancy:** the **Abstract** calls 0.513 the pupil–NASA-TLX correlation, whereas Results **§4.2** assigns 0.513 to the relationship between original and adjusted pupil measurements. **Citation policy:** use the detailed Results values, explicitly note the discrepancy, and do not present 0.513 as reliable evidence of a workload correlation. Repetition changed subjective workload and pupil responses; visual tracking and laparoscopic tasks differ in participants, demands and setting. **CLOE status:** `SUPPORTED` as source audit; actual Nano-to-programming transfer is `TO VALIDATE`.

### 3.2 S3 — Krejtz et al. 2018: hardware-transfer boundary

**Source:** https://pmc.ncbi.nlm.nih.gov/articles/PMC6138399/; Methods **§3.1–3.6**, Results **§4**, Discussion. **17 volunteers**, **13 analyzed** after exclusions. Subjects maintained central fixation while completing difficult/easy/control mental arithmetic; independent measures comprised **a modified NASA-TLX**, arithmetic correctness and working-memory assessment. Recording employed **EyeLink 1000 at 500 Hz**, head stabilization and controlled lighting. The authors explicitly caution that resolving the shortest microsaccades requires **≥300 Hz**.

**Decision:** `PROPOSED` exclude microsaccades from required CLOE MVP. Standard (macro-)saccades and fixation metrics are separate events that may still be investigated with the 60 Hz device using cautious algorithms and quality tests. Do not substitute ordinary saccades for microsaccades or claim that this study validates 60 Hz microsaccade detection.

### 3.3 S6 — Biondi et al. 2023: hardware agreement ≠ cognitive-load validity

**Source:** https://doi.org/10.1049/ccs2.12088, Methods **§2**, Results **§3**. **25 volunteers**, three counterbalanced auditory n-back demand conditions, a **60 fps NexiGo webcam** and **60 Hz Gazepoint GP3 eye tracker**. Their independent demand checks were an additional reaction-time task and perceived demand. The camera-derived blink rate did **not** track manipulated demand in their Bayesian model (**BF=0.22**), whereas eye-tracker-derived blink rate did (**BF=40.65**); the overall comparison between sensor outputs did not yield a difference (**BF=0.18**). This does **not** show that eye-tracker blinks universally increase with workload.

**Decision:** `PROPOSED` validate webcam blink event agreement and workload sensitivity separately before including as predictive feature; blink alone never labels a high-load state.

### 3.4 S7 — Weber et al. 2023: closest architectural predecessor

**Source:** https://doi.org/10.1145/3603555.3603571; [open author PDF](https://www.medien.ifi.lmu.de/pubdb/publications/pub/weber2023muc/weber2023muc.pdf), Methods/Results **§3–5**. A gaze-aware **Visual Studio extension** predicted important IDE windows and resized layout. Authors report **N=6** for data collection, **N=6** for an initial evaluation, and qualitative preferences for changes that are unobtrusive, contextual and **overrideable**. In evaluation, participants encountered **5–70 changes over 30 minutes** across participants. One participant experienced a layout change that interfered with the editor and manually corrected it.

**Major distinction:** Weber et al. predict *task context / relevant pane*, **not validated cognitive overload**; this work must not be cited as proof that CLOE reduces workload. It does justify a direct architecture/evaluation comparison. **CLOE requirements:** adaptation cooldown, manual override, easy restore, task-critical-pane protection and logging of false positives, reversals and interruption.

### 3.5 S8–S12: what adaptive-interface research adds

- **S8 Yanez et al. (2025)** — https://doi.org/10.1111/cgf.15271. A state-of-the-art review of **91 papers** proposes a pipeline from sensing to user modelling and adaptation; it warns that dynamic changes can themselves overload the user. **PROPOSED:** separate sensing, classification, intervention assignment, execution and evaluation; consider privacy and control.
- **S9 Findlater & Gajos (2009)** — https://doi.org/10.1609/aimag.v30i4.2268. The authors' evaluation framework emphasizes describing adaptive algorithm properties, task/user variation and appropriate assessment. **PROPOSED:** record why each adaptation occurred and how accurately it supported the task.
- **S10 Gajos et al. (2008)** — DOI: https://doi.org/10.1145/1357054.1357252; [author abstract](https://www.eecs.harvard.edu/~kgajos/papers/2008/gajos08predictability.shtml). The abstract supports evaluating both *predictability* and *accuracy* of adaptation. **Limitation:** full study/sample details not extracted in this iteration; cite only at abstract level.
- **S11 Darejeh et al. (2026)** — https://doi.org/10.1177/00187208261427867. A systematic review of **87 studies** on cognitive-load assessment in software usability identified performance, NASA-TLX and fixation metrics among common approaches. **The popularity of a metric does not establish its validity for CLOE**.
- **S12 Sun & Liao (2025)** — https://doi.org/10.1017/dsj.2025.10040. **36 participants analyzed** across two AR studies; sensor-triggered rest was associated with decreased cumulative skin-conductance response, but task-time benefits were not established and interruption cost was observed. **Do not infer causality about gaze or adaptive desktop UI** from this physiology-triggered AR prototype. For CLOE, the transferable issue is to predefine acceptable workload–performance trade-offs.

### 3.6 S13 — Programming workload reference measurement

**Source:** https://doi.org/10.3390/s21072338, Methods **§3**; **30 recorded / 26 analyzed**. Three **Java comprehension tasks** (presented in fixed ascending complexity order), EEG and gaze synchronized with code regions, response explaining the code, and a **modified four-item NASA-TLX**. The study supports using *multiple independent references* rather than declaring a static code-complexity score to be a direct cognitive-load label. **Limitations:** fixed ordering; EEG is invasive/expensive and is not required for CLOE's initial prototype.


### 3.7 S14 — Chen, Epps & Paas (2023): differentiate load types

**Source:** https://doi.org/10.1111/bjep.12577; publisher full text, Methods §§ Participants/Tasks/Apparatus and Results. **20 recruited, 19 with usable eye data**, using **Pupil Labs wearable 60 Hz eye cameras** (not the Tobii Pro Nano). Participants completed low-/high-demand arithmetic, visual search, walking and communicative tasks; independent measures included **9-point perceived effort ratings** and **task time**. Eye-derived measures varied by **task type**: blink rate discriminated low/high levels in the cognitive condition but not in the perceptual condition. The authors also reported a pupil-size effect in the cognitive condition. **For CLOE:** record task category and visual demand, control lighting and avoid training a load classifier across incomparable interface contexts without verifying transfer. `SUPPORTED` within the study; transfer is `TO VALIDATE`.

### 3.8 S15 — Jin et al. (2023): perceptual and cognitive demands interact

**Source:** https://doi.org/10.1080/00140139.2023.2223785; publisher/PubMed abstracts available; publisher full text blocked. Authors report that **blink frequency reflected cognitive demand only when perceptual demand was low**, while pupil diameter and blink duration were sensitive to both manipulated factors. The paper combined ocular measures with NASA-TLX, performance and ERPs. We **do not** extract unverified sample size, devices, effect sizes or classifier accuracy. This is `SUPPORTED_ABSTRACT_ONLY`, and a context-aware CLOE indicator remains `TO VALIDATE`.

### 3.9 S16 — Developer Behaviors in Validating and Repairing LLM-Generated Code (2024)

**Source:** https://doi.org/10.1109/VL/HCC60511.2024.00015; IEEE/DOI abstract. **28 participants** worked on repairing/validating generated code across **three software projects**, with IDE interaction, eye tracking, workload assessment and interviews. The abstract reports that the group informed of AI-code provenance had better performance but **higher cognitive workload**. Study details beyond the abstract, including exact eye features, scales and equipment, remain `NOT VERIFIED`. This is a **programming-task analogue**, not evidence for the efficacy of CLOE or a universal relation between performance and workload.

### 3.10 Publisher integrity audit: S4 retracted; S5 corrected

**S4 RETRACTED:** Holmqvist et al., *Eye tracking: empirical foundations for a minimal reporting guideline*, https://doi.org/10.3758/s13428-021-01762-8. Publisher notice published **16 Nov 2023**: https://doi.org/10.3758/s13428-023-02285-0. Authors cited unsuitable supporting references in several statements. **S4 must not be used to support design claims**; retained solely as a retraction audit entry.

**S5 usable guideline:** Dunn et al., *Minimal reporting guideline for research involving eye tracking (2023 edition)*, https://doi.org/10.3758/s13428-023-02187-1 (journal volume **2024**). Its **30 Apr 2024 author correction**, https://doi.org/10.3758/s13428-024-02438-9, added a funding note. This correction does **not** retract the guideline or, according to the correction notice, change its methods checklist. Use S5 for reporting, **not** S4.

## 4. Integrated methodological implications for CLOE

| Evidence / consideration | CLOE proposal | Verification required before acceptance |
|---|---|---|
| Program comprehension is workload-relevant (S1, S13) | Pilot comparable IDE code questions across levels | Demonstrate difficulty manipulation with performance + subjective data |
| Pupil reflects multiple influences (S2, S3) | Participant-relative baseline; stable lighting; log brightness, screen content, head pose if available | Validate pupil availability and compare baselines during real code tasks |
| Macro-saccade / fixation metrics are plausible (S1) | Configure algorithms with explicit units and quality gates | Test 60 Hz device, degrees conversion, fixation thresholds and event detection |
| Short microsaccades need fast acquisition (S3) | Exclude microsaccades from required MVP | New dedicated high-rate validation only if reconsidered |
| Webcam blink sensing may lack workload sensitivity (S6) | Keep blink supplementary | Estimate error/coverage and independent association, not just raw count agreement |
| Adaptive UI may interrupt user (S7–S10, S12) | Reversible occlusion, manual override, cooldown, no hard removal of functionality | Record intervention rate, restore actions, errors, subjective agency and UX |
| Measurement needs triangulation (S1–S3, S6, S11, S13) | NASA-TLX after each task + completion time + accuracy + subjective difficulty | Predefine analysis and label strategy; avoid circular training labels |
| Eye tracking quality varies (S5) | Full reporting of 60 Hz, calibration, timestamps, validity, screen geometry, processing settings | Provide reproducible run logs and sampling-quality statistics |
| Task context changes eye-signal interpretation (S14, S15) | Match visual load; annotate IDE versus browsing context; consider separate baselines | Compare matched-condition effects; check confounding by screen brightness and visual density |
| Programming workload and performance may diverge (S16) | Measure both outcomes independently | Predefine accuracy/time and subjective workload rather than treating either as perfect load truth |

**Candidate features:** (a) valid-data coverage, (b) fixation count/rate and duration, (c) macro-saccade count, amplitude and rate, (d) pupil changes relative to a carefully defined baseline; (e) webcam blink and posture **exploratory only**. No single metric is a validated real-time cognitive-load classifier in this review. `UNKNOWN` is the correct operational fallback for low-quality windows, never a synonym for `HIGH`.

## 5. Proposed study designs (not performed)

### Phase A — workload signal feasibility

1. Recruit consenting adults under the relevant university research/ethics process; note programming experience and equipment conditions minimally.
2. Pre-record baseline, Tobii calibration/validation and display/ambient illumination; measure gaze/validity as quality, not workload.
3. Counterbalance versions of C++/Python comprehension, debugging and browser search tasks across difficulty levels; separate task type from difficulty, and explicitly match visual search demand, display contrast and task time where feasible (S14–S15).
4. Record eye metrics, anonymized task event timestamps and task outcomes; only record webcam data where consent and privacy policy permit.
5. Administer NASA-TLX per task (specify raw/weighted version and scoring before launch), record time, accuracy and subjective difficulty.
6. Analyze within-person associations; report confidence intervals/effect sizes; group train/test by participant or session to avoid overlap leakage; record missing data.

### Phase B — adaptive UI intervention efficacy

Compare a **static control** against CLOE, using counterbalanced conditions with matched task difficulty. *Predefine* (i) task accuracy and time, (ii) perceived workload, (iii) perceived disruption, feature awareness, SUS/usability, (iv) unhelpful adaptations and undo/override, (v) persistence and recovery after false signals. State a practical non-inferiority criterion for performance *before* conducting the study. Include a manual-control mode to distinguish algorithmic adaptation from user-initiated simplification if feasible.

**Privacy and reproducibility:** local processing by default, informed consent, no unnecessary raw face-video retention, session pseudonyms, software and driver versions, timestamp sync, and explicit retention/deletion plan. Ethical review and supervisor validation remain open.

## 6. Decision register — source-based, not yet experimentally validated

| ID | Decision | Status | Basis / next test |
|---|---|---|---|
| D01 | Combine subjective and performance measures rather than eye-derived labels alone | PROPOSED | S1, S2, S11, S13; define scoring |
| D02 | Keep pupil/fixations/saccades as candidates only | PROPOSED | S1–S3; pilot and control confounders |
| D03 | Microsaccades not required at 60 Hz | PROPOSED (strong hardware justification) | S3; no claim of validated detection |
| D04 | Webcam blink is supplementary and independently validated | PROPOSED | S6; compare detection and demand sensitivity separately |
| D05 | `UNKNOWN` for inadequate data; no automatic `HIGH` from low quality | PROPOSED | Existing quality gate; integration test |
| D06 | Reversible adaptive occlusion and explicit override | PROPOSED | S7–S10; test rate and user experience |
| D07 | Measure both workload and task-performance trade-offs | PROPOSED | S11–S12; predefined acceptance criteria |
| Q01 | Numeric 0.513 in S2 abstract cannot be cited as pupil–TLX | RESOLVED SOURCE DISCREPANCY | Document contradictory abstract/results |
| Q02 | S4 cannot justify the methods | RESOLVED RETRACTION | Publisher notice; use S5 |
| Q03 | Is real-time workload identification accurate with CLOE signals? | TO VALIDATE | Pilot, participant-level holdout |
| Q04 | Does CLOE help without masking necessary tools? | TO VALIDATE | Controlled UI intervention experiment |
| D08 | Record task category / perceptual demand in trials | PROPOSED | S14 full text + S15 abstract; matched-difficulty pilot |
| D09 | Track workload and programming performance as distinct endpoints | PROPOSED | S16 abstract; verify in controlled code tasks |

## 7. Bias/limitations audit

- The source set was assembled through **targeted scholarly search**, not an exhaustive database or formal systematic-review protocol. The screening counts pertain only to a named shortlist, not total search hits.
- Multiple studies have **small samples** (S2/S3/S7/S12), constrained conditions (S3), unequal tasks/groups (S2), or fixed task sequences (S1/S13).
- **Eye-derived features and software task type are not independent ground truth**. Retrospective NASA-TLX is independent of the eye measures but is a noisy, non-instantaneous subjective reference.
- HCI studies of adaptive menus/visualizations/AR are **design analogues**, not evidence of measured CLOE efficacy.
- **S4 is retracted**, S5 corrected funding information. Avoid accidentally copying S4 claims from older drafts. The S4 publication year is 2023 (issue), though its original online publication was 2022.
- **S14:** 20 recruited but **19 ocular data sets analyzed**; do not label eye-signal N as 20. **S15–S16 are abstract-only**, so no unverified equipment, sample size (S15) or classifier numerical effects are presented.
- Qualitative paper S7 offers promising feasibility but cannot justify a universal adaptation frequency, user acceptance rate or workload reduction; S10 evidence is abstract-level only.
- Generalizability to *Tobii Pro Nano 60 Hz + webcam + coding and browsing* remains an experimental question.

## 8. Definition of Done and closure status

- [x] Explicit research questions and terminology.
- [x] Evidence matrix including sample, task, measure, independent reference, result, limitation and source URL.
- [x] Full-text source extraction for core studies Wu and Krejtz and study on adaptive IDE; verify retraction/correction records.
- [x] Add adaptive interface studies and state transferability conditions.
- [x] Bounded shortlist screening with named decisions and actual web query strings logged.
- [x] A1.4 source audit: cross-check core study numbers; add S14–S16 with verification-level caveats; create an auditable per-candidate screening CSV.
- [x] Record **attempted** PubMed/ACM/IEEE dynamic database queries and why searchable hit/export counts could not be obtained.
- [x] Draft audit of claims, source discrepancies and PROPOSED versus SUPPORTED.
- [ ] **Complete formally reproducible multi-database search** (e.g. ACM/IEEE/Scopus or PubMed where appropriate): per-database search strings, timestamp, hit/export counts, deduplication and all screen decisions. No counts may be invented retrospectively.
- [ ] Obtain full text and detailed extraction of any abstract-only study if used for quantitative conclusions (not required if only abstract-level claim retained).
- [ ] Approve methods/design decisions with supervisor and define experimental protocol in T01-A2.
- [ ] Review/commit these artifacts in repo (not performed by this document update).

**Final decision for this iteration:** `A1.4 TARGETED SEARCH + FINAL CLAIM AUDIT = COMPLETE WITH LIMITATIONS`; **T01-A1 overall = IN PROGRESS**, **not PASSED**, under the previously agreed full multi-database search and supervisor sign-off criterion. The three database search result pages were inaccessible here; no result census/export is claimed. This review alone does not validate a cognitive-load detector or adaptive UI intervention.

## 9. Bibliography: included evidence (see CSV for extraction)

1. **S1:** Andrzejewska, M., et al. (2020). *Examining Students’ Intrinsic Cognitive Load During Program Comprehension – An Eye Tracking Approach.* https://doi.org/10.1007/978-3-030-52240-7_5 — https://pmc.ncbi.nlm.nih.gov/articles/PMC7334692/
2. **S2:** Wu, Y., Zhang, Y., & Zheng, B. (2024). *Workload Assessment of Operators: Correlation Between NASA-TLX and Pupillary Responses.* https://doi.org/10.3390/app142411975
3. **S3:** Krejtz, K., et al. (2018). *Eye tracking cognitive load using pupil diameter and microsaccades with fixed gaze.* https://doi.org/10.1371/journal.pone.0203629
4. **S5:** Dunn, M. J., et al. (2024). *Minimal reporting guideline for research involving eye tracking (2023 edition).* https://doi.org/10.3758/s13428-023-02187-1 ; author correction https://doi.org/10.3758/s13428-024-02438-9
5. **S6:** Biondi, F. N., et al. (2023). *On validating a generic camera-based blink detection system for cognitive load assessment.* https://doi.org/10.1049/ccs2.12088
6. **S7:** Weber, T., Thiel, R. V. M., & Mayer, S. (2023). *Supporting Software Developers Through a Gaze-Based Adaptive IDE.* https://doi.org/10.1145/3603555.3603571
7. **S8:** Yanez, F., Conati, C., Ottley, A., & Nobre, C. (2025). *The State of the Art in User-Adaptive Visualizations.* https://doi.org/10.1111/cgf.15271
8. **S9:** Findlater, L., & Gajos, K. Z. (2009). *Design Space and Evaluation Challenges of Adaptive Graphical User Interfaces.* https://doi.org/10.1609/aimag.v30i4.2268
9. **S10:** Gajos, K. Z., Everitt, K., Tan, D. S., Czerwinski, M., & Weld, D. S. (2008). *Predictability and accuracy in adaptive user interfaces.* https://doi.org/10.1145/1357054.1357252 ; [Author record](https://www.eecs.harvard.edu/~kgajos/papers/2008/gajos08predictability.shtml).
10. **S11:** Darejeh, A., Marcus, N., Mohammadi, G., & Sweller, J. (2026). *Cognitive Load Measurement Methods for Usability Testing: A Critical Analysis and Framework for Interface Evaluation.* https://doi.org/10.1177/00187208261427867
11. **S12:** Sun, J., & Liao, T. (2025). *Designing adaptive feedback systems for managing cognitive load in augmented reality.* https://doi.org/10.1017/dsj.2025.10040
12. **S13:** Medeiros, J., et al. (2021). *Can EEG Be Adopted as a Neuroscience Reference for Assessing Software Programmers’ Cognitive Load?* https://doi.org/10.3390/s21072338
13. **S14:** Chen, S., Epps, J., & Paas, F. (2023). *Pupillometric and blink measures of diverse task loads: Implications for working memory models.* https://doi.org/10.1111/bjep.12577
14. **S15:** Jin, H., et al. (2023). *Recognition and evaluation of mental workload in different stages of perceptual and cognitive information processing using a multimodal approach.* https://doi.org/10.1080/00140139.2023.2223785 **[abstract-level extraction only]**
15. **S16:** *Developer Behaviors in Validating and Repairing LLM-Generated Code Using IDE and Eye Tracking.* (2024). VL/HCC. https://doi.org/10.1109/VL/HCC60511.2024.00015 **[abstract-level extraction only; authors to verify]**

**Excluded but retained for audit:** **S4** Holmqvist et al. (2023), https://doi.org/10.3758/s13428-021-01762-8 — **RETRACTED**; https://doi.org/10.3758/s13428-023-02285-0.


## 10. A1.4 final audit: reproducibility and acceptance boundary (2026-11-19)

**Audited artifacts:** literature review (`.md`), evidence matrix (`.csv`), search log (`.md`) and screening decisions (`.csv`). The audit checks source IDs, count consistency, missing metadata explicitly marked, exact URLs, and the mapping from supported results to proposed CLOE design.

**What can be claimed now:** a *targeted, source-audited narrative review*, 15 included papers/guidelines, one retracted exclusion, three deferred named candidates; the new web-search records and query language are reproducible at the **query-string** level. The full text for S14 and publication metadata for S15/S16 were checked where accessible. **What cannot be claimed:** an exhaustive multi-database search, PRISMA evidence census, stable search hit counts, exported ACM/IEEE/PubMed records or supervisor approval. Dynamic search-result URLs were inaccessible in this environment; see search log.

**Required hands-on completion if the originally agreed stringent DoD is retained:** use institutional/library access to run the pre-specified search protocol; save a timestamped screenshot and RIS/BibTeX/CSV export per database; deduplicate by DOI/title; record every inclusion/exclusion in the screening CSV; update the evidence matrix and review; then obtain supervisor feedback and commit. If the supervisor accepts a **targeted narrative review** instead, explicitly record that scope change rather than silently presenting this as systematic.
