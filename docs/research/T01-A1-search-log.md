# CLOE — T01-A1 Search and Screening Log

**Audit date:** 2026-11-19 (Europe/Bucharest).  
**Iteration:** A1.3 + A1.4, targeted scholarly web discovery / source verification / database access audit.  
**Claim:** This log makes **the named candidate shortlist and its source decisions** auditable. It does **not** establish a PRISMA systematic review; full search-engine hit counts, database exports, and comprehensive deduplication were **not available**.

## 1. Search mode and reproducibility boundary

- Primary discovery: scholarly-indexed web search (`fast`), supplemented by direct inspection of publisher HTML/PMC, author bibliographic records and the Weber et al. PDF.
- Source verification: publisher/PMC records, methodology and result sections; for S7, original PDF with page screenshot inspection of pp. 267, 273 and 275. Search engine results are used for candidate discovery; publisher or open-access full text is preferred for quantitative extraction.
- The query list below reproduces the wording used in this iteration **as submitted to a general web search engine**. Results can change; no unobserved query result totals are claimed.
- Search window: research available through **2026-11-19**. No post-search references added.

## 2. Actual query strings (selected executed queries, not invented retrospective counts)

| QID | Query text | Intent | Distinct selected candidates |
|---|---|---|---|
| Q01 | `site:mdpi.com/2076-3417/14/24/11975 correlation NASA-TLX r 0.513 r 0.312 0.103 15 22 Wu Zhang Zheng` | S2 numerical audit | S2 |
| Q02 | `site:pmc.ncbi.nlm.nih.gov "Eye tracking cognitive load using pupil diameter and microsaccades with fixed gaze" participants results` | S3 participant/hardware check | S3 |
| Q03 | `adaptive interface cognitive load eye tracking adaptive user interface study evaluation NASA TLX performance user study` | Intervention literature | S8, S11, S12 |
| Q04 | `eye tracking based adaptive interface cognitive load programming software developer interface experiments NASA TLX` | IDE analogue | S7, S13 |
| Q05 | `systematic review adaptive user interface cognitive workload adaptive visualization overload user evaluation experimental 2024` | Adaptation framework | S8 |
| Q06 | `"Supporting Software Developers Through a Gaze-Based Adaptive IDE" pdf authors participants results` | Primary IDE study | S7 |
| Q07 | `adaptive menu user study Findlater Gajos 2009 evaluation adaptive interfaces predictability control` | User control studies | S9, S10 |
| Q08 | `"Predictability and accuracy in adaptive user interfaces" DOI Gajos 2008` | Source metadata | S10 |
| Q09 | `"Minimal reporting guideline for research involving eye tracking (2023 edition)" Dunn 2024 DOI` | Guideline provenance | S5 |
| Q10 | `"Eye tracking: empirical foundations for a minimal reporting guideline" Holmqvist 2023 10.3758` | **Retraction audit** | S4 (excluded) |
| Q11 | `"Can EEG Be Adopted as a Neuroscience Reference for Assessing Software Programmers’ Cognitive Load?" DOI` | Programmer reference measurement | S13 |

**Pre-existing named sources:** S1, S2, S3, S4, S5 and S6 were already in the review. A1.3 re-screened their current sources and statuses; it did **not** rerun a systematic retrospective database search for them.

## 3. Named candidate screening (shortlist-only counts)

**Exactly 19 named unique candidates manually tracked across A1.3–A1.4:** **15 included**, **1 excluded (retracted)**, **3 deferred** due to incomplete methodological access or limited fit. A duplicate search appearance of S5 is **not** counted as a new paper.

| Candidate | Source / stable locator | Decision | Verification level | Rationale |
|---|---|---|---|---|
| S1 | https://pmc.ncbi.nlm.nih.gov/articles/PMC7334692/ | INCLUDE | Full text reviewed in prior pass | Programming ocular metrics with independent assessments |
| S2 | https://www.mdpi.com/2076-3417/14/24/11975 | INCLUDE | Full text and statistics verified | Tobii Nano; conflicting abstract versus Results recorded |
| S3 | https://pmc.ncbi.nlm.nih.gov/articles/PMC6138399/ | INCLUDE | Full text and equipment verified | Micro-saccade limitation directly constrains 60 Hz feature scope |
| S4 | https://doi.org/10.3758/s13428-023-02285-0 | EXCLUDE | Publisher retraction notice | Article DOI 10.3758/s13428-021-01762-8 retracted |
| S5 | https://link.springer.com/article/10.3758/s13428-023-02187-1 | INCLUDE | Publisher; correction verified | Still usable eye tracking reporting guideline |
| S6 | https://ietresearch.onlinelibrary.wiley.com/doi/full/10.1049/ccs2.12088 | INCLUDE | Full text | Webcam-vs-tracker blink validation |
| S7 | https://www.medien.ifi.lmu.de/pubdb/publications/pub/weber2023muc/weber2023muc.pdf | INCLUDE | Full PDF; screenshots checked | Direct gaze-adaptive IDE precedent |
| S8 | https://onlinelibrary.wiley.com/doi/full/10.1111/cgf.15271 | INCLUDE | Full text | Adaptive visualization architecture and evaluation review |
| S9 | https://www.eecs.harvard.edu/~kgajos/papers/2009/findlater09design.shtml | INCLUDE | Author abstract/metadata | Adaptive UI evaluation framework; not used for numerical effects |
| S10 | https://www.eecs.harvard.edu/~kgajos/papers/2008/gajos08predictability.shtml | INCLUDE | Author abstract/metadata | Predictability and accuracy; no detailed numerical claims |
| S11 | https://journals.sagepub.com/doi/full/10.1177/00187208261427867 | INCLUDE | Full text | Review of 87 usability workload studies |
| S12 | https://www.cambridge.org/core/journals/design-science/article/designing-adaptive-feedback-systems-for-managing-cognitive-load-in-augmented-reality/B2F5BA55D92F60D587BFDB9EE776BE22 | INCLUDE | Full text | Physiological adaptation outcomes + intervention cost |
| S13 | https://pmc.ncbi.nlm.nih.gov/articles/PMC8037053/ | INCLUDE | Full text | Independent programmer EEG / workload reference |
| D01 | https://www.sciencedirect.com/science/article/pii/S0164121225002675 | DEFER | Abstract/index; full text blocked | Adaptive menu evaluation interesting but direct methods unavailable in this pass |
| D02 | https://www.nature.com/articles/s41598-026-35017-3 | DEFER | Search/abstract; full text access challenge | Specialized manned/unmanned operations; weak desktop transfer |
| D03 | https://journals.sagepub.com/doi/10.3233/FAIA251433 | DEFER | Search snippet/index only | 2026 physiology-adaptive visualization; insufficient method inspection in this pass |
| S14 | https://doi.org/10.1111/bjep.12577 | INCLUDE | Publisher full text | 20 recruited, 19 analyzed eye datasets; task-type and blink/pupil confounds |
| S15 | https://doi.org/10.1080/00140139.2023.2223785 | INCLUDE (limited) | Publisher/PubMed abstract | Perceptual demand alters interpretation of blink metrics; N and hardware not verified |
| S16 | https://doi.org/10.1109/VL/HCC60511.2024.00015 | INCLUDE (limited) | IEEE/DOI abstract | IDE task/workload analogue; N=28 confirmed; full methods not verified |

**Duplicate note:** S5 appeared in publisher, DOI and PMC results, but is *one* guideline. S4 retraction notice is a record *about* S4, not an additional independent study.

## 4. Field extraction and risk decisions

- Extract source ID, authors, publication year, DOI/URL, design, participant count (or `NOT VERIFIED`), controlled task, sensor sampling, ocular or physiological measures, *independent* evaluation, exact finding, limitations, CLOE implication, evidence status and verification level. All fields are in `T01-A1-evidence-matrix.csv`.
- **Numerical audit S2:** Abstract reports r=0.513 for pupil–NASA-TLX but Results §4.2 reports r=0.312 for raw pupil–NASA-TLX, r=0.103 (p=0.11) for adjusted pupil–NASA-TLX, r=0.513 for raw vs adjusted pupil. Do not cite inconsistent abstract value as a workload effect.
- **Equipment audit S3:** N=13 analyzed; EyeLink 500 Hz; authors caution ≥300 Hz for shortest microsaccades; not transferable to Nano 60 Hz detection.
- **Integrity audit S4:** Retraction notice published 2023-11-16; https://doi.org/10.3758/s13428-023-02285-0. Excluded from evidence.
- **Correction audit S5:** Author correction published 2024-04-30: https://doi.org/10.3758/s13428-024-02438-9; adds funding statement; no substantive methods change described.
- **Intervention audit S7:** Visual Studio gaze adaptation is task-context prediction, *not* a validated cognitive-load classifier. PDF pages 267, 273 and 275 inspected.
- **Conceptual audit:** S12 uses electrodermal signal for rest intervention; cannot establish that gaze-based desktop simplification improves accuracy, workload or usability.

## 5. Remaining actions to claim a formal reproducible search

1. Select and explicitly name databases (e.g. ACM Digital Library, IEEE Xplore, PubMed, Scopus), exact field restrictions and search coverage dates; ensure access is available to export results.
2. Run each exact database query on a logged date and capture search-result count, database URL or screen evidence, exported record files and identifier list. Do not mix raw search hit counts from web discovery with database hit counts.
3. Deduplicate by DOI/title, save decision for *every* unique result and exact inclusion/exclusion rationale; record full-text eligibility and the final included set.
4. Run citation chasing using references and forward citations; track method separately.
5. Audit bibliographic details and publication integrity immediately before final hand-in, including publisher retractions and corrections.
6. Reconcile any new included studies with the evidence CSV and claim-register decisions.
7. Obtain supervisor's feedback and commit artifacts.

**Status:** `A1.4 BOUNDED SEARCH & AUDIT COMPLETED WITH ACCESS LIMITATIONS`; `T01-A1 IN PROGRESS (database census + sign-off open)`.


## 6. A1.4 audit run: submitted searches and outcomes (2026-11-19)

**Execution mode:** public web index with searches constrained to publisher/aggregator domains; publisher/abstract cross-checks separately. `fast` and `slow` denote two search-index query modes, **not** direct queries executed inside ACM/IEEE/PubMed. Results listed in the observed-candidate column are examples of actually surfaced named candidates, **not an exhaustive response set**. Search indices cannot provide complete database counts or stable pagination through this interface.

| QID | Exact query submitted | Method | Observed relevant named candidates | Database hit count | Record export |
|---|---|---|---|---|---|
| Q12 | `site:dl.acm.org/doi/ eye tracking cognitive load adaptive interface developer IDE gaze evaluation` | Web domain filter | Related adaptive interface search results; S7 already known | NOT AVAILABLE | NO |
| Q13 | `site:ieeexplore.ieee.org/document/ pupil blink cognitive workload software developer adaptive user interface` | Web domain filter | S16 and related IEEE candidates | NOT AVAILABLE | NO |
| Q14 | `site:pubmed.ncbi.nlm.nih.gov/ eye tracking cognitive load pupil blink review` | Web domain filter | S5; S14 (via separate publisher search); S15 | NOT AVAILABLE | NO |
| Q15 | `site:dl.acm.org/doi/ "Supporting Software Developers Through a Gaze-Based Adaptive IDE"` | Web domain filter | S7 metadata | NOT AVAILABLE | NO |
| Q16 | `site:ieeexplore.ieee.org/document/ "cognitive load" "eye tracking" "adaptive"` | Web domain filter | IEEE adaptation candidates | NOT AVAILABLE | NO |
| Q17 | `site:acm.org "adaptation" "user control" adaptive user interface gaze 2023 2024` | Web domain filter | User control analogues | NOT AVAILABLE | NO |
| Q18 | `site:pubmed.ncbi.nlm.nih.gov/ "Minimal reporting guideline for research involving eye tracking"` | Web domain filter | S5 | NOT AVAILABLE | NO |
| Q19 | `site:doi.org "Cognitive Load Measurement Methods for Usability Testing" 2026` | Web domain filter | S11 | NOT AVAILABLE | NO |
| Q20 | `"Pupillometric and blink measures of diverse task loads" methodology results 2023` | Web search | S14 | NOT AVAILABLE | NO |
| Q21 | `"Recognition and evaluation of mental workload in different stages of perceptual and cognitive information processing using a multimodal approach" Jin full text` | Web search | S15 | NOT AVAILABLE | NO |
| Q22 | `"Developer Behaviors in Validating and Repairing LLM-Generated Code Using IDE and Eye Tracking" DOI participants` | Web search | S16 | NOT AVAILABLE | NO |
| Q23 | `"Cognitive Load Measurement Methods for Usability Testing" Darejeh 2026 87 studies full text` | Web search | S11 | NOT AVAILABLE | NO |
| Q24 | `"Workload Assessment of Operators: Correlation Between NASA-TLX and Pupillary Responses" 0.312 0.513` | Web search | S2 numerical audit | NOT AVAILABLE | NO |
| Q25 | `"Eye tracking: empirical foundations for a minimal reporting guideline" retraction notice 2023` | Web search | S4 integrity check | NOT AVAILABLE | NO |

Other metadata checks were performed via exact-title searches and direct publisher/DOI opening; they were **verification operations**, not independent broad database searches. See included URLs in the CSV.

### 6.1 Dynamic database search attempts

| DB interface | Query attempted (URL or logical syntax) | Access outcome | Observed database result count | Export |
|---|---|---|---|---|
| PubMed | `(eye-tracking OR eye tracking OR pupillometry) AND (cognitive load OR mental workload) AND (blink OR pupil OR fixation)` in PubMed dynamic `?term=` URL | Dynamic result page could not be accessed | UNKNOWN | NOT GENERATED |
| ACM Digital Library | `"eye tracking" "cognitive load"` in `/action/doSearch?AllField=` | Dynamic result page inaccessible | UNKNOWN | NOT GENERATED |
| IEEE Xplore | `"eye tracking" "cognitive load"` in `/search/searchresult.jsp?queryText=` | Dynamic result page inaccessible; some individual article URLs returned HTTP 418 | UNKNOWN | NOT GENERATED |

**DO NOT** turn the above entries into database hit counts or systematic coverage claims. The count of 19 pertains solely to named manually tracked candidate papers (S1–S16 and D01–D03).

### 6.2 Pre-registered proposed direct-database search protocol (NOT executed)

- **Goal:** a bounded *scoping* search, not an assumed exhaustive systematic review. Record each database separately, including query date/time in Europe/Bucharest and its native query syntax. Use English language and publications from **2008-01-01 through 2026-11-19**, excluding post-date publications. Source types: peer-reviewed journal/conference studies, systematic reviews and relevant reporting guidelines.
- **Track A (physiology and reference):** `(eye tracking OR eye-tracking OR pupillometry) AND (cognitive load OR mental workload OR cognitive workload) AND (pupil OR blink OR fixation OR saccade)`
- **Track B (programming and UI):** `(eye tracking OR gaze) AND (programmer OR developer OR "software engineering" OR "program comprehension" OR "adaptive interface" OR "adaptive IDE")`
- **Track C (adaptation evaluation):** `("adaptive user interface" OR "adaptive visualization" OR "adaptive IDE") AND (workload OR usability OR performance OR user control OR interruption)`
- **Field restrictions:** ACM/IEEE Title–Abstract–Keywords where supported; PubMed title/abstract; preserve each engine's actual reformulation and filters in an exported search log; do **not** claim the Boolean syntax is identical between systems.
- **Screening:** title/abstract then full text; include primary empirical studies/rigorous synthesis/guidelines directly relevant to indicators or UI adaptation; exclude unrelated clinical diagnosis, unsupported opinion, pure model performance without external reference, unavailable identity, and retracted papers. Mark abstract-only supporting evidence *limited*, not full-text reviewed.
- **Dedup:** normalize DOI (lowercase, strip DOI URL prefixes); otherwise title/year; retain original row with each source DB, and screening decision with structured rationale; do not merge two different studies merely because titles look similar.
- **Required outputs:** query URL/screenshot with timestamp, total results as displayed by *that database*, raw RIS/BibTeX/CSV export, dedup table, all screening decisions, full-text included set, final evidence extraction. No claim is made that these were produced in the current pass.

### 6.3 Source recheck and change log

- **S2:** MDPI Results §4.2 still distinguishes r=0.312 (raw pupil/TLX), r=0.103 (adjusted pupil/TLX) and r=0.513 (raw/adjusted pupil); discrepancy with abstract documented.
- **S4:** Publisher explicitly marks the article RETRACTED; the publisher retraction notice gives publication date 2023-11-16.
- **S11:** Publisher/PubMed metadata confirm 2026 publication and 87 studies. These are the *authors' review counts*, never CLOE search results.
- **S14:** Publisher Methods confirm 20 participants recruited, 19 usable eye datasets, Pupil Labs eye-video acquisition 60 Hz, 9-point effort rating; Results support task-dependent pupil/blink associations.
- **S15:** Publisher/PubMed abstracts checked; full text not accessible. N and eye-tracker model remain NOT VERIFIED.
- **S16:** IEEE/DOI abstract confirms 28 subjects, three projects and workload assessment; full text/method details not verified.
- **S10:** Missing DOI filled from the author’s Harvard publications record: https://doi.org/10.1145/1357054.1357252. DOI/metadata verified; result interpretation remains abstract-only.

### 6.4 Closure boundary

A1.4 can be labeled **COMPLETED WITH LIMITATIONS** for the **bounded narrative-review audit**; **T01-A1 remains IN PROGRESS** under the previous strict acceptance condition until a library-authenticated full database pass and a supervisor review are recorded. `T01-A1-screening-decisions.csv` contains the 19 named-candidate dispositions, not a complete screen of every search result.
