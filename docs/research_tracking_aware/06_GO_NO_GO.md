# Decision gates and stopping rules

All thresholds are **research targets proposed before new test results**, not
existing achievements or guaranteed power. Keep the source/GT/mask policy fixed
while applying a gate. Changes require a new versioned protocol.

## Gate order

Check novelty **Gate 5 first**, at least to a full-text mechanism comparison,
then inexpensive Gates 1/2 in parallel. Gate 3 precedes a large implementation;
Gate 4 precedes a journal-ready generalization claim. The numbering follows the
master prompt, not an instruction to postpone the novelty threat until week eight.

| Gate | Hypothesis and required evidence | Quantitative pass target | Failure means / next action | Effort estimate |
|---|---|---|---|---|
| **1: crop benefit** | F1/E1; non-oracle fixed crops on independently rechecked development windows, same common fuser | ≥5 percentage points absolute small-motorcycle detection recall gain at matched FP definition; ≥0.010 HOTA and nonnegative AssA/IDF1 versus its global low-resolution baseline, pooled with per-window results; no systematic duplicate births | Native/masked pixels, scale or fusion do not yield useful information. Fix one demonstrated integration error if any; otherwise stop spatial active perception. Do not add a risk model to make an unhelpful detector action useful | 2–4 engineering days + 6–12 human review hours |
| **2: useful CPU budget** | F2/E6 pilot, same actual frozen backend and controlled hardware, all stages included | At 40 ms target: a useful F1 crop can be admitted on ≥10% of frames; measured p95 ≤40 ms; no growing queue at 25 fps; preview/selection/fusion overhead preferably ≤10% of budget (4 ms). No equally cheap fixed high-resolution pass dominates it | Insufficient slack for real-time refinement. Stop the 25-fps real-time claim. Consider a separately registered 80/120 ms budget-aware direction, or empirical backup; common backend optimization is a feasibility intervention, not novel contribution | 2–3 days + controlled unattended measurement time |
| **3: identity-driven value** | F3 then registered E2/E3, complete strong controls including available P01 method/proxy with honest label | F3: ≥0.05 absolute AUPRC gain over the best confidence/scale/gap failure predictor and positive action benefit per cost; E2: ≥0.015 HOTA, ≥0.010 AssA, ≥0.015 IDF1 over the strongest feasible validation-selected control, mean cost within ±5%, HOTA paired sequence CI above 0 | Risk is generic difficulty, action utility is not learned, or cheap heuristics explain gains. If only recall improves, reframe detection refinement. If OC-SORT/no new scheduler explains the improvement, stop the identity-allocation claim | 4–7 days after F1/F2, plus pilot event adjudication |
| **4: held-out camera** | E5 on independently reviewed, locked camera-disjoint footage; no test threshold fit | Primary HOTA target above at comparable cost, AssA/IDF1 targets positive as specified; show per-camera results and no substantial scene regression (predeclare >0.010 HOTA loss as a warning requiring explanation). With one camera, conclusions explicitly conditional on it | A camera-specific policy or annotation artifact, not demonstrated generalization. No post-test tuning followed by calling the same camera held-out; acquire a new lock if the method changes | 2–4 engineering days + roughly 25–60 annotation/audit hours, highly data-dependent |
| **5: novelty** | Full texts/mechanism matrix for closest work, especially P01–P03; compare input signals, spatial actions, objective, cost and causality | At least **one identifiable technical element** absent from the closest verified formulation, with **one dedicated falsification/ablation** isolating its benefit beyond that control; zero unresolved central overlap before asserting novelty | The broad idea is occupied. Stop a new-method submission or choose one of the three formulations in the literature review. CPU/Vietnamese motorcycles alone do not pass | 2–4 researcher days; full-text access may be an external dependency |

Efforts are person-day planning ranges, not measured execution times. Human effort
can dominate. If an independent annotator or usable footage is unavailable, the
eight-week publication plan must shrink or extend; automatic prelabels do not close
Gate 4.

## Reading failed or inconclusive tests

- A confidence interval crossing zero is **inconclusive**, not proof of equivalence.
  A tiny statistically positive effect below the practical target is not a pass.
- Fixed crops beating low-resolution inference but beating the proposed allocation
  too means selective inference is feasible while the new scheduler is unnecessary.
- Oracle gains only show an available opportunity. They do not pass Gate 1/3 for a
  deployable policy, and their GT search time is not a runtime measurement.
- Correct failure prediction with zero intervention benefit rejects the premise
  that high risk is a useful computation-allocation target.
- Mixed/dense/freeflow from one source are not three independent cameras. A camera
  test which changes the winning method after manual GT corrections is a warning
  to resolve annotation uncertainty, not a license to choose the favorable GT.
- If zero eligible identity failures occur, AUPRC/AssA-improvement evidence is not
  available. Collect the predeclared event stratum or report insufficient data.

## Change and stopping policy

At each gate write a dated decision with hashes, the exact comparison, target,
estimate/interval, deviations and action: GO, REVISE ONCE, STOP or INCONCLUSIVE.
Allow one small diagnostic revision for an identified bug, then repeat on separate
development windows. Do not keep adding features until a positive table appears.

Keep all timing trials and run variants. Exclude a thermal/power-invalid trial by
the registered condition only, never its accuracy or latency outcome. Preserve
failed runs and deprecated GT as historical artifacts.

If using a pilot variance estimate for sample planning, the unit is an independent
sequence/group. A rough paired normal approximation is
`n ~= ((1.96 + 0.84) * sd_sequence_delta / target_delta)^2`; treat it as planning,
not a guaranteed sample size under camera clustering or small-N non-normality.
Fix expansion size before locked outcomes, rather than optional-stopping for p<0.05.

## Current verdict against gates

| Gate | Current status |
|---|---|
| 1 | **UNVERIFIED:** resolution/mask experiments motivate crops; no actual crop intervention result inspected |
| 2 | **UNVERIFIED:** final CPU measurements absent; old throttled profiles cannot pass |
| 3 | **UNVERIFIED:** no action-benefit scheduler or independent labels yet |
| 4 | **NOT READY:** independent-camera review queues exist but every inspected decision is blank |
| 5 | **CENTRAL OVERLAP THREAT:** broad novelty rejected; narrower distinction awaits full-text closure |

**CONDITIONAL GO applies only to the feasibility program. It is not a decision to
spend eight weeks implementing a presumed publishable architecture.**
