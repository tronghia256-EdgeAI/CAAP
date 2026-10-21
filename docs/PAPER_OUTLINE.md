# Paper outline — seed bias in tracker-assisted MOT GT annotation

Status: the manuscript is `paper/main.tex`; this outline is the original plan. Format follows the Pattern
Recognition Letters Guide for Authors (read 21 October 2026) and its mandatory authorship and formats form:
elsarticle with `prletters.sty`, double column, at most 7 pages including references, numbered references,
abstract of at most 200 words, highlights in a separate file (`paper/highlights.tex`, 3-5 bullets of at most
85 characters), a graphical abstract (`paper/graphical_abstract.pdf`), institutional e-mails of all authors in the
first-page footnote, a CRediT statement, and the authorship confirmation form uploaded as the cover letter.
Do not mention AI in the paper, including a sentence such as "no AI was used".

## Working title

"How much does a tracker-seeded ground truth favour its seed? Measuring and removing seed bias in
multi-object tracking benchmarks"

## Questions and permitted conclusions (per PROTOCOL.md A5–A6)

| Question | Confirmatory conclusion | Source in `summary.json` |
|---|---|---|
| RQ1: How much does GT seeded from tracker A favour A? | SA ≥ δ = 0.01 IDF1 at θ_ref, **separately for each dataset**; a general statement only if all 3 datasets meet it | `h1[REF].sa_same_detector` (BCa), `above_delta` |
| RQ2: Do errors correlated with the seed reverse rankings more than random errors of the same size? | τ_null − τ_seed and the number of reversed pairs (threshold δ), at a = 0 | `h2[ref].a0`, `null_skip_share` |
| RQ3: Which cheap protocol reduces the bias? | BCa upper bound of D_P − D_P0 < 0 at θ_ref, with the two-part cost | `h3[θ_ref]` |
| Descriptive | θ map, curves over r/q/p_fp, diagnostics | `h1` (all cells), `ranking`, `h1_diagnostics`, `reviewer_diagnostics` |

State clearly in the paper: SA ≥ 0 is a consequence of the reviewer model, so the scientific content lies in the **magnitude**. θ_ref is
an **assumption**, not a measurement; the human study is reserved for the revision round (PROTOCOL.md section 6). All conclusions
over the θ grid and about rankings use IDF1 only; HOTA only at θ_ref.

## Contributions (planned; keep only those the data support)

1. The first quantitative measurement of seed bias in tracker-assisted MOT GT, on 3 public benchmarks
   (traffic CCTV FastTrack, MOT17, DanceTrack), 8 systems.
2. An open, parameterised reviewer model (r, p_fp, q, a), with a sensitivity map and a null model matched on the number of errors.
3. Findings: with a shared detector, union seeding coincides with single seeding (A6 section 3); box geometry contributes almost nothing
   to the bias (A5 section 4).
4. Evaluation of the consensus and bracket protocols along the (inspection cost, drawing cost) path — D.
5. Full reproduction code (no redistribution of data).

## Structure

1. **Introduction.** Model-assisted annotation has become standard. Known in NLP (Berzak et al. 2016) and medicine
   ("incorporation bias", QUADAS-2). In MOT only DIVOTrack mentions it in one sentence; nobody has measured it. State RQ1–3.
2. **Related work.** Label errors and benchmark rankings (Northcutt et al. 2021; COCO-ReM 2024; Penquitt et al.
   2026, stating clearly: random errors rarely reverse rankings, while correlated errors are the open question here). Incomplete labels
   in tracking (TETA 2022). Cheap annotation for tracking (SPAM 2024). Metrics (HOTA 2021, IDF1, TrackEval).
   Pre-annotation (Lingren et al. 2014; Schroeder et al. 2025).
3. **Problem and reviewer model.** Definitions of GT_S, SA, the reviewer model (ID error episodes, runs, geometry),
   the check identities. A figure illustrating a swap episode.
4. **Experimental setup.** Datasets; YOLO11x/YOLO11n COCO detectors; 4 trackers (Roboflow trackers), configured
   per A2; shared preprocessing; TrackEval; θ grid, θ_ref; sequence-level BCa bootstrap; pre-registration
   (PROTOCOL.md and amendments, freezing commit).
5. **Results.**
   - 5.1 RQ1: table of SA at θ_ref by dataset (BCa, percentile, leave-one-out); SA(A, B) matrix.
   - 5.2 Sensitivity: SA curves over r, q, p_fp through θ_ref; map (descriptive); match thresholds 0.4/0.6;
     SORT sensitivity.
   - 5.3 RQ2: τ and number of reversed pairs, seed versus null, a = 0 (a = 1 alongside).
   - 5.4 RQ3: Pareto (inspection cost, drawing cost, D); held-out; bracket.
   - 5.5 Diagnostics: by class (FastTrack), class confusion, by sequence, geometry for cross-detector pairs.
6. **Discussion.** Practical implications: when tracker-assisted GT is safe (the r, q that must be reached). Limitations: θ is an
   assumption, shared detector, no ReID trackers, 3 datasets. Conclusions are written according to the results, even when negative.
7. **Conclusion.**

## Figures and tables (maximum according to the venue's limit)

- Figure 1: diagram of seed → reviewer → GT_S → scoring, and one episode.
- Table 1: SA at θ_ref, 3 datasets (H1).
- Figure 2: SA over r and over q through θ_ref, 3 datasets (CI bands).
- Figure 3: H2 — τ_seed and τ_null over r.
- Figure 4: H3 Pareto.
- Appendix tables: diagnostics, sensitivity.

## References to verify (Crossref/arXiv) before adding to the .bib

Berzak et al. 2016 (arXiv 1605.04481); DIVOTrack (arXiv 2302.07676); Schroeder et al. 2025 (arXiv
2507.15821); Northcutt et al. 2021 (arXiv 2103.14749); COCO-ReM (arXiv 2403.18819); Penquitt et al. 2026
(arXiv 2609.21822); TETA (arXiv 2207.12978); SPAM (arXiv 2404.11426); HOTA (arXiv 2009.07736); Lingren et
al. 2014 (JAMIA, PMC3994857); FastTracker (arXiv 2508.14370); MOT17/MOTChallenge; DanceTrack; ByteTrack;
OC-SORT; BoT-SORT; SORT; QUADAS-2. Each entry must be opened and checked against authors, year, venue and DOI.
