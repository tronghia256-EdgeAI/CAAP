# Experiment matrix and pre-test endpoint

**All experiments below are planned. None were launched for this document.**
Primary class: motorcycle. Frozen first detector: best.pt, native source coordinates,
same confidence floor and authorized ROI/context policy for every compared method.
Do not combine historical unmasked/reference rows with current masked inference
as if detector resolution were the only changed factor.

## Primary endpoint and targets

Before new locked-test results, freeze:

- **Primary endpoint:** difference in **camera-balanced, sequence-macro motorcycle
  HOTA** between the proposal and the strongest feasible non-proposed policy selected
  on development/validation, at the **40 ms end-to-end CPU service target**.
- Compute official TrackEval HOTA per complete sequence, averaging its 19 localization
  thresholds. Average sequences within each camera, then cameras equally. This macro
  endpoint is declared explicitly; also provide official detection-weighted combined
  results. Do not present a hand average as TrackEval's combined HOTA.
- Compare against all registered baselines too. The primary control is chosen on
  validation, not whichever test baseline makes the largest proposal margin.
- **Research targets:** ≥0.015 absolute HOTA, ≥0.010 AssA, ≥0.015 IDF1 over that
  control, with a 95% paired sequence-level HOTA-difference interval above zero.
  These mean **1.5/1.0/1.5 percentage points**, not relative percent improvements.
- Latency feasibility: p95 ≤40 ms, bounded queue/backlog over a complete clip,
  and no worse deadline-miss rate than the control. Report p99/max and misses
  even when p95 passes. This is empirical soft real-time evidence, not a WCET proof.
- Cost comparability: same hardware/backend and maximum budget; target mean measured
  CPU wall time within ±5% for direct matched-cost claims, with common deadline
  constraints. If actual cost differs more, show a Pareto comparison and do not
  call it matched. No artificial sleeps or ignoring scheduler overhead.

If no refinement can fit the 40 ms target, Gate 2 fails for the real-time title.
Secondary 80/120 ms and the full Pareto frontier may support a renamed budget-aware
study; they must not silently replace the registered primary endpoint.

AssA, IDF1, DetA, MOTA, IDSW, Frag, motorcycle recall, small-object recall,
discovery delay, crop count and latency percentiles are all reported. Do not rescue
a failed primary HOTA comparison using whichever secondary metric improves.

## First three experiments before full implementation

### F1 — Is there any useful crop intervention? (E1 pilot)

Use 2–3 short NKKN windows containing independently rechecked tiny objects,
crossings and an ROI-boundary case. Use one frozen detector and OC-SORT. Compare
448/640/960/1280 global inference with **640 plus one fixed allowed crop** and
448 plus that crop. Choose fixed regions before inspecting intervention outcomes;
all crop policies use one common simple fuser. No risk model is required.

Measure class-wise detection recall, HOTA/AssA/IDF1, IDSW and duplicate births.
Keep actual native pixels and strict mask. An offline GT-selected best crop is
allowed only as a clearly marked optimistic diagnostic; it cannot pass the gate.
Go forward only if a **non-oracle** fixed crop demonstrates a useful benefit
(Gate 1). More detections with worse association is not success.

### F2 — Is that benefit affordable? (E6 pilot)

On the same controlled CPU/backend, time global 448/640, crop inputs 384/640,
global+crop+fusion+tracking and scheduling-preview overhead. Use actual dense and
freeflow frames, not an all-black image or detector-only number. At least three
separate warmed trials per action/configuration, with CPU power/thermal telemetry.
This short feasibility profile is future work; it is not being run in this plan.

Ask whether a crop can be admitted on ≥10% of frames within the 40 ms budget,
with a useful observed F1 action. A high-resolution full pass with the same cost
and better accuracy dominates the crop option. Gate 2 fails if no nontrivial crop
slack exists under a common practical backend.

### F3 — Does identity risk identify *repairable* errors? (E2/E3 pilot)

Build a stratified fixed sample of approximately 100–200 development decision
events, targeting ≥50 independently confirmed future ID-failure events if the
footage supports them. Preserve prevalence weights; do not quote case-enriched
precision as deployment precision. For each event replay the same H=10 future
frames from isolated state with no crop and each permitted candidate action.
Following the intervention, both arms use the same frozen base policy.

Features use only pre-action information. Outcomes use future GT offline. Compare
risk-only, confidence+scale+gap, density, randomized feasible selection and the
action-benefit model. Estimate failure AUPRC and realized reduction in identity
errors per measured millisecond. Positive failure prediction without intervention
benefit fails the scheduling hypothesis. This test should be done before a large
learned scheduler, not after eight weeks of integration.

## Progressive matrix

| Stage | Arms / controls | Fixed factors and output | Exit condition |
|---|---|---|---|
| E0 baseline reproduction | ByteTrack; OC-SORT published and matched; BoT-SORT without ReID/GMC; optional full/modern cheap tracker | Existing shared caches, same corrected GT, correct worktree code, official evaluator; reproduce current rows | IDs/metrics/hash agreement or explained small evaluator difference before new method |
| E1 spatial feasibility | Full-frame/global 448/640/960/1280; 640 + fixed crops; 448 + fixed crops; fixed SAHI-style tiling | Frozen detector, common source/context, fuser and complete timing; size/edge-bin recall | F1 and F2 pass; no crop-allocation model yet |
| E2 allocation | No refinement; fixed region; periodic region; density; confidence+scale; random; covariance-only; covariance+overlap; proposed action-benefit | Same candidate library, maximum K, cost model, discovery allocation, calibration/fuser; paired episodes | Proposal beats the strongest feasible cheap allocation at matched actual cost |
| E3 risk/action ablation | Remove uncertainty, ambiguity, confidence, scale, disappearance; risk-only vs benefit-conditioned; discovery reserve off | One backbone and detector first; same validation-selected operating point | Individual signals justify complexity; risk prediction and action value assessed separately |
| E4 backbone transfer | OC-SORT and ByteTrack mandatory; BoT-SORT if feasible | Same scheduler design/action library, normalized features; no test tuning per backbone | Gains are not just a replacement of a weak tracker; report interaction |
| E5 generalization | All four global sizes; regimes; locked camera(s); second detector sensitivity | First main detector fixed; older checkpoint provenance qualified; camera-disjoint GT | Gate 4; identify detector/scene-specific failures |
| E6 complete CPU profiling | Every main scheduler/backbone + feasible global/crop baselines | Actual decode→output, controlled hardware/backend, repeated randomized process order | Cost-matched frontier and honest deadline/throughput result |

Do not use a giant Cartesian product initially. F1/F2 prune useless tensor/crop
sizes; F3 prunes weak features. Only then run the registered E2 controls. Keep all
negative feasibility results and report the pruning rule.

## Fair allocation controls

Random crops share the same allowed rectangles/shapes and feasible budget logic,
with at least five predeclared seeds. Fixed/periodic controls can use their cheaper
decision overhead to afford more useful perception; do not force them to waste it.
The proposal pays for preview, risk, calibration, crop merging and final fusion.

Detection-call counts alone do not match compute: a rectangular letterboxed crop,
a square crop, a full image and an empty image can have different inference/NMS
costs. Match measured end-to-end behavior and disclose call count/tensor pixels
as explanatory variables. An oracle with zero charged decision cost is not a
fair runtime baseline.

To test the identity mechanism, add a **development-selected comparable-recall**
control and a recall/DetA versus AssA analysis. Do not retune thresholds using
locked-test GT to force exact recall matching. Higher HOTA entirely explained by
DetA supports detection refinement, not a claimed association-specific advantage.

The P01-style control is mandatory once its full method is available. If only a
covariance/overlap proxy can be implemented, label it a proxy; do not claim a
reproduction or superiority over an unavailable original implementation.

## E6 timing and load protocol

| Item | Registered treatment |
|---|---|
| Hardware | Record i5-12500H, RAM, OS/build, BIOS/power limits, CPU topology; another CPU is desirable before general edge-device claims |
| Power policy | On Windows record the active AC power plan/performance mode; Linux governor if another host is used. Do not change unrelated system settings in this planning task |
| Threads | Fixed PyTorch/ONNX/OpenVINO and OpenCV counts; verify after backend warm-up; fix affinity policy consistently on hybrid P/E cores |
| Backend | Same precision/export/runtime for all main policies. Confirm accuracy equivalence before treating a backend optimization as neutral |
| Thermal state | Record effective frequency, temperature/power when available, processor-performance counter and throttling flags; preregister exclusions uniformly |
| Background load | Record total/process utilization; pause research jobs for future trials; do not terminate other people's processes |
| Warm-up | Model warm-up plus identical tracker prehistory/prefix, excluded from measured window but documented; initial full-video startup also reported |
| Repetitions | At least 5 valid trials/configuration in fresh processes, randomized paired ordering; keep invalid trials and reasons. Never discard a slow valid trial because it misses budget |
| Duration | Full eligible clips or ≥1,000 measured frames/condition if feasible; enough sustained runtime to expose thermal drift, not only 200 favorable frames |
| Stages | Decode, mask/resize, global detector, preview/risk, selection, crop extraction, crop inference, coordinate/fusion, final tracker, output |
| Queueing | Capture-to-output latency/queue delay, source timestamps, dropped/skipped frames, arrival rate and deadline miss rate; cannot infer live stability from an offline loop alone |
| Utilization/power | Report process CPU seconds and utilization; watts/joules only with an identified sensor/method. `% Processor Performance` is not CPU utilization or energy |

Existing ≥90% processor-performance validity rule is a diagnostic, not proof of
equal thermal conditions or a universal standard. Timestamp the actual measured
interval in future profiling; reconstructing it from file modification times can
be contaminated by file I/O. Charge necessary policy work and avoid hidden
cache/annotation/oracle computation in the claimed deployable path.

For skipped detector frames in any later variant, tracking still advances on the
source clock with explicit dt. Do not compress time by omitting empty updates.
The initial MVP keeps a low-resolution global pass each source frame to simplify
fairness and discovery; detector skipping is a separately named ablation.

Also record which source timestamp each emitted result describes and how old it
is at emission. Offline HOTA on processed frames and throughput alone can hide
stale outputs. Use an explicitly registered arrival/drop/output policy for live
tests; report age and missed arrivals alongside standard offline HOTA. This follows
the evaluation warning in [Towards Streaming Perception](https://www.cs.cmu.edu/~mengtial/proj/streaming/),
not a claim to have implemented a standard streaming-HOTA metric.

## Uncertainty and report package

Use paired independent sequence differences and report camera-level outcomes.
Bootstrap clips within camera for conditional intervals; with sufficient cameras,
use a hierarchical camera/clip bootstrap. Small numbers require restrained claims
and raw per-sequence points, not a nominally precise interval.

Do not bootstrap random frames as if they were independent scenes. Existing
ID-reset moving-block intervals estimate a different statistic and remain secondary.
For signal ablations, predeclare a primary full-versus-simpler comparison and either
adjust multiple secondary comparisons or label them exploratory.

Artifacts per experiment: frozen source/GT/model/policy hashes; manifest and split;
complete actions/causal features; fused detections and track dump; official metrics;
selection frequency and discovery diagnostics; raw timing/telemetry; validity
receipt; tables and paired Pareto plots. Derived score scenarios remain separate
from human GT. No new paper number is accepted without its producing artifact.
