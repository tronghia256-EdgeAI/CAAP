# Protocol — seed bias in MOT GT (FROZEN 20/10/2026)

_This is an English translation. The protocol and its amendments were written and frozen in Vietnamese; the Vietnamese originals are in the repository history (git log -- docs/PROTOCOL.md)._

Status: **FROZEN 2026-10-20**, approved by Nghĩa. At the time of freezing, no experiment had been run and no
number had been seen. From here on, every change may only be added to the "Amendments" section (dated),
before seeing the results that the change affects.

## 1. Definitions

- `GT_true`: the public GT of the dataset.
- `GT_S(θ)`: simulated GT, created by having a "reviewer" with parameters θ review the output of seed tracker S
  (Section 4).
- `M(T; G)`: the metric of tracker T when scored against GT G.
- Bias: `b(T, S) = M(T; GT_S) − M(T; GT_true)`.
- **Self-seed advantage** of A over B under seed A:
  `SA(A, B) = [M(A; GT_A) − M(B; GT_A)] − [M(A; GT_true) − M(B; GT_true)]`.

## 2. Hypotheses and endpoints

- **H1 (primary):** `SA(A, B) > 0` at the reference parameters θ_ref = (r=0.75, p_fp=0.1, q=0.5, a=1).
  θ_ref was chosen before running; it is an **assumption**, not a measurement, and the paper must state this clearly.
  Primary endpoint: the mean `SA` in IDF1 over all pairs (A, B), with a 95% CI from a sequence-level bootstrap
  (10 000 iterations), reported separately for each dataset. Additionally report, over the whole grid in Section 4, the region of θ where
  the CI excludes 0, so that the conclusion does not depend on a single point θ_ref.
- **H2:** GT errors correlated with the seed reverse rankings more than random errors with the **same number** of
  FN, FP and ID errors. Endpoint: Kendall τ between the ranking on `GT_S` and on `GT_true`, compared with τ on a GT
  with random errors matched in error count.
- **H3:** A debiasing protocol reduces |SA| at a review cost (number of boxes shown to the reviewer) lower than
  full relabelling. Endpoint: the Pareto curve between remaining |SA| and cost.
- Secondary metrics: HOTA@α=0.5, DetA, AssA, MOTA, number of ID switches. HOTA averaged over α is only secondary, because
  the reviewer keeps the seed's box geometry.

## 3. Data, detector, trackers

| Dataset | Part used | Role | Licence (must be rechecked at download) |
|---|---|---|---|
| FastTrack (arXiv 2508.14370) | 12 videos | Main traffic CCTV testbed | OpenRAIL-M (HF); paper CC BY-NC-SA |
| MOT17 | 7 train sequences | Generalisation, has public detections | CC BY-NC-SA 3.0 |
| DanceTrack | 25 val sequences | Generalisation, similar appearance | Labels CC BY 4.0, video non-commercial |

- Detector: YOLO11 pretrained on COCO, not fine-tuned. COCO classes are mapped to the dataset's classes; the
  mapping table is recorded before running. Detection is run once on a Kaggle T4 and then cached; all trackers use
  the same cache (the "shared detector" condition).
- Secondary "different detector" condition: tracker A uses YOLO11x, tracker B uses YOLO11n, to measure the component of
  seed bias that comes from the detector.
- Trackers (published default parameters, fixed before running): SORT, ByteTrack, OC-SORT, BoT-SORT
  (without ReID), and one tracker with ReID (Deep OC-SORT or StrongSORT). Run via `trackers` (Roboflow)
  or BoxMOT; installed for use only, no AGPL code vendored.
- Pipeline sanity check: ByteTrack on MOT17 must deviate by no more than 1 IDF1 point from the published reference number
  for the same detector. If this fails, fix the pipeline before continuing.

## 4. Reviewer model (simulator)

Match the seed output to `GT_true` frame by frame (Hungarian, IoU ≥ 0.5). Then:

| Parameter | Meaning | Grid |
|---|---|---|
| r | Probability that the reviewer adds a GT segment the seed missed (a contiguous segment of one GT id) | 0, 0.25, 0.5, 0.75, 0.9, 1 |
| p_fp | Probability of keeping an FP segment of the seed | 0, 0.1, 0.25, 0.5 |
| q | Probability of correcting an ID error of the seed (switch or fragment) | 0, 0.5, 0.9, 1 |
| a | Probability of keeping the seed's box geometry instead of the GT box | 1 (main), 0 (check) |

- Each cell of the grid is run with 10 random seeds.
- Mandatory check with a synthetic test: with r=1, p_fp=0, q=1, a=0, `GT_S = GT_true` and bias = 0.
  With r=0, p_fp=1, q=0, a=1, `GT_S` = seed output and the seed tracker achieves IDF1 = 1.
- Random errors for H2: the same number of FN, FP and ID-error segments as `GT_S`, but chosen at random, independently
  of the tracker.

## 5. Debiasing protocol (H3)

1. **Union seeding:** seed with the union of the outputs of k ∈ {2, 3} trackers, then review with the same θ.
2. **Blind adjudication:** review only the regions where the trackers disagree; the reviewer does not know which
   tracker a box belongs to (r applies to the disagreement regions).
3. **Bracket bound:** score on `GT_A` and `GT_B`, report the interval. Additional review cost is 0.

Cost: the number of boxes shown to the reviewer, relative to the number of boxes in `GT_true` (the cost of full relabelling).

## 6. Human mini-study — DEFERRED

Nghĩa decided on 20/10/2026: the first submission has no human mini-study. It is done only if reviewers
request it in the revision round. In that case, the fallback design below is used, added to the protocol through an
amendment, and used only to calibrate θ (without changing hypotheses or endpoints):
- 2 people, about 3–4 hours each on CVAT, about 6 clips of 10–20 s from FastTrack and DanceTrack
  (which already have `GT_true`).
- Crossover design seed A / seed B (Latin square). Measure r, p_fp, q, a by comparison with `GT_true`.

Consequence for the first submission: the results rest on simulation. The paper must state this as a limitation and present the conclusions
over the whole θ grid, not only at θ_ref.

## 7. Early stopping rule

If, after running the full grid in Section 4, |SA| < 0.01 IDF1 for every θ with r ≥ 0.5 on all three datasets and there is no
ranking reversal, then change the framing to "tracker-assisted GT is safe when r ≥ X", drop Section 5 and
write a short paper.

## 8. Analysis and reporting

- Every number is generated from a commit; each run has a `provenance.json` (commit, input hash, parameters).
- Output lives in `data/processed/seed_bias/` (gitignored). Only small summary tables are committed.
- No frames, videos or original GT are redistributed; code is released for reproduction.

## Freeze

- 2026-10-20: approved by Nghĩa. Before freezing, the mini-study was deferred to the revision round and θ_ref replaced
  θ\* measured from the mini-study (Sections 2 and 6). The freeze commit is the first commit containing the line
  `FROZEN 2026-10-20`: `git log --format=%h -S "FROZEN 2026-10-20" -- docs/PROTOCOL.md`.

## Amendments

### A1 — 20/10/2026, before any results were available

**Rationale.** A critical review of the first simulator version (3 independent strands) found that the model in Section 4, when
interpreted link by link, pulls GT_S towards the seed at every 0 < q < 1. Examples: a single correction of an
"excursion" error has no effect; a swap is fully corrected only with probability about q⁴. This effect increases SA
by about 0.01 IDF1, on a par with the stopping threshold in Section 7. The points below replace the interpretation of Section 4; the
hypotheses, endpoints, θ grid, θ_ref and stopping rule remain unchanged.

1. **Box matching.** Hungarian per frame, only over pairs with IoU ≥ 0.5 (machine-epsilon tolerance,
   as in TrackEval), filtered before assignment.
2. **Identity.** One-to-one matching of seed id ↔ GT id by Hungarian on the number of matched boxes (as in IDF1).
   `label(g)` = the seed id matched to g, or a new label if g is unmatched.
3. **ID-correction unit = episode.** A (seed id, GT id) pair outside the identity matching is an error pair.
   Error pairs whose corrections would collide with each other in the same frame (e.g. the two halves of a swap) are merged into one
   episode. Each episode is corrected with probability **q**, drawn once: if corrected, all its boxes receive
   `label(g)`; otherwise they keep the seed id. By construction, the output is always valid; no conflict rule remains.
4. **Run.** Missed segments and FP segments are **frame-contiguous** segments of one id. A frame gap
   splits a run.
5. **Labels of added/kept boxes.** An added missed segment receives `label(g)`, or a new label if `label(g)` is already
   used in a frame of the segment. A kept FP segment receives its seed id, or a new label if it collides.
   **An added GT box replaces** an unmatched seed box overlapping it (IoU ≥ 0.1) in the same frame: the reviewer
   corrects the misplaced box rather than keeping both.
6. **Geometry a.** Drawn per matched box.
7. **Input.** Frame/id must be integers, (frame, id) unique, all values finite. Input is sorted
   into a canonical order, so the result does not depend on the row order in the file. Fixed order of random draws:
   episodes (by first frame), missed segments, FP segments (by id, then first frame), geometry.
8. **Common preprocessing.** GT_true and every tracker output pass through **the same** filtering step, before simulation
   and before scoring, so that GT_true and GT_S are scored identically:
   - MOT17: GT_true is the rows with consider = 1 and class = 1. Tracker boxes matched (IoU ≥ 0.5) to a
     distractor GT (class 2, 7, 8, 12) or consider = 0 are removed once, following TrackEval's rule exactly.
     Scoring is then done without the distractor step.
   - FastTrack: class 9 (`ignore_region`) and classes 10–15 are ignore regions. Tracker boxes whose centre lies
     inside an ignore region in the same frame are removed.
9. **Detection (Section 3).** The shared detector is YOLO11x pretrained on COCO. The "different detector" condition uses
   YOLO11n. imgsz 1280, conf ≥ 0.05, ultralytics 8.4.92, script `tools/kaggle_detect_cache.py`.
   MOT17 uses YOLO11 detections on the images of the `*-FRCNN` folders, not the public detections.
   Class mapping (COCO → FastTrack, 1-based numbering following `labels.txt`):

   | Evaluation class | FastTrack | COCO |
   |---|---|---|
   | person | 1 | 0 person |
   | bus | 2 bus_small, 3 bus_big | 5 bus |
   | truck | 4 truck_small, 5 truck_big | 7 truck |
   | car | 6 | 2 car |
   | bicycle | 7 bike | 1 bicycle |
   | motorbike | 8 | 3 motorcycle |

   MOT17 and DanceTrack have person only.
10. **Diagnostics reported alongside** (from the methods review): the actual correction rate by episode size; SA
    at a = 0 next to a = 1 (separating the identity part from the geometry part); sensitivity to the match threshold 0.4 / 0.6
    (at θ_ref only); the distribution of missed-segment lengths for each seed tracker; the variance across random seeds
    within each grid cell.

### A2 — 20/10/2026, before any results were available

Fixes the details of running trackers and scoring (Sections 3 and 8), after having looked at the libraries' APIs:

1. **Trackers.** Roboflow `trackers` 2.6.1, the library's default parameters, `frame_rate` taken from
   `seqinfo.ini`. Run separately for each evaluation class. ByteTrack, OC-SORT and BoT-SORT receive all
   cached detections (conf ≥ 0.05) and apply their own thresholds. **SORT** receives only detections with
   conf ≥ 0.25 (its activation threshold), because SORT has no low-score stage. **BoT-SORT has CMC disabled**, because
   no images are available when running offline. The tracker with ReID runs on Kaggle at a later step and will be fixed by a
   separate amendment before running.
2. **MOT17 preprocessing exactly as in TrackEval.** Only tracker boxes matched (Hungarian, IoU ≥ 0.5) to GT
   of distractor classes 2/7/8/12 are removed. Boxes matched to pedestrian GT with consider = 0 are **not** removed (correcting
   the phrase "or consider = 0" in A1 item 8 to match TrackEval's rule). GT_true is consider = 1 and
   class = 1.
3. **Metrics.** Official TrackEval @12c8791 (JonathonLuiten), calling the HOTA,
   CLEAR and Identity metric classes directly on in-memory data. The aliases `np.float`/`np.int`/`np.bool` that numpy 2
   removed are restored before import. The bridge must give results identical to TrackEval's official file-based
   Evaluator (absolute error ≤ 1e-12, with a test). This check **replaces the sanity check in
   Section 3** ("ByteTrack on MOT17 deviates ≤ 1 point from the published number"), because no reference number has
   been published for this COCO YOLO11 detector.
4. **Units.** Each (sequence, class) is one scoring unit. Dataset-level metrics are aggregated in TrackEval's way
   (`combine_sequences`). The bootstrap resamples by **sequence**, each sequence carrying
   all of its classes.
5. **Storage.** Preprocessed tracks are in `data/processed/tracks/`. `provenance.json` records the commit,
   the uncommitted-changes state, library versions and the hash of every input detection/GT file.

### A3 — 20/10/2026, before any results were available

Fixes the computation and analysis of H1 and the ranking part of H2 (`code/seedbias/experiment.py`):

1. **Seeds and scored trackers** are both the four trackers of A2 (shared detector YOLO11x). Each tracker in
   turn serves as seed A. SA is computed for every ordered pair (A, B) with A ≠ B.
2. **IDF1 on GT_S** is computed exactly following TrackEval's Identity: count same-frame pairs with IoU ≥ 0.5
   (IoU computed with TrackEval's function), then find the id matching with the largest total. IoU pairs are computed
   once with the GT boxes and the seed boxes, because every box of GT_S carries the geometry of one of the two. A mandatory test requires
   IDTP to be identical to the TrackEval bridge on simulated GT.
3. **Common random numbers.** The simulator's random seed is (k, A, unit) with
   k = 0..9, **identical in every θ cell**, so differences between cells are not confounded by different draws.
4. **H1 endpoint** = mean SA (IDF1) over all ordered pairs and over the 10 random seeds, computed at the
   dataset level (summing IDTP and box counts over all units). The 95% CI is the percentile interval of 10 000 bootstrap
   resamples of sequences (bootstrap seed fixed at 0). Each θ cell is computed the same way; "the region where the CI excludes 0" is the set of
   cells with lower bound > 0.
5. **H2, ranking part.** For each (A, θ, k): Kendall τ-b (scipy) between the trackers' IDF1 on GT_A and on
   GT_true, and the number of tracker pairs whose order is reversed. Report the mean τ, the mean number of reversed pairs, and the proportion of
   draws with at least one reversed pair. The comparison with random errors (null model) will be fixed in a later
   amendment, before running.
6. **Secondary metrics** (HOTA@0.5, DetA, AssA, MOTA, IDSW) are computed with the full TrackEval bridge, at θ_ref only,
   with all 10 random seeds.

### A4 — 20/10/2026, before any results were available

Fixes the H2 null model, the set of scored systems, and the operational definition of H3 (Section 5):

1. **Set of systems.** 8 systems = 4 trackers × {YOLO11x, YOLO11n}. The seeds remain the 4 YOLO11x systems.
   The H1 endpoint (A3 item 4) is unchanged: it includes only pairs (A, B) both using YOLO11x. Pairs (A YOLO11x,
   B YOLO11n) are reported separately as the detector component of seed bias (Section 3, the "different
   detector" condition). Rankings for H2 (τ, number of reversed pairs) are computed over all 8 systems.
2. **θ slice for the expensive analyses.** S_r = {θ_ref with r replaced by each value in the grid}, 6 cells,
   including θ_ref. The H2 null model and the H3 protocols run only on S_r, with 10 random seeds.
3. **H2 null model.** For each draw of GT_S (A, θ, k, unit), build GT_R from GT_true, with the same random
   seed:
   - For each missed segment not added in GT_S, of length ℓ: delete a segment of ℓ consecutive boxes at a
     random position on a random GT track (not yet deleted), if the track is still long enough.
   - For each uncorrected ID-error pair, of n boxes: choose a random segment of n consecutive boxes on a random
     track. If the seed id of that error pair still lies on another object (merge type), assign this segment the id of
     another track not present in those frames; otherwise (fragment type), or if no suitable track exists,
     assign a new id.
   - For each kept FP segment, of length ℓ: copy a random segment of ℓ consecutive boxes of a GT track, shifted
     to another random time in the sequence (shift ≠ 0, within [1, n_frames]), with a new id.
   - The geometry of the remaining boxes is the GT's (a = 0), to compare structural errors with structural errors. The part of SA coming from
     geometry is reported separately via a = 0 / a = 1 (A1 item 10).
   - **H2 endpoint** at θ_ref: mean of (τ_null − τ_seed) and of (number of reversed pairs of seed − of null) over
     (A, k), paired by the same (A, θ, k). 95% CI by sequence bootstrap as in A3. The remaining cells of S_r are
     reported as curves.
4. **H3 protocols** (on the 4 YOLO11x systems only, in alphabetical order of tracker name):
   - P0, single seed: as in H1.
   - P1, union seeding, k ∈ {2, 3}, every combination of k systems: union of outputs in a fixed order; in each
     frame, a box of a later system is dropped if it matches (Hungarian, IoU ≥ 0.5) a box already in the union. Ids
     are kept separate per system, geometry is kept unchanged. Review is then simulated with the same θ.
   - P2, **consensus seeding** (the operational version of "blind adjudication"): a consensus box is a box that all 4
     systems have (chained IoU ≥ 0.5 match with the box of the first system). Its geometry is the mean of the
     boxes, so it is not identical to the geometry of any system. Two consensus boxes in two consecutive frames are linked
     if and only if every system keeps the same id on both. Disagreement boxes are not seeded; the reviewer adds
     them as missed segments with probability r.
   - P3, bracket: for each system T, the interval [min_A M(T; GT_A), max_A M(T; GT_A)] over the 4 single-seed GTs.
     Report the width and the proportion of intervals containing M(T; GT_true). The cost equals the total cost of the single-seed GTs
     (correcting the sentence "additional review cost is 0" in Section 5).
   - **H3 criterion** for every protocol: pairwise distortion
     D = mean over ordered pairs (A, B) of |[M(A; GT_P) − M(B; GT_P)] − [M(A; true) − M(B; true)]|
     (IDF1, 4 YOLO11x systems). For P1, additionally report the SA of members relative to systems outside the set.
     **Cost** = number of boxes shown to the reviewer (seed boxes + disagreement candidate boxes in P2), divided by the number of boxes
     of GT_true. The result is a Pareto curve (cost, D) at θ_ref, with a sequence-bootstrap CI for D.

### A5 — 20/10/2026, before any results were available

**Rationale.** The second critical review (3 strands, on commit 139dea1) found no computational error that would invalidate
SA: the fast IDF1, the bootstrap and the common random numbers were all rechecked against brute-force implementations. However,
the review identified several methodological points that must be fixed before seeing the numbers:

1. **H1 is a statement about magnitude.** The reviewer model only pulls GT towards the seed, so SA ≥ 0 almost by
   definition. The sign of SA is not evidence. H1 is restated as: **SA ≥ δ, with δ = 0.01 IDF1**, at
   θ_ref, assessed by the lower bound of the confidence interval (item 2). The θ-region map reports both: lower bound > 0
   and lower bound > δ. The paper must state clearly that SA ≥ 0 is a consequence of the model; the scientific content lies in the magnitude.
2. **Confidence intervals.** With 7–25 sequences, the percentile interval has coverage below 95% (the review's simulation:
   84–91%). The primary interval is **BCa**: sequence bootstrap with 10 000 iterations, acceleration from a
   leave-one-sequence-out jackknife. The percentile interval and the leave-one-sequence-out interval are reported alongside. The interval for
   MOT17 (7 sequences) is labelled approximate.
3. **Thresholded ranking reversals.** A pair is counted as reversed only when that pair's IDF1 gap on GT_true
   exceeds δ, so that near-tied trackers (e.g. BoT-SORT without CMC and ByteTrack) do not add noise.
   τ-b is unchanged. The H2 endpoint (A4 item 3) uses the number of thresholded reversed pairs. **The stopping rule in Section 7** is
   restated: the BCa upper bound of SA < δ for every θ with r ≥ 0.5 on all three datasets, and no thresholded
   reversed pair.
4. **Diagnostics reported alongside, at θ_ref:** SA per sequence and the unweighted mean; the
   leave-one-sequence-out interval; SA per class; the full SA(A, B) matrix and SA with pairs involving SORT removed;
   SA at a = 1 versus a = 0, for same-detector pairs and different-detector pairs. With a shared detector, every tracker
   returns the detection boxes unchanged, so geometry makes no difference. The meaningful geometry measurement lies in the
   different-detector pairs, and the paper must state this clearly.
5. **Class confusion (FastTrack).** For each class, measure the proportion of seed boxes that do not match GT of the same class but match
   (IoU ≥ 0.5) GT of another class in the same frame; count the units without GT and the proportion of tracker boxes
   falling in them. If a class's confusion rate is > 10%, the paper reports SA with that class removed, and runs an additional
   sensitivity analysis with car + bus + truck merged into one "vehicle" class.
6. **FastTrack ignore regions** (correcting A1 item 8): a tracker box whose centre lies inside an ignore region is removed only when
   it does **not** match (IoU ≥ 0.5) a GT_true box of the class being scored in that frame, close to TrackEval's
   region-ignore rule. Each sequence must have a `labels.txt` consistent with the mapping table in A1 item 9;
   otherwise stop.
7. **MOT17** uses exactly TrackEval's formulas, including the orientation of the matching matrix (GT × tracker, GT in
   file order). A test compares against the official Evaluator with `DO_PREPROC=True`, on data deliberately
   constructed to contain ties.
8. **Cache and provenance.** Tracks are keyed by input hash, source-code hash and library versions, and
   are regenerated automatically when the key changes. Experiment results are checkpointed per (seed, unit), in a directory keyed
   by code + input + grid. `provenance.json` records the commit of this repository and the uncommitted-changes flag.
9. **Metric scope.** Conclusions over the whole θ grid and conclusions about rankings use IDF1 only. HOTA conclusions are only
   at θ_ref.
10. **SORT sensitivity.** At θ_ref, additionally run SORT receiving all detections (conf ≥ 0.05) as a secondary
    system, to measure the effect of the 0.25 threshold in A2. The endpoints are unchanged.

### A6 — 20/10/2026, before any results were available

**Rationale.** The third critical review (null model, H3 protocols, statistics, scope of conclusions; on commit
8540728) confirmed that the statistics match brute-force implementations, but found design problems in H2 and
H3. The points below replace the corresponding parts of A4 and A5.

1. **H2 compares structural errors with structural errors.** The H2 endpoint and the S_r curves use the **a = 0** cells, because GT_S
   then carries GT geometry like the null model. The null does not depend on a: thanks to common random numbers, the same
   draw yields the same structural errors at a = 0 and a = 1. The difference at a = 1 is reported alongside, labelled
   "structure + geometry".
2. **The null model matches the error counts in full.**
   - Units without GT_true boxes are excluded from H2 on both sides, because the null cannot place their FPs.
   - Errors are placed in order of longest segment first.
   - An FP copy must not coincide (IoU ≥ 0.5) with any GT_true box in the new frame; if it does, a different segment
     or shift is drawn, up to 100 times, before skipping.
   - The merge branch uses only labels free in every frame of the segment, so (frame, label) is always unique (with a
     check).
   - Missed segments that GT_S assigns a new label are also transferred to the null as a fragment.
   - The number of skipped error boxes is reported by type (FN, ID, FP), as a proportion of the number requested. If
     a type exceeds 1%, the paper states this clearly and treats that dataset's H2 endpoint as approximate.
3. **P1 (union seeding) is not run as a protocol.** With a shared detector, every tracker returns the detection boxes unchanged,
   so the union of the outputs is exactly identical to the output of the first member (verified by the review).
   P1 therefore coincides with P0 of that member. The paper reports this as a finding: union seeding has no
   effect when the trackers share a detector.
4. **P2 consensus, redefined.**
   - Consensus boxes as in A4.
   - A consensus box is linked to the nearest subsequent consensus box, within **30 frames**, on which a **majority** of
     systems (3/4, or 2/3) keep the same id. This way a tracker breaking a track or a detection gap does not break
     the track.
   - Non-consensus boxes are deduplicated across systems (Hungarian, IoU ≥ 0.5) and shown as
     anonymous candidates.
   - Candidates that do not match GT_true are included as FP segments (by the originating system's id, frame-contiguous),
     kept with probability p_fp. Correct candidates that are real objects are added by the reviewer with probability r,
     as missed segments.
   - Run P2 on all 4 YOLO11x systems, and on each set of 3 systems (leave-one-out). The excluded system
     is a generalisation test: the SA of the members relative to it is reported.
5. **H3 criterion.**
   - D is computed on the 4 YOLO11x systems (primary) and on all 8 systems.
   - Report the SA of members relative to the 4 YOLO11n systems.
   - **"Bias reduction" criterion:** the BCa upper bound of the paired difference D_P − D_P0 (same bootstrap columns) < 0
     at θ_ref, with D_P0 the mean over the 4 single seeds.
   - P3 bracket: report the coverage for each system, with a sequence-bootstrap CI.
6. **Cost has two parts, not combined:** (i) boxes to check = seed boxes (P2: plus the deduplicated
   candidates); (ii) boxes to draw anew = the number of boxes of the missed segments added by the reviewer (depends on r). Both are divided
   by the number of boxes of GT_true. Full relabelling corresponds to (0, 1). "Cheaper than full relabelling" may be written only
   when both parts are stated.
7. **Scope of conclusions.**
   - Confirmatory conclusions are only at θ_ref and separately for each dataset.
   - To state H1 in general, all three datasets must pass (intersection-union, no correction needed).
   - The 192-cell θ map is descriptive only, with pointwise CIs.
   - The three datasets are not pooled into one.
8. **The diagnostics committed in A1 item 10 now have running code:**
   - the actual correction rate by episode size at θ_ref;
   - sensitivity to the match threshold 0.4 / 0.6 at θ_ref (scoring IoU remains 0.5);
   - the distribution of missed-segment lengths for each seed;
   - the standard deviation across the 10 random seeds in each cell.
9. **BCa** compares ties with a rounding tolerance (1e-12) and takes quantiles by linear interpolation, as
   `np.percentile` does.

### A7 — 20/10/2026, before any results were available

**Rationale.** The verification pass on the A6 fixes (commit 6063de3) confirmed that the statistics and the wiring in
`main()` match brute force, and that the null-model fixes are all correct. However, this pass found a crashing bug
(`_run_seed` failed on units where the seed missed no box, including units without GT) and two mechanisms that left P2
still biased.

1. **P2 consensus, redefined again** (replacing A6 item 4, the parts on box coverage and track linking):
   - Boxes are clustered across systems, frame by frame (IoU ≥ 0.5). A cluster supported by a **majority** of systems
     (3/4, or 2/3) is a consensus box, with geometry the mean. All systems are no longer required: an
     intersection-type consensus would inherit all the missed boxes of the system with the lowest coverage.
   - Each system present on a consensus box casts one vote for the nearest subsequent consensus box (≤ 30
     frames) on which it keeps the same id. The box receiving the most votes is linked if it has **at least 2 votes** and a strict
     relative majority. A system that breaks the id casts no vote against, so two trackers both breaking a track do not break
     the consensus when the other two trackers still link it.
   - Candidates are the clusters without a sufficient majority, one box per cluster, with the id taken from the originating system. A candidate is
     considered an FP only when it does not overlap (IoU ≥ 0.5) **any** GT_true box in the frame, not based only on
     a one-to-one matching.
2. **Null model, scope of the claim.** The null matches the **number of boxes** of FN, ID and FP errors in each draw of GT_S.
   A kept FP segment in GT_S can carry the label of a real track (a kind of merge via an FP tail); the null
   cannot reproduce this kind of error. The proportion of such FP boxes is reported for each cell of S_r. The paper must
   not state that the null matches "all errors".
3. **Crash fix.** The missed-segment-length histogram uses an integer-typed array. The end-to-end test now has a unit
   without GT and a unit whose seed is identical to the GT.

### A8 — 21/10/2026, after the H1, H2 and P2 results were available (disclosed explicitly)

**Rationale.** The manuscript review found that the reason for dropping P1 in A6 item 3 is **wrong on real data**. Matching boxes
do have the same geometry (99.6–100%), but each tracker outputs a different subset of the detections. Therefore the
deduplicated union has more boxes than the first member: 1.45 times (MOT17), 1.06 times (DanceTrack, first 6
sequences), 1.40 times (FastTrack). A8 withdraws that reason.

1. **P1 is run** exactly as defined in A4 item 4: every combination of 2 and 3 YOLO11x systems, union in alphabetical
   order, on S_r, 10 random seeds. Report D, ΔD, the SA of members relative to YOLO11n and relative to systems outside
   the set, together with the two-part cost. Because P1 is run **after** H1, H2 and P2 had been seen, the paper must state this order clearly.
   The definition of P1 is unchanged from A4, so there is no new analytical degree of freedom. The P1 results must not be used to
   choose or change the other analyses.
2. **Exploratory analyses after seeing the results**, labelled exploratory in the paper:
   - τ among the 7 non-seed systems, with CI;
   - "kin bias" (the YOLO11n system with the same algorithm as the seed);
   - the near-linear relationship of SA with q;
   - SA per seed versus the seed's true IDF1;
   - the deviation among the non-seed trackers;
   - IDSW.
3. **Deviations from the protocol, disclosed in the paper:**
   - The tracker with ReID (Section 3) was not run. Reason: it requires images on a GPU, and BoxMOT has an opencv version
     conflict on the machine. All conclusions apply only to the four motion-based trackers.
   - Human mini-study deferred (Section 6).
   - H1 restated as a magnitude test (A5).
   - The H3 endpoint replaced by ΔD (A4, A6).
