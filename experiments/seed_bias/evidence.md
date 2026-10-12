# Seed bias in the reviewed NKKN ground truth

**Question.** Each reviewed GT started from one tracker's output: `dense` from
`ctrv_gate_nsa` (C2), `mixed` from `baseline`. Does a GT favour the tracker that
seeded it, and through what?

**Method.** `python -m code.scripts.check_seed_bias` scores every frozen dump in
`experiments/gt_ablation` on both reviewed GTs. Motorcycles only, each review in
its own scope (dense: full frame; mixed: ROI). Scored two ways:

- **as published**;
- **detection-anchored**: every GT and predicted box is replaced by the cached
  detection it overlaps one-to-one at IoU ≥ 0.5, so both sides share the
  detector's geometry.

Output is in `seed_bias.json`. FN and FP counts come from the repository metric
(IoU 0.5).

| GT (seeded from) | variant | exact-box share | IDF1 | IDF1 anchored | IDSW | FN | FP |
|---|---|---:|---:|---:|---:|---:|---:|
| dense (C2) | baseline | 0.008 | 0.858 | 0.859 | 137 | 1547 | 1618 |
| dense (C2) | ctrv_gate_nsa | 0.909 | 0.907 | 0.907 | 27 | 872 | 1376 |
| mixed (baseline) | baseline | 0.997 | 0.983 | 0.983 | 9 | 20 | 23 |
| mixed (baseline) | ctrv_gate_nsa | 0.003 | 0.945 | 0.946 | 10 | 58 | 281 |

**Findings.**

1. **Each GT favours its seed by about 0.04 IDF1.** C2 leads by +0.048 on
   `dense`; `baseline` leads by +0.038 on `mixed`.
2. **Box geometry does not explain the IDF1 gap.** Anchoring both sides to the
   same detections moves IDF1 and HOTA at α = 0.5 by at most 0.002, for all 7
   variants on both GTs.

   Alpha-averaged HOTA is the exception: it *is* sensitive to geometry. After
   anchoring, the C2 − baseline gap shrinks:

   | GT | published | anchored |
   |---|---:|---:|
   | dense | +0.134 | +0.057 |
   | mixed | −0.127 | −0.049 |

   On both GTs the seed's geometry inflates the averaged score in the seed's
   favour. That is why the manuscript reports α = 0.5 only. Anchored scores make
   the averaged value usable.
3. **On `mixed` the gap comes from which boxes are in the GT, not from
   identity.** ID switches are 9 vs 10. C2 outputs 220 more boxes than
   `baseline`, which gives 281 FPs against 23. Of C2's anchored boxes that the
   GT lacks:
   - 73% are detections with score ≥ 0.5;
   - 61% lie where the GT has no box of any class;
   - 23% overlap a GT box at IoU ≥ 0.5 (duplicates or class confusion).
4. **`dense` is the mirror image.** 73% of `baseline`'s extra boxes lie where
   the C2-seeded GT has no box.

**Why the seed wins.** The seeding tracker's boxes were all shown to the
reviewer, so its wrong ones could be deleted. Boxes that only the other tracker
outputs were never shown. Their absence from the GT is therefore a default, not
a judgement.

**Consequence.** A GT pre-labelled from one tracker cannot rank that tracker
against another by IDF1 or MOTA unless the other tracker's disagreements are
adjudicated as well.

**Open: blind audit.** `python -m code.scripts.audit_disagreements sample`
(seed 20261012) drew 146 runs, where a run is consecutive frames of one ID:

| Stratum | Runs available | Runs sampled |
|---|---:|---:|
| C2 extras on `mixed` | 157 | 40 |
| C2 misses on `mixed` | 26 | 26 (all) |
| `baseline` extras on `dense` | 233 | 40 |
| `baseline` misses on `dense` | 453 | 40 |

The judge sees numbered crops only, in `data/annotations/seed_bias_audit/`
(gitignored). `score` reports, per stratum, the share of runs where the GT is
wrong, with Wilson 95% CIs.

**Identity strata.** Membership does not settle whether the dense ID-switch gap
(137 vs 27) is real. Wherever the reviewer missed a swap in the C2-seeded
identities, a baseline that tracked correctly is still charged a switch.
`switches` (seed 20261013) replicates the CLEAR matching of
`compute_tracking_metrics` and aborts if its count differs. It draws:

| GT | Tracker | Switches | Sampled |
|---|---|---:|---:|
| dense | baseline | 137 | 30 |
| dense | ctrv_gate_nsa | 27 | 27 (all) |
| mixed | baseline | 9 | 9 (all) |
| mixed | ctrv_gate_nsa | 10 | 10 (all) |

Each switch is shown blind as a crop pair of the GT identity: one crop at its
last match before the switch, one at the switch.

- Same vehicle in both crops: the switch is real.
- Two different vehicles: the switch is an artefact of the GT identities.

A seed's own switches are reviewer corrections, so they also act as a control
on the judge.

**Stopping rule.** Fixed on 2026-10-12, before any verdict was entered. At
commit 1ddaa05 both verdict files were empty: 0 of 146 in `verdicts.csv` and 0
of 76 in `switch_verdicts.csv`.

- **Order:** the judge works in sheet order. That order is a seeded shuffle,
  so every prefix is a random subsample of each stratum.
- **Early stop:** a stratum stops once 20 items are judged (excluding `?`)
  and its Wilson 99% interval excludes 0.5. Otherwise it runs to its end.
- **Why 99%:** `score` is checked after every sheet, and repeated looks at 95%
  would inflate the error rate. The intervals reported are 95%.
- **Blind interim output:** until every stratum has stopped, `score` prints
  only "continue" or "you may stop" for each file, so the judge sees no
  interim shares.
- **Gaps:** a blank verdict before a filled one is reported, because a
  skipped item breaks the random prefix.
