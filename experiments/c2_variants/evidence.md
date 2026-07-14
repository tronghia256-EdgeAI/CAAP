# C2 variant sweep — tracker-only replay (2026-07-14)

Data: `experiments/c2_real_vnweights_full/detections.npz` — 9000 frames
(6 min, NKKN 08:00) of cached VN-yolo11n@1280 detections. All variants
consume IDENTICAL detections; differences are pure tracker behaviour.
Replay runs at 50–70 fps (no detector), so this sweep is the standard
iteration loop from now on.

## Results (motorcycle unless noted)

| metric | baseline | ctrv | **ctrv_gate** | ctrv_gate_snoise | ctrv_snoise |
|---|---|---|---|---|---|
| re-id events        | 259  | 205  | **125** | 199  | 258  |
| unique IDs          | 3226 | 3164 | **2628**| 2985 | 3262 |
| mean lifespan (all) | 55.8 | 56.0 | **71.8**| 64.5 | 54.6 |
| short tracks (all)  | 711  | 706  | **353** | 472  | 784  |

**Winner: ctrv_gate** — vs baseline: re-id −51.7%, unique moto IDs
−18.5%, mean lifespan +28.7%, short tracks −50.4%.

ID-transfer sanity check: intra-track jumps >40 px between consecutive
output frames — baseline 1, ctrv 2, ctrv_gate 2 (per ~218k pairs).
Gating does not create teleporting tracks. Same-class constraint +
rescued-cost floor (0.5, so real IoU matches always win) hold in tests.

## Negative result: scale-adaptive noise

Both with and without the gate, scaling Q/R by (box/40px)² HURTS
(re-id 258 vs 205 standalone; 199 vs 125 on top of the gate).
Interpretation: detection jitter for small far boxes does NOT shrink
proportionally with size (pixel-quantization floor), so the tightened R
makes the filter overconfident exactly where detections are noisiest;
under the gate it additionally shrinks the innovation ellipse and blocks
legitimate rescues. Kept in the code behind `ctrv.scale_adaptive`
(default OFF) as documented ablation material.

## Decisions applied

- `uncertainty_gating: true` in default/exp1/exp2/exp3 configs
  (baseline unaffected). Vendor patch P11 (see PATCHES.md) keeps the
  association algorithm itself untouched — only the first-association
  cost matrix gains a motion-uncertainty rescue for lost CTRV tracks.
- C3 gained a det_conf component (w=0.30) after ghost-track forensics —
  see `experiments/c2_real_vnweights/evidence.md`.

## Framing for the paper (when we return to it)

C2 = "the class-conditioned motion model supplies the matcher with both
a predicted box and its uncertainty": CTRV mean → predicted box (as
before), CTRV covariance → re-association gate. One contribution, two
uses of the same filter; association algorithm unchanged.

Reproduce:
```
python -m code.scripts.compare_motion_models \
    --replay experiments/c2_real_vnweights_full/detections.npz \
    --out-dir experiments/c2_variants
```

## Exp2 replay: buffer hypothesis rejected (2026-07-14, Phase 1.1)

Hypothesis: the 23 gap>=30 re-id events die because the lost-track buffer
(30) removes tracks before reappearance; C1's DENSE_PEAK buffer (45)
should bridge them. Probe confirmed C1 engaged (3602/9000 frames in
DENSE_PEAK, density p90 = 52) — yet **0/23 events were bridged** in the
exp2 replay (`c1_ctrv_gate` variant): 16 fragmented identically (tracks
present at both endpoints, different ids), 7 not tracked at the death
point at all.

Mechanism: after 30+ coasting frames the CTRV prediction has diverged
beyond the chi2=5.99 gate, so keeping the track alive longer changes
nothing — the binding constraint is COAST ACCURACY at long gaps, not
track lifetime. Widening the gate is not an option (see
gate_sweep/evidence.md). The long-gap group therefore waits for a
better predictor (IMM, post-GT) or appearance cues (out of scope).

Note on exp2's aggregate numbers (moto re-id 224, uIDs 3052): NOT
comparable head-to-head with ctrv_gate — DENSE_PEAK lowers track_thresh
to 0.35, changing the track population (recall up, churn up). Population-
changing variants can only be compared on GT metrics.
