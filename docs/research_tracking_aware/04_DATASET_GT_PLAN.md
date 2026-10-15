# Dataset, annotation and leakage plan

**Status: proposed additional work.** Existing GT and prelabels are preserved.
The old NKKN-only submission parked other-camera review on 13 October; this new
research plan needs that decision revisited before a generalization claim.

## Separate four roles, even if only three dataset families exist

| Role | Available evidence | Permitted use | Forbidden use |
|---|---|---|---|
| Detector training | `data/annotations/accident_vehicle/`, cleaned package, `ket_qua_train/training_protocol.json` | Freeze best.pt for the first study; document image groups/source/augmentation families | Calling its validation split an independent MOT test |
| Method development | All three reviewed NKKN segments, 1,800 frames/33,420 boxes | Feasibility, diagnostics, design choices; acknowledge repeated inspection | Renaming Mixed/Dense/Freeflow held-out after tuning on them |
| Calibration/validation | Additional, non-overlapping NKKN recording windows or a separate development recording, to annotate | Risk/action/cost calibration, fusion thresholds, budget-policy operating points; grouped folds | Using a final-camera prefix without declaring adaptation |
| Locked tracking test | At least one other camera, independently adjudicated; not ready yet | One frozen evaluation of registered endpoints | Choosing crops, scores, thresholds, masks or detector version from its results |

Detector data are a different modality/protocol from tracking-video GT. Preserve
the five detector classes and native→project ID mapping. Track motorcycle as the
primary target and all available traffic classes as secondary scope; do not make
accident-event or severity claims from image labels.

## What exists and what is missing

Verified NKKN boxes: 28,775 motorcycle, 4,460 car and 185 bus. Segment ID counts
344/48/154 are not a certified count of unique vehicles across the source. Review
and reconciliation fixed known cases, not every omission in all footage.

`experiments/gt_newcam/` already has camera/window/prelabel infrastructure. Review
decisions are **all blank** in the inspected bundles:

- Cộng Hòa–Trường Chinh 17:00: 974 cases;
- Cộng Hòa–Út Tịch 17:15: 1,647 cases;
- Dương Bá Trạc–Tạ Quang Bửu 08:00: 825 cases.

Files/caches/prelabels are not completed GT. Two Út Tịch recordings at different
times are the same camera; they are not two independent cameras.

The overlap audit found a known detector-training camera in `7_20_2017` footage:
exclude it from claims of camera-disjoint detector generalization. No recognizable
overlap was found for several candidate cameras under that audit; strong crops,
other source versions and older yolo11_vn provenance remain gaps. Review the original
source/near-duplicate groups before final test selection, not just filenames.

## Practical acquisition target

**First feasibility:** use corrected NKKN event windows only. Before investing in
M1–M3, manually recheck all objects in the F1/F3 pilot areas, including objects no
tracker proposed. Keep these additional corrections as a new development GT version.

**Minimum locked expansion target, not an existing count:** one new camera with
6–10 separated clips, about 600–1,500 source frames each, until the collection has:

- at least **500 reviewed motorcycle trajectory segments** on that camera;
- at least **50 independently adjudicated occlusion/reappearance events**;
- at least **30 candidate-competition/crossing events** involving similar bikes;
- at least **150 small-motorcycle trajectories** represented, with native-size bins;
- multiple routes, entry/exit directions, speeds and density conditions.

These targets are an annotation planning floor, not a power calculation or proof
of adequate diversity. Pilot event prevalence/paired sequence variance should set
the final clip count before test access. Do not repeatedly extend the test until
significance appears. Partial trajectories/duplicate appearances must be counted
transparently, with the physical-identity linking policy documented.

Prefer two locked cameras and at least two recording sessions per camera if the
team can annotate them. One new camera supports a statement about that camera;
it cannot estimate population-level camera variability. Native 720p/1080p or higher
footage would test whether the 800×450 information ceiling is a special case.
More network upsampling of NKKN does not create high-resolution sensor data.

## Efficient annotation without selecting a winner's truth

1. **Freeze recording groups and evaluation ROI first.** Save source hashes,
   timestamps/FPS, native dimensions, clip intervals, camera/site/day and rights.
   Choose windows by predeclared time/density strata, not best algorithm margins.
2. **Use YOLO proposals only as proposals.** On development data a fixed high-quality
   detector/global-plus-slicing proposal set is useful. The proposed scheduler's
   selective visibility must not define which test objects enter GT.
3. **Use symmetric tracker assistance.** Union independent ByteTrack and OC-SORT
   proposals, with detector diversity where available. Retain disagreement flags.
   `gt_newcam.union_seed` is reusable but its identity links are hypotheses.
4. **Correct in CVAT or the existing editor.** Human adjusts boxes/class/visibility,
   adds missing objects and resolves identity through full temporal playback. Do
   not accept interpolation through complete occlusion as an observed box.
5. **Run suspicious-transition checks.** Duplicate boxes/IDs per frame, class
   changes, impossible displacement/area jumps, discontinuous reappearance,
   crop/ROI-edge truncation and unlabelled detection clusters become review cases.
   Automatic flags do not auto-split/merge identity.
6. **Perform an exhaustive-area blind pass.** A reviewer sees native/full-context
   footage and a fixed tiling/zoom order, without knowing proposal method. This
   specifically searches for motorcycles every proposal generator missed.
7. **Independent audit.** A second human reviews a stratified fixed sample of
   tracks, absences and identity transitions, with algorithm names hidden. Include
   easy random areas, tiny/distant objects, crossings and long occlusions. Report
   disagreement rates and adjudication; the same annotator twice is not independent.
8. **Version and lock.** Export local one-based MOT plus metadata, ROI, audit log,
   reviewer identities, unresolved/ignore regions and SHA256 receipts. Resolve
   uncertain IDs before official test scoring or declare an ignore policy applied
   identically to all methods. Never edit the old release in place.

An annotation lead and the method tuner should have separated responsibilities.
The tuner should not see interim locked-test rankings. A GT correction after lock
must be blind to method and apply to all methods; publish both GT versions and the
reason rather than choosing the version favorable to the proposal.

## Seed bias must not become a fabricated correction

The approximately 0.04 old-protocol IDF1 pattern is an observed, seed-associated
gap, not a universally known bias magnitude. Audit sample sizes are small and
run-length weighted effects differ from run-count shares. Existing union/interpolation
brackets use assumptions and borrowed strata; they are sensitivity analyses, not
certified upper/lower bounds or de-biased truth.

For new evaluation, adjudicate union membership and identity directly. Audit
proposed-only, baseline-only, shared and neither-proposed regions. Include crops
that create new detections, not just old baseline/C2 disagreements. Do not use
policy outputs to automatically expand GT and then score that policy as correct.
Repeat primary comparisons on a conservative independently reviewed subset and
report the full GT result as well; subset selection must not depend on winners.

## Evaluation subsets and exact construction

| Subset | Registered label/selection | Metric/interpretation |
|---|---|---|
| Small motorcycles | Native GT height <20, 20–40, ≥40 px; also image-normalized height for cross-resolution cameras | One-to-one motorcycle detection recall; track coverage and time to first detection |
| High density | GT object count stratum assigned by annotators before policy results; online density is a separate estimate | Full-sequence HOTA/AssA/IDF1 for fixed selected clips |
| Long occlusion | Human visibility/reappearance event, e.g. ≥10 source frames with FPS-normalized seconds also given | ID continuity, IDSW/event, reacquisition delay; do not label absent pixels as detections |
| Ambiguous identity | Human-confirmed close/crossing competitors, not the proposed risk score | Event failure rate; context-preserving windows and full-sequence main metrics |
| Distant region | Camera-specific fixed polygon and native size, declared before comparison | Recall and identity-event results; no moving boundary to hide missed bikes |
| ROI boundary | GT box straddles mask versus whole/interior, plus fixed edge-distance bins | Isolate context erasure, score shifts and membership effects |
| Cross camera | Camera/site/session groups separate from all fitting | Per-camera metrics and camera-balanced aggregate; no test-camera threshold fit |

Do not simply delete non-small GT while leaving every prediction in the evaluator:
that invents false positives for other objects. Main official metrics use all
in-scope objects for the evaluated class. Subset recall uses matches against the
full GT before attribution; identity-event diagnostics keep their temporal context.
If reporting subset HOTA, define a common ignore/preprocessing protocol first and
label the changed task explicitly.

## Split and lock procedure

Register `train_sources`, `development`, `calibration`, `validation` and `locked_test`
manifests before new method development. Group augmented relatives and temporally
overlapping trajectories. Add guard bands at least the risk horizon plus maximum
track-history horizon; longer bands are needed when a vehicle persists across clips.
Fit risk/action benefit/cost/fusion on development/calibration only, select a fixed
operating point on validation, and serialize the full policy before unlocking test.

Existing C1's whole-sequence, non-GT percentile is not the new test-calibration rule.
No per-camera test adaptation in the primary protocol. If unsupervised warm-up is
studied, give every method the same fixed prefix and report it as a separate setting.

For uncertainty, resample independent clips within camera and report each camera.
Only bootstrap cameras when there are enough genuinely independent cameras to make
that interpretable. With one new camera, interval language remains conditional on
that camera; thousands of adjacent frame samples cannot change the number of cameras.

Human-only dependencies: footage permission/provenance confirmation, ambiguous
identity adjudication and an independent reviewer. The assistant can prepare
manifests, proposals and audit queues later, but cannot certify these human facts.
