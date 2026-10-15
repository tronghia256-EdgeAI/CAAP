# Publication strategy and claim boundaries

**Recommendation:** pursue **B, a budget-aware active perception system**, only
after the feasibility gates. Backup **C, an empirical evaluation study**. Do not
position the current work as **A, a new MOT algorithm** merely by wrapping OC-SORT
or transplanting a motorcycle filter that did not improve its strongest reference.

## Why this positioning

| Direction | Fit to current evidence | What would make it defensible |
|---|---|---|
| A: new MOT algorithm | Weak: current C1/C2/C3 evidence is mixed/null and strongest baseline integration is negative | A distinct association model with broad benchmark gains beyond current scope; not the proposed MVP |
| B: budget-aware active perception | Plausible research question; novelty occupied in broad form | Demonstrated action-benefit distinction, spatial allocation controls, fair complete CPU costs and camera-disjoint results |
| C: empirical resolution/context/GT study | Closest to evidence already present | Independent GT/data, factorial isolation, strong tracker coverage and controlled timing; transparent generalizable findings beyond one camera |

No route is currently submission-ready, and none has an evidence-based acceptance
probability. Avoid treating Q1 as a property of an attractive title or complex diagram.

## Working titles

Primary, deliberately avoiding an unproved real-time claim:

**Action-Conditioned Spatial Refinement for Budget-Constrained Multi-Object Tracking**.

If 40 ms end-to-end and live queue behavior are actually demonstrated, a subtitle
can identify real-time motorcycle-dominant traffic on the measured CPU. Broader
"CPU-only edge devices" claims need more than one laptop configuration or must be
qualified to that device.

Backup:

**Detection Scale, ROI Context and Annotation Membership in CPU Traffic Tracking:
A Controlled Multi-Camera Study**.

Both are hypotheses about a future paper. Preserve `paper/jrtip/main.tex` unchanged
in this planning phase and distinguish the existing submission from a new direction.

## Problem and mathematical core

Given a source frame and causal track state, choose a set of spatial detector
actions to reduce identity loss while respecting an end-to-end service constraint:

`maximize E[ L_ID(no refinement) - L_ID(A_t) | I_t ]`

`subject to measured/predicted complete cost(A_t) <= B`,

with fixed discovery coverage and a single committed tracker update. The formulation
is not itself novel; its empirical/action-estimation content must distinguish it
from [the closest mechanisms](02_PRIOR_ART.md). The method proposal's coverage
surrogate is not a theorem about actual HOTA or optimal information gain.

## At most three candidate contributions

1. **Action-conditioned identity benefit:** a simple, calibrated way to distinguish
   useful spatial refinement from generic failure risk, including competing-track
   region coverage. Keep only if its isolated ablation passes and prior art does not
   already establish the same contribution.
2. **Causal budgeted integration:** a reusable spatial action/one-update protocol with
   measured CPU accounting and discovery safeguards. This may be an engineering
   contribution supporting item 1, not an independent novelty claim.
3. **Evidence package:** independent, versioned traffic GT and a cost-matched study
   separating association benefit, recall, source context and annotation uncertainty.
   Its public release depends on confirmed rights; private footage plus code alone
   weakens reproducibility and must be stated.

If only item 3 survives, write the empirical backup and remove algorithmic claims.
Do not count C1, C2, C3, geographic location, YOLO integration, a greedy optimizer
or CPU deployment as separate new contributions without direct comparative evidence.

## Related-work positioning

Organize by mechanism, not by a list of traffic applications:

- active sensing and tracking-informed observation selection;
- temporal detector/workload/resolution scheduling;
- spatial coarse-to-fine inference and slicing;
- uncertainty/association-aware tracking;
- measured real-time system constraints and annotation validity.

Use the evidence levels in the literature catalog. A hardware change or replacing
the word confidence with identity risk is not an algorithmic distinction. P01 full
text remains necessary before a "unlike prior work" sentence about spatial actions.

## Essential ablations and outputs

Essential controls: fixed/full resolutions; fixed/periodic crops; fixed SAHI-style
slicing; density/confidence/scale/gap; random cost-matched actions; covariance and
overlap; risk-only versus action-conditioned value; discovery reserve; same fuser;
OC-SORT and ByteTrack. Include the strongest accessible prior scheduler or label an
honest proxy, and make any inability to reproduce it explicit.

| Planned figure | Claim it would support |
|---|---|
| 1. Causal architecture with decision-time information | No future GT, duplicate update or hidden inference |
| 2. HOTA/AssA/IDF1 versus end-to-end p95/mean, per camera | Accuracy–compute improvement, not detector-only FPS |
| 3. Native scale and ROI-edge recall/identity breakdown | Where image information is recoverable |
| 4. Risk calibration versus action-benefit scatter/enrichment | High risk is distinct from useful refinement |
| 5. Complete stage costs, queue and thermal traces | Actual deployment feasibility and overhead |
| 6. Blinded successes **and failures**, fixed event selection | Mechanism and failure analysis without cherry-picking |

| Planned table | Required content |
|---|---|
| 1. Prior-art mechanism matrix | Signals, action granularity, objective, hardware, cost controls, evidence status |
| 2. Dataset/split/annotation ledger | Cameras/sessions, trajectories/events, tiny objects, audit agreement, rights/provenance |
| 3. Main locked comparison at registered budget | Official per-sequence metrics, actual cost, strongest controls, paired uncertainty |
| 4. Scheduler/features/fusion/discovery ablation | All decisions selected on development; no GT-based test tuning |
| 5. Backbone/detector transfer and annotation sensitivity | Conditional results, limits and negative cases |

## Journal shortlist: scope verified, current Q1 eligibility not certified

Quartiles depend on **index, category and year**. JCR/JIF Q1 and SCImago/SJR Q1 are
not interchangeable. Direct SCImago/Scopus access was blocked in this review; an
institutional current JCR record was not available. Search aggregators differ in
index/category presentation. Therefore the table is a **scope shortlist**, not a
verified list of current Q1 journals. No unverified numerical journal metrics are used.

| Venue | Evidence of topical fit | Recommendation / missing condition |
|---|---|---|
| IEEE Transactions on Intelligent Transportation Systems | [Official society journal page](https://ieee-itss.org/pub/t-its/) | Primary application-oriented candidate if independent traffic evidence and clear new system benefit exist; verify institution-accepted Q1 category/year |
| IEEE Transactions on Circuits and Systems for Video Technology | [Official scope](https://ieee-cas.org/publication/tcsvt) covers video algorithms/systems and implementation | Strong candidate if spatial computation/identity mechanism is technically distinct and reproducible; generic crop wrapper is too weak |
| Journal of Real-Time Image Processing | [Official aims/scope](https://link.springer.com/journal/11554/aims-and-scope) emphasizes real-time processing | Natural systems/empirical fallback if sustained end-to-end timing is central; existing template does not certify Q1 under the required index |
| IEEE Transactions on Image Processing | [Official scope/reproducibility guidance](https://signalprocessingsociety.org/publications-resources/ieee-transactions-image-processing/about-transactions-image-processing) | Not the current first choice: needs a stronger generally applicable algorithmic contribution and broader evidence than application-specific integration |

Before submission an author/advisor should record the exact index, edition,
category, quartile and official source/export, plus current author guidelines.
[SCImago record attempted](https://www.scimagojr.com/journalsearch.php?q=4900152415&tip=sid)
and [Scopus source record](https://www.scopus.com/sourceid/4900152415) were not readable
via the research browser. Do not claim a paywall-blocked check passed.

## Likely rejection reasons and their remedies

| Likely objection | Evidence needed, not a wording fix |
|---|---|
| Existing scheduler renamed | Exact closest-work comparison and isolated technical advantage |
| More compute produces more detections | Strong cost-matched full-frame/crop controls, overhead included |
| No identity-specific effect | AssA/event continuity and comparable-recall analysis, not just DetA |
| Seed-selected truth | Symmetric proposal review, blind exhaustive-area audit, independent adjudication |
| Only one short camera | Locked camera expansion, sequence diversity and restrained inference |
| Real-time claim from throttled or partial timing | Complete valid sustained trials, queue/miss reporting, no omitted stages |
| Unfair baseline | Same detector/scope/fuser/backend and documented native class/birth/association rules |
| Geographic novelty / untested downstream benefits | General mechanism; remove unsupported accident-control or safety claims |
| Missing rights or inaccessible evidence | Verified provenance and a realistic reproducibility/data-availability statement |

## What is and is not ready

| Dimension | Assessment |
|---|---|
| Novelty potential | Conditional, narrower than the original prompt; strong competing mechanisms exist |
| Demonstrated novelty | None for the proposed method; this plan is not a result |
| Experimental readiness | Reusable baseline infrastructure; crop actions, calibration, independent GT and timing still needed |
| Publication readiness | Not ready; only evidence-generating feasibility is justified now |

The first decision is whether F1–F3 justify a new method, not which journal template
to fill. If gates fail, publishable honesty requires changing the scope or stopping.
