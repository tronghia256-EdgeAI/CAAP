# Future task packets and dependencies

These are **planning deliverables**, not launched agents or permission to implement
during this task. No messages to collaborators, training, benchmark, deployment or
branch merge are authorized by this file. A later execution task should adopt only
the packets whose research gates passed.

Use a new worktree/branch for future method implementation, preserve all old runs,
and obey each run's source/config freeze. Share data/model contracts before parallel
work. Scientific dependence takes priority over maximizing concurrent engineering.

Each packet below has a small reviewable output. Suggested future file paths do
not mean the modules already exist. Estimates exclude unattended measurement time
and are uncertain engineering person-days.

| ID | Task / role | Depends on | Deliverable and proposed file boundary | Acceptance criteria | Estimate |
|---|---|---|---|---|---|
| R01 | Close closest prior art / researcher | This plan | P01 full-text mechanism note; update literature matrix only | Exact signals/actions/cost/runtime/availability comparison, source URLs/pages; unresolved distinction explicitly marked | 1–2 d plus access |
| R02 | Freeze research contract / lead | R01 | Versioned scope/split/endpoint/action-space protocol | 40 ms primary; mask/context rule; strongest controls; honest alternative if novelty absent; no test rankings consulted | 0.5–1 d |
| D01 | Source and leakage ledger / data lead + Nghĩa | R02 | Recording/camera/day/rights and training-source manifest | Exclude known training camera; flag old detector provenance; same camera at two times not double-counted as cameras; human confirmation kept separate | 1 d + human input |
| D02 | Pilot GT completeness / annotator | R02 | New pilot GT version, old GT untouched | Fixed full-area zoom pass, all methods' disagreements, unknown/occluded IDs adjudicated; no tracker output auto-certified | 1–2 d human |
| B01 | Baseline authority audit / engineer | R02 | Hash/metric/class/ROI/worktree reproduction receipt | Pin branch sources; official HOTA; explain CLEAR differences; name stripped BoT-SORT and partially matched OC-SORT thresholds accurately | 1 d |
| F01 | Fixed-crop feasibility harness / engineer | D02, B01 | Proposed `experiments/tracking_aware_pilot/` fixed-action runner/report | F1 results with one common fuser, non-oracle crop, detection and ID outcomes; no risk scheduler; coordinate fixtures | 1–2 d |
| F02 | CPU action feasibility / systems student | F01 | Raw controlled action timing, environment/thermal receipt | F2 end-to-end stages; no speed claims from cache/replay; useful crop slack at primary budget or documented Gate 2 failure | 1–2 d |
| F03 | Risk versus repairability pilot / researcher | F01, F02 | Fixed event manifest and paired intervention analysis | Causal features only; future GT used offline only; grouped splits, correct prevalence weighting; compare cheap heuristics; isolated tracker states | 2–3 d |
| G01 | Feasibility verdict / lead + advisor | R01, F01–F03 | Dated Gates 1/2/3/5 decision | Targets checked, failures/intervals retained; full implementation stopped if unsupported | 0.5 d |
| M01 | OC-SORT read-only preview / engineer | G01 pass | Proposed `code/perception/tracker_preview.py` | Zero-crop bit-equivalence; exactly one committed prediction/update; no ID/frame/history mutation during preview; overhead measured | 1–2 d |
| M02 | Crop inference contract / engineer | G01 pass | Proposed `code/perception/crop_detector.py` | Native-coordinate inversion with letterbox/padding; fixed checkpoint/floor/class IDs; authorized source mask only; empty/edge cases | 1–2 d |
| M03 | Common fuser / engineer | M02 | Proposed `code/perception/fusion.py` | Same fuser all selection policies; cross-source duplicates handled; neighboring bikes kept; empty crop never erases coarse evidence | 1–2 d |
| M04 | Action cache/provenance / engineer | M02–M03 contracts | Proposed `code/perception/action_cache.py` | Key includes source frame/crop/tensor/model/scope/fuser version; exact causal frame alignment; mismatch fails; atomic resume | 1 d |
| D03 | Independent-camera annotation / annotation lead | D01, R02 | Human-corrected CVAT/editor export with union hypotheses | Proposed trajectory/occlusion/competition/small-object targets reached or deficit reported; no method ranking used to pick windows | 15–40 h human, variable |
| D04 | Independent audit and GT lock / second reviewer | D03 | Blinded audit/adjudication and immutable GT/split receipt | Review neither-proposed regions too; report agreement/unknowns; one person twice not called independent; no unresolved primary ambiguities | 10–20 h human |
| M05 | Calibrated risk / researcher | F03, M01, D02 | Proposed `code/perception/identity_risk.py` | Features available pre-action; covariance units valid; no-candidate case explicit; beats confidence+scale+gap on held-out development; AUPRC/Brier/calibration logged | 1–2 d |
| M06 | Conditional action value / researcher | F03, M02–M05 | Proposed `code/perception/action_value.py` | Risk-only comparator; joint competitor coverage; useful action labels from isolated development interventions; no claim surrogate equals HOTA | 1–2 d |
| M07 | Budget selector/discovery / systems student | F02, M06 | Proposed `code/perception/budget_selector.py` | K=1 first; charge overhead; actual conditional costs; no-feasible-action fallback; discovery reserve and starvation logs; no RL | 1–2 d |
| E01 | Controlled scheduler matrix / engineer | M01–M07 | Versioned E2/E3 orchestration and complete development report | Fixed/periodic/random/density/confidence/covariance/overlap/strong prior method controls; comparable actual budgets; five random seeds; negative runs retained | 2–3 d |
| M08 | ByteTrack adapter / engineer | M01 contract, E01 viable | Proposed ByteTrack preview implementation, isolated from OC-SORT | Same one-update invariants and normalized features; class/birth differences documented; no global-state contamination across arms | 1–2 d |
| E02 | Policy lock and independent evaluation / evaluator | E01, M08, D04 | Frozen policy hash, sealed test manifest, E4/E5 report | No camera-test calibration; registered primary endpoint first; per-camera data and negative scenes; official metric versions | 1–2 d |
| P01 | Complete CPU profiler / systems student | E01 contracts | Proposed profiler separate from historical runners | All main baselines/backbones included; stage and queue timing; fresh randomized trials; power only if measured; invalid-trial policy | 1–2 d |
| E03 | Sustained profiling and robustness / evaluator | E02, P01 | E6 cost-matched frontier and raw telemetry report | ≥5 valid trials/configuration; slow valid trials kept; source clock/skipped frames explicit; no cache/oracle path presented as live | 1–2 d + measurement |
| A01 | Statistical/annotation sensitivity / analyst | E02–E03 | Paired clip/camera report and event/GT sensitivity | Correct units; no frame bootstrap masquerading as cameras; sensitivity scenarios not true GT bounds; effect magnitude and uncertainty both shown | 1–2 d |
| W01 | Venue/claim audit / advisor + author | G01, E02–E03, A01 | Final GO/NO-GO, index/category/year and rights/declarations checklist | Demonstrated distinction; all gates addressed; current required Q1 verified by acceptable official source; no acceptance probability invented | 1 d |
| W02 | Figures and new draft / writer | W01 GO or explicit empirical route | Separate manuscript branch/draft and reproducible figures/tables | Maximum three supported contributions; every number maps to artifact; old JRTIP draft and experiments preserved | 3–5 d |

## Shared contracts before independent execution

Data contract: source hash, camera/day, absolute frame ID/timestamp/native size,
local GT indexing, ROI geometry/rule, context policy, detector identity and class map.

Action contract: pre-action information timestamp, crop rectangle before/after clip,
tensor shape/letterbox transform, cost estimate/actual time, selection reason and
fusion provenance. A skipped action remains a skipped action, not an empty detector
observation that can advance the track twice.

Evaluation contract: policy/GT/model/code hashes, class-aware primary evaluation,
official full-alpha HOTA, exact latency boundary and pre-registered exclusion/split
rules. Preview/cost/fusion/calibration work is not performed by an uncharged oracle.

## Safe opportunities for future parallel work

R01 and D01 can progress together. After feasibility, D03/D04 can run while M01–M07
are engineered, provided annotators cannot see policy rankings. M02/M03 need a
shared coordinate contract; P01 needs that timing boundary. E02 cannot start before
both policy and GT lock. No person should tune on the test ranking they are charged
with independently evaluating.

Human ownership remains necessary for footage use, difficult identity adjudication,
independent review and author declarations. Automated task completion is not proof
of those facts. This file defines future work packages; none were executed now.
