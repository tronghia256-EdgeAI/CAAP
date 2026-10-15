# Tracking-aware adaptive perception — research plan

**Planning snapshot: 15 October 2026 (Asia/Saigon). Audited main: `9b6fd34`.**
This is a research proposal, not an implementation or a new experimental result.
Existing code, manuscripts, annotations, branches and runs are preserved.

**Recommendation: CONDITIONAL GO for a short feasibility study; no commitment to a Q1 submission yet.**
The broad idea is already substantially occupied by prior work. A narrower,
action-conditioned spatial refinement contribution needs evidence before engineering.

| Read | Document | Decision it supports |
|---|---|---|
| 1 | [00_RESEARCH_VERDICT.md](00_RESEARCH_VERDICT.md) | Whether to invest further |
| 2 | [01_REPO_AUDIT.md](01_REPO_AUDIT.md) | What the repository actually establishes |
| 3 | [02_PRIOR_ART.md](02_PRIOR_ART.md) | Which novelty claims are unavailable |
| 4 | [03_METHOD_PROPOSAL.md](03_METHOD_PROPOSAL.md) | Minimal causal architecture and mathematics |
| 5 | [04_DATASET_GT_PLAN.md](04_DATASET_GT_PLAN.md) | Development, calibration and locked testing |
| 6 | [05_EXPERIMENT_MATRIX.md](05_EXPERIMENT_MATRIX.md) | Controls, primary endpoint and CPU measurements |
| 7 | [06_GO_NO_GO.md](06_GO_NO_GO.md) | Quantitative stopping rules |
| 8 | [07_EIGHT_WEEK_ROADMAP.md](07_EIGHT_WEEK_ROADMAP.md) | A gated eight-week schedule |
| 9 | [08_PAPER_STRATEGY.md](08_PAPER_STRATEGY.md) | Contributions, venues and fallback |
| 10 | [09_AGENT_TASKS.md](09_AGENT_TASKS.md) | Future tasks with dependencies and acceptance criteria |

Evidence labels throughout:

- **VERIFIED:** inspected code/artifact or identified primary publication evidence.
- **INFERRED:** reasoned interpretation; not a measured causal effect.
- **UNVERIFIED:** missing measurement, full text, provenance or completed human review.
- **PROPOSED/TARGET:** future design or research threshold, never an achieved result.

Start with experiments **F1 crop benefit**, **F2 actual CPU cost**, **F3 risk versus
action benefit**, defined in the experiment matrix. Read the closest prior art first.
Do not implement the full architecture until these gates pass.

Existing scope remains [PAPER_SCOPE.md](../PAPER_SCOPE.md): no accident severity.
For this proposed paper, accident alerting, MAPPO and C1/C2/C3 are outside the main
contribution. Keeping existing code and the detector's Accident class is compatible
with that boundary. No training, benchmark or branch merge was performed for this plan.

Literature search reaches **15 October 2026**, not the unelapsed remainder of October.
It is targeted, not an exhaustive systematic review. In particular, the closest 2026
paper has verified DOI metadata and an indexed publisher abstract, but its full text
and reproducible implementation remain a gate. Journal quartile verification is also
explicitly incomplete; scope suitability does not establish Q1 status.
