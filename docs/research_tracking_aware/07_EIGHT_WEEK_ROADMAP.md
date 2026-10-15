# Eight-week roadmap with early exits

**Proposed dates: 15 October–9 December 2026, Asia/Saigon.** Start dates are a
planning scenario, not an already running project or a deadline promise.
Team assumption: one engineer/research student, one annotation/review partner,
and an advisor for gate reviews. The assistant can support analysis/engineering
later; it cannot replace an independent human annotator or provide footage rights.

No week authorizes implementation in the present planning-only phase. Stop at a
failed gate instead of mechanically filling the rest of the schedule.

## Week 1 — 15–21 October: close threats and test useful actions

- **Research objective:** determine whether there is a defensible question and
  useful crop signal before building a scheduler.
- **Technical tasks:** obtain closest full texts/code availability; compare mechanisms;
  freeze the strict-mask pilot protocol; recheck pilot GT areas; specify common
  crop/fusion behavior and native/network scales.
- **Reuse:** `Detector`, `open_video`, reconciled GT receipts, `gt_roi`, final
  resolution/mask artifacts, the prior-art/evidence ledger in this folder.
- **New modules later:** minimal fixed-crop experiment harness and geometric remapping
  helper only; no risk model or production pipeline refactor yet.
- **Required data:** 2–3 reviewed NKKN pilot windows, tiny objects, at least one
  crossing and an ROI-boundary case; source/rights inventory for new cameras.
- **Experiments:** F1; desk-based Gate 5 review. Existing E0 numbers are audited before
  deciding whether a lightweight reproduction is necessary in the execution phase.
- **Expected artifacts:** mechanism-overlap matrix, pilot GT v2 receipt, F1 table with
  detection and identity metrics, explicit proposed mask/context policy.
- **Acceptance:** a non-oracle permitted crop passes Gate 1 and a plausible technical
  distinction survives prior-art review. Missing closest full text keeps novelty open.
- **Dependencies/risks:** primary-paper access, readable native pixels, annotation
  omissions. If F1 fails, stop the active-perception implementation path.

## Week 2 — 22–28 October: CPU feasibility and repairable-risk pilot

- **Research objective:** establish budget slack and whether identity risk maps to
  an intervention that helps.
- **Technical tasks:** controlled short action profiling; isolate state for one-step
  interventions; label future ID events offline; compare simple risk controls.
- **Reuse:** stage timer design, `benchmark_realtime.environment`, existing
  `operating_point/cpu_sampler.ps1` and validity scripts, official evaluator bridge.
- **New modules later:** action-cost lookup, counterfactual pilot logger; prototype
  read-only tracker projection limited to pilot use.
- **Required data:** F1 windows plus a fixed 100–200-event development sample;
  independent human checking of sampled failure/repair labels.
- **Experiments:** F2 and F3; zero-crop invariance smoke tests; no large detector
  training or RL.
- **Expected artifacts:** raw stage times/telemetry, valid/invalid trial receipts,
  AUPRC/reliability curves and identity benefit per millisecond.
- **Acceptance:** Gates 2 and pilot 3 meet targets or produce a clear information-rich
  stop decision; no uncharged preview/crop work.
- **Dependencies/risks:** CPU throttling, crop call overhead, scarce ID failures,
  copied tracker globals. If 40 ms cannot admit useful crops, remove the 25-fps
  real-time objective or stop; do not quietly move its success target.

## Week 3 — 29 October–4 November: minimal causal integration and annotation lock design

- **Research objective:** implement only the viable actions and preserve tracker
  semantics while preparing independent evidence.
- **Technical tasks:** preview/commit adapter, coordinate provenance, common fusion,
  empty/skipped crop handling, invalid-state/ROI rules, deterministic action caching.
- **Reuse:** OC-SORT, `gt_roi`, cache hash/atomic-write design, upstream verification,
  GT editor/CVAT workflow.
- **New modules later:** `perception/tracker_preview.py`, `crop_detector.py`,
  `fusion.py`, `action_cache.py` (proposed names).
- **Required data:** old development clips; choose camera-disjoint test clips and
  annotation guidelines without viewing proposed-method rankings.
- **Experiments:** no-refinement equivalence, synthetic transforms/overlap, short
  crossing replay; common fuser comparison.
- **Expected artifacts:** deterministic integration checks, frozen action library,
  cache schema, source/split manifests and initial independent-camera annotation.
- **Acceptance:** each frame advances once; zero-crop output reproduces its backbone;
  no systematic duplicate/merged identities from fusion; test selection registered.
- **Dependencies/risks:** Gate 5 still unresolved → do not market a new method;
  union prelabels can overwhelm review, so schedule a blind full-area pass too.

## Week 4 — 5–11 November: calibrate risk and action benefit

- **Research objective:** isolate the benefit beyond cheaper confidence/scale rules.
- **Technical tasks:** grouped development/calibration/validation split; small risk
  and conditional-benefit model; per-shape CPU cost model; K=1 selector and
  reserved-discovery control; calibration error analysis.
- **Reuse:** native detection caches, official HOTA/identity scoring, event audit tools;
  no C1 percentile from future test video.
- **New modules later:** `identity_risk.py`, `action_value.py`, `budget_selector.py`;
  serialize every fitted parameter/version.
- **Required data:** trustworthy development/calibration trajectories and pilot
  intervention labels; independent test GT remains inaccessible to the tuner.
- **Experiments:** E2 pilot, E3 single-signal ablations, risk-only versus action-benefit,
  exploration reserve versus none.
- **Expected artifacts:** validation tables, calibration plots, selected policy and
  signed Gate 3 decision; ongoing GT review/audit progress.
- **Acceptance:** gains over strongest cheap control at actual matched cost; model
  complexity justified feature by feature; no hidden per-track detector calls.
- **Dependencies/risks:** low power, model overfit to crossings, difficulty predicting
  crop benefit. Use the empirical backup if only resolution explains results.

## Week 5 — 12–18 November: full controlled development study and GT adjudication

- **Research objective:** freeze a reproducible operating point and finish the
  independent evaluation asset without selecting a winner's annotations.
- **Technical tasks:** full E0/E1/E2 matrix pruned by prior gates; five random-policy
  seeds; independent reviewer resolves membership/identity disagreements; common
  ignore/occlusion/re-entry definitions.
- **Reuse:** result provenance and GT release patterns, prior seed-bias audit design.
- **New modules later:** experiment orchestrator and common action/cost recorder;
  metric export uses pinned official TrackEval as authority.
- **Required data:** all corrected NKKN development/calibration clips; completed
  camera-disjoint GT with sufficient trajectories/events from the dataset plan.
- **Experiments:** full development allocation controls and event-based diagnostics;
  do not unlock final test for selection.
- **Expected artifacts:** frozen policy/config/model/GT/split hashes; final GT audit
  receipt, per-sequence development scores and compute frontier.
- **Acceptance:** target data diversity reached or explicitly downgraded; independent
  blind audit completed; no unresolved ambiguity driving the primary endpoint.
- **Dependencies/risks:** annotation effort 25–60 hours is only a planning range;
  if it exceeds capacity, extend the schedule instead of calling prelabels GT.

## Week 6 — 19–25 November: backbone transfer and locked-camera evaluation

- **Research objective:** test generality after parameters and GT are locked.
- **Technical tasks:** ByteTrack adapter with the same causal contract; feature-unit
  normalization; optional BoT-SORT/modern cheap baseline; one registered test release.
- **Reuse:** published/default/matched backbones, frozen calibration and common fuser.
- **New modules later:** ByteTrack preview adapter and camera-grouped evaluator report.
- **Required data:** locked independent camera(s), plus development clips for all
  remaining integration debugging; no test-parameter fitting.
- **Experiments:** E4 and E5; main endpoint first, all predeclared secondary results
  including unfavorable scenes.
- **Expected artifacts:** full test actions/dumps/official metrics, paired per-clip
  differences, camera-specific plots and Gate 4 decision.
- **Acceptance:** primary practical/statistical targets hold and cost is comparable;
  label one-camera evidence conditionally if only one new camera was available.
- **Dependencies/risks:** source/domain shift, unseen entrants and seed uncertainty.
  A method change after test requires a new lock; do not reuse the same camera as
  untouched evidence after inspecting its failures for tuning.

## Week 7 — 26 November–2 December: complete CPU evidence and robustness

- **Research objective:** verify that the complete deployment path sustains its
  registered budget rather than just looking fast in detector/replay timing.
- **Technical tasks:** sustained profiling with randomized fresh-process trials;
  queue/timestamp/drop accounting; memory and CPU utilization; power only if a
  supported sensor exists; backend/model provenance check.
- **Reuse:** stage instrumentation, telemetry/validity concepts, frozen output logs.
- **New modules later:** live-arrival evaluation harness and transparent timing
  aggregation; optional second-CPU adapter without policy retuning.
- **Required data:** fixed dense/freeflow/test clips long enough for thermal behavior;
  the frozen action/policy implementation, not an offline oracle cache path.
- **Experiments:** E6 and predefined latency/GT robustness analyses; optional second
  detector reference with qualified provenance.
- **Expected artifacts:** p50/p95/p99/max, CPU cost, deadline misses/queue curves,
  cost-matched Pareto plot and raw validity/telemetry archives.
- **Acceptance:** all compared leading policies timed end to end; slow valid trials
  kept; uncertainty claims match experimental units; no missing profiling stages.
- **Dependencies/risks:** unstable laptop thermal/power state and unsupported power
  sensors. Report unknown power explicitly; no inferred watt or broad hardware claim.

## Week 8 — 3–9 December: decide paper form and audit every claim

- **Research objective:** write the paper supported by evidence, including a decision
  not to pursue a new-method Q1 paper if gates failed.
- **Technical tasks:** reviewer-style novelty/fairness/data audit; source-to-table
  regeneration; check full-alpha HOTA and official metric versions; verify current
  journal quartile/category/year; author rights/declarations; reproducibility package.
- **Reuse:** existing JRTIP manuscript as a preserved background reference, not a
  text to relabel into a different contribution without results.
- **New modules later:** table/figure generation only where needed; new manuscript
  branch or separate draft after an explicit writing task, never overwrite old evidence.
- **Required data:** complete frozen reports, limitations and rights confirmation.
- **Experiments:** no unregistered final-test tuning; only correction of documented
  analysis bugs, applied to all methods with an audit trail.
- **Expected artifacts:** up to three defensible contributions, paper draft, six
  key figures/tables, data/code availability statements and final GO/NO-GO memo.
- **Acceptance:** novelty distinction demonstrated; all primary controls present;
  data/timing complete; claims reproducible; suitable journal verified. Otherwise
  deliver the empirical study or stop and retain the negative-result record.
- **Dependencies/risks:** novelty too incremental, single-camera evidence or missing
  rights. Eight weeks is a research milestone, not an acceptance guarantee.

## Dependency spine

`Prior-art closure + F1/F2 → F3 → minimal causal adapter → calibration → full
development controls → policy/GT lock → independent test → sustained timing → writing`.

Annotation/source review starts early in parallel with feasibility and is never
replaced by extra engineering. A week-one/two stop saves most of the eight-week
cost. Detailed future task boundaries are in [09_AGENT_TASKS.md](09_AGENT_TASKS.md).
