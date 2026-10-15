# Research verdict

**15 October 2026. CONDITIONAL GO — feasibility only.**

The repository demonstrates an important bottleneck: changing detector operating
points changes tracking more than several tracker modifications. It does not yet
demonstrate that identity-directed crops solve that bottleneck within a useful CPU
budget. Nor does it establish novelty for a generic uncertainty scheduler.

## What is promising

1. Small-object misses are large enough to make selective refinement worth testing.
2. There is a reusable, provenance-aware evaluation system, reviewed ROI GT, multiple
   detector resolutions and strong motion-only baselines.
3. A spatial action can cover competing identities together. Testing **which action
   changes an association outcome**, rather than merely which track looks unreliable,
   is a falsifiable research question.

These are motivations, not proof of effectiveness or publishability.

## What is already unavailable as a novelty claim

Adaptive resolution, selective high-resolution processing and confidence-aware MOT
workload scheduling have prior art. The closest 2026 threat is [P01 in the literature
review](02_PRIOR_ART.md#p01--driftsched-2026-closest-threat). A covariance/ambiguity
score followed by budgeted detection is not an adequate standalone contribution.

The remaining **hypothesis**, subject to full-text comparison, is:

> Estimate the incremental association benefit of a joint image-region refinement,
> account for competing tracks and discovery, and choose spatial actions using
> measured end-to-end CPU slack; demonstrate improvement over cost-matched
> uncertainty, confidence, density and fixed-region policies.

Neither a weighted risk sum, a greedy knapsack nor concatenating established modules
is new by itself. If the closest method already covers this formulation, stop or
change direction before a full implementation.

## What the existing evidence says

The audited reference is `experiments/paper_final/best85_roi_final/`, not the failed
v4 run or the superseded v5 C1 results. Motorcycle IDF1 on Dense:

| Input | ByteTrack baseline | C2 | OC-SORT matched |
|---|---:|---:|---:|
| 448 | 0.4769 | 0.4994 | 0.5512 |
| 640 | 0.5896 | 0.6023 | 0.6258 |
| 960 | 0.6851 | 0.6978 | 0.6918 |
| 1280 | 0.7242 | 0.7641 | 0.7274 |

These are existing repository scores, conditional on biased development GT. They
justify considering OC-SORT as the initial backbone at low resolution, not claiming
it wins every metric, resolution or scene. AssA on Mixed/640, for example, is higher
for baseline than matched OC-SORT despite OC-SORT's higher IDF1.

C3's scored output equals its raw output in the inspected final runs. The OC-SORT
plus CTRV experiment has no clear primary Mixed benefit and adds Dense switches.
C1 can switch regimes without delivering consistent gains. Retire these modules
from the new paper's novelty narrative, while retaining their artifacts.

## Five scientific risks

| Risk | Consequence | Evidence required to proceed |
|---|---|---|
| Close prior art | A renamed existing scheduler | Full-text mechanism comparison and executable strongest control |
| High risk is not recoverable risk | Crop budget spent on fully occluded/absent objects | Counterfactual action-benefit experiment F3 |
| CPU call overhead | A tiny crop can cost almost a full detector call | F2 with actual tensor shapes and complete pipeline timing |
| Seed-dependent GT | Apparent benefit reflects annotation membership | Multi-source adjudication plus blind exhaustive-area audit |
| No locked camera | Same-camera tuning reported as generalization | Independently reviewed, camera-disjoint locked test |

## Three corrections to the starting narrative

- Masking is not uniformly harmful: at best.pt/1280 Dense, C2 IDF1 is **0.7641
  masked versus 0.7417 unmasked**. A refinement changes context and confidence,
  not only visible object pixels. Keep the mask policy identical across methods.
- The often quoted 99% small-object miss figure is a **tracker-output miss rate**
  in one operating-point analysis. Detector recall requires its own detections and
  one-to-one matching. Do not interchange the two.
- `COMPLETED` with `requested_phase: score` does not establish completed latency.
  The four inspected final/reference/mask-ablation run roots have no final
  `benchmark.json` or active benchmark trial JSON files. No new FPS claim is justified.

## Recommendation

Primary direction: **budget-aware active perception system**, conditional on a
demonstrable spatial action benefit beyond simpler allocation. Backup: a carefully
designed empirical study of resolution, ROI context and annotation bias; it still
needs broader data and controlled timing to justify a journal submission.

The existing 1,800 frames support development feasibility, not a strong Q1 claim.
The old submission explicitly parked independent-camera GT on 13 October. This new
master prompt asks for a strategy to add it; the plan recommends that additional
work but does not silently restart or certify those annotations.

Novelty potential: limited and conditional. Demonstrated new-method novelty: **none**.
Experimental readiness: useful infrastructure, substantial GT/timing gaps.
Publication readiness: **not ready**. No acceptance probability is estimated.

Read [the gates](06_GO_NO_GO.md) before scheduling eight weeks of work. If F1 or F2
fails, do not build M1–M3 in full. If F3 shows only detection gains, revise the claim
to a detection-efficient system or use the empirical backup.
