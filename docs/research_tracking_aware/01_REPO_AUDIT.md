# Repository audit and evidence ledger

**Snapshot: main `9b6fd34`, 15 October 2026. Read-only audit.**
Scope: source/configuration paths below, final and superseded result families,
GT receipts and review CSVs, manuscript and references, Git branch/history and
existing profiling records. No new inference or expensive replay was run.

## Repository and branch state

The source tree contains detector wrappers, an adaptive ByteTrack implementation,
vendored OC-SORT/BoT-SORT, review/ROI/audit tools, cached-detection runners,
evaluation, profiling and two manuscript trees. Primary manuscript:
[paper/jrtip/main.tex](../../paper/jrtip/main.tex). Older `paper/sections/` is not the
current results authority.

| Branch/worktree | Observed head | Meaning |
|---|---|---|
| `main` | `9b6fd34` | Current manuscript/result records |
| `exp/ocsort-ctrv`, `../CAAP-ocsort` | `2d50fae` | New motion arm inside OC-SORT; not a main source file |
| `exp/roi-filter-only`, `../CAAP-nomask` | `3cff2dc` | No-pixel-mask ablation and rounded-box scope check |
| `fix/invalid-tracker-state`, `../CAAP-fix` | `9d2a0f6` | Common degenerate-state expiry |
| `claude/jolly-lumiere-374d07` | `28c697e` | Separate initial-commit worktree; no evidence it is an experiment authority |

**VERIFIED:** result provenance can point to a worktree implementation absent from
main. Reproducing all runs from today's main would be incorrect. No branches were
merged. The two untracked `bracket_best85_roi_20261013_pareto_{960,1280}.json` files
present before this task were preserved and are not final-run evidence.

## Evidence table

V = VERIFIED; I = INFERRED; U = UNVERIFIED. A verified artifact is not automatically
an unbiased or independently replicated scientific result.

| Finding/status | File path | Function/configuration | Inspected evidence | Risk | Recommended action |
|---|---|---|---|---|---|
| V: detector input contract is reusable | `code/detection/detector.py` | `Detector.detect`, `DETECTOR_CONF=0.1` | Native-coordinate Nx6 boxes; name-based mapping to car/motorcycle/bus/truck/accident | Raising the floor silently disables BYTE low-score recovery | Preserve floor, mapping, precision and postprocess across policies |
| V: mask occurs **before** YOLO | same | `pixel_mask`, `cv2.bitwise_and`, model call | YOLO still receives a rectangular full-frame tensor | Calling black masking a compute saving; starting diagram's ordering is inaccurate | Time actual tensors; separate masking, cropping and evaluation scope |
| V: ROI membership is footpoint-based | `code/scripts/gt_roi.py:101` | `contains_box`, `filter_frames`, `pixel_mask` | Boundary included; GT/prediction membership versus raster-rounded polygon | A retained GT box can straddle erased pixels | Freeze rule; keep context policy explicit |
| V: pipeline is monolithic | `code/pipeline.py:215` | `Pipeline.process` | Context → detector → tracker update → C3 | Adding refinement after update risks two predictions/updates per frame | Introduce a read-only preview and one final commit in a future adapter |
| V: runtime exits expire state | `code/pipeline.py:229` | tracked/lost pruning | State outside ROI is removed | Re-entry can receive new ID; branches differ in invalid-box handling | Freeze common exit/rounding policy before comparisons |
| V: OC-SORT is stateful in `update` | `code/tracker/external/ocsort/ocsort.py:198` | `OCSort.update` | Increments frame, predicts, associates, performs ORU/birth/death | Calling it to obtain risk then calling again changes time and IDs | Zero-crop replay must exactly reproduce frozen OC-SORT |
| V: OC-SORT class patch stores birth class | same | `classes_keep`, `trk.cls`, `associate` | Main `update` passes geometry/scores, not classes, into association | Class metadata is not hard class gating; unlike a class-aware ByteTrack arm | Report native behavior; any common class gate is a separately named adaptation |
| V: matched thresholds are partial matching | `code/scripts/run_external_trackers.py` | `OCSORT_MATCHED`, `BOTSORT_MATCHED` | OC-SORT's single association/birth threshold differs structurally from BYTE | Calling all birth/association rules identical | Retain published-default and matched-score controls; list residual differences |
| V: BoT-SORT reference disables features | same; `external/botsort/bot_sort.py` | `with_reid=False`, `cmc_method='none'` | Geometry-only reference | Presenting it as full BoT-SORT SOTA | Name it BoT-SORT without ReID/GMC; optional full version needs CPU timing |
| V: C2 covariance is an association mechanism | `code/tracker/adaptive_bytetrack.py:227` | `_first_association_cost` | Lost CTRV tracks use a same-class uncertainty gate | Claiming this already allocates detector computation | Reuse mathematical state access only as a candidate feature |
| V: shared class configuration exists | same:216; `ClassAwareSTrack` | class-level CTRV/NSA settings | A single-tracker limitation is documented | Parallel counterfactual arms can contaminate one another | Isolate processes or eliminate globals in a future adapter |
| V: C1 calibration differs between run generations | `run_roi_paper.py:324`; `experiments/c1_recalibration/evidence.md` | `c1_rule`, `c1_calibrate` | Final p75 threshold from DEFAULT probe outside GT; v5 used old threshold | Mixing v5 and final C1 claims | Final profiles only; keep superseded tables historical |
| I: C1 uses transductive sequence information | same | percentile over all non-GT frames | Those frames can occur after earlier scored Mixed frames | Calling it strictly online calibration on a held-out stream | New scheduler fits on separate development/calibration clips only |
| V: C1 filter choice can persist for track life | `adaptive_bytetrack.py:88`; `c1_birth_regime.py` | `activate`, `_should_use_ctrv` | Final diagnosis links DEFAULT-born linear tracks to switches | Regime switching is not equivalent to changing every existing track's model | Do not recycle C1 as an active detector scheduler |
| V: C3 thresholds are module constants | `code/models/track_reliability.py` | `ReliabilityScore.__post_init__` | 0.70/0.40; weights configurable, threshold fields in YAML are not authoritative here | A config threshold sweep may do nothing unless actual runtime constants change | Retire C3 from main method; audit realized filtering, not YAML labels |
| V: C3 is inert in scored final tracking rows | `experiments/paper_final/*/*/metrics.json` | `c1c2c3` vs `c1c2c3_raw` | Exact metric equality in inspected final detector/mask families | Generalizing to all thresholds/tasks | State only observed tracking result at the tested threshold |
| V: original replay has fake brightness | `code/scripts/compare_motion_models.py:200` | `run_replay` | Constant gray frame | C1 conclusions from that path are context-confounded | Reuse only video helper; use current exact cached context path |
| V: final cache preserves real ROI brightness | `code/scripts/run_roi_paper.py:232` | `read_cache`, `CachedContext`, `cache` | Per-chunk hashes; actual ROI means; sequential frame indexing | It does not contain arbitrary future crop actions or risk features | Extend cache design on a new branch after gates, not by relabeling old caches |
| V: ASF seek hazard is handled | `compare_motion_models.py:120` | `open_video` | Sequential `grab`, not distant keyframe seek | Frame/GT misalignment can masquerade as tracking failure | Retain absolute/local/MOT index tests |
| V: official HOTA agrees in inspected profile | `experiments/paper_final/best85_roi_final/640/metrics.json` | `trackeval_crosscheck` | Maximum HOTA-array difference 0 on all three segments | Assuming all metrics therefore match | Use official TrackEval as new primary evaluator |
| V: small CLEAR differences remain | same | repository versus `trackeval_MOTA` | Dense OC-SORT matched 0.4262218 vs 0.4260657; some other rows differ by 1–3 events | Mixing official IDSW with repository MOTA/CI | Name evaluator; reconcile definitions and version before new comparisons |
| V: ALL is class-agnostic | `run_roi_paper.py:451`; `eval_hota_ci.py` | class filters | Per-class rows versus ALL | Wrong-class overlaps can receive credit in ALL | Motorcycle primary; class-aware official multiclass secondary |
| V: bootstrap resets identity across blocks | `eval_hota_ci.py:351`; `run_roi_paper.py:442` | `block_table`, `paired_ci` | Shared starts, fresh IDs/CLEAR state per block | Treating it as camera-independent or full-sequence IDF1 uncertainty | Keep diagnostic only; sequence/camera units for new primary uncertainty |
| V: seed sensitivity is modelled, not ground-truth correction | `code/scripts/seed_bracket.py` | `sources_and_shares`, `union_seed`, interpolation | Synthetic union-GT upper scenario and borrowed audit strata | Calling scenarios rigorous bounds or corrected true scores | Call sensitivity scenarios; human-adjudicate for main results |
| V: GT sampling audit is narrow | `experiments/seed_bias/audit_shares.json`; `evidence.md` | run-level strata | 148 verdicts, 32-group repair, 8/10 non-seed extra runs in key strata | Universal 0.04 IDF1 bias or proof all remaining boxes are correct | Larger independent membership and identity audit |
| V: camera overlap has a known positive | `experiments/detector_leakage/evidence.md` | `audit_camera_overlap` | 75 v12 images from `7_20_2017` camera | Using that camera as unseen detector-test data | Exclude it; no-match pHash is evidence, not a universal absence proof |
| V/U: current checkpoint has records, older one incomplete | `ket_qua_train/training_protocol.json`; same overlap report | best.pt vs `weights/yolo11_vn.pt` | best.pt development training receipt; older Roboflow version unrecorded | Treating all detector versions equally leakage-audited | Freeze best.pt first; qualify older checkpoint as sensitivity reference |
| V: final timing is absent locally | `data/processed/paper_runs/{best85_roi_final,yolo11vn_roi_final2,best85_roi_nomask2,yolo11vn_roi_nomask2}` | `status.json`, benchmark paths | Score completed; no final benchmark/trial JSON at inspection | Relabelling replay FPS or throttled old measurements as real time | Schedule E6 later under fixed thermal/power controls |
| V: latency baseline set omits OC-SORT | `run_roi_paper.py:567` | `benchmark` arm loop | Baseline/C2/C1C2C3 only | An accuracy leader has no matched end-to-end CPU measurement | Include every main accuracy/scheduler baseline in new profiler |
| V: independent GT is not ready | `experiments/gt_newcam/README.md`; three review CSVs | parked decision; decision column | All 974/1647/825 rows blank | Calling prelabels completed held-out GT | Budget human review; explicitly revisit old submission scope |
| V: manuscript still contains unresolved claims | `paper/jrtip/main.tex:90,101,112,639,645,683,914` | abstract/setup/TODOs | Real-time language before final timing; tracker misses described as detector misses; old C1 wording; HOTA@0.5 emphasis | Submission before methodological reconciliation | Preserve manuscript now; use a future revision checklist |
| V: bibliography predates the proposed positioning | `paper/jrtip/references.bib` | 61 bibliography entries | Existing tracking references do not yet cover the central adaptive-perception works in this plan | Reusing the old related-work section could miss the closest overlap | Build a new mechanism comparison from the verified references in `02_PRIOR_ART.md`; no bibliography edits in this phase |
| V: legacy severity remains in runtime | `code/pipeline.py:256`; `docs/PAPER_SCOPE.md` | classifier/alert branch | Severity removed from paper; runner bypasses branch | Mistaking legacy code for binary alert validation | Exclude incident/MAPPO claims from new method |

## GT inventory verified from local MOT files

Receipt: `data/annotations/paper_gt_reconciliation/reconcile_90026162a7963db7/reconciled_e880ead8.json`.
Hashes below were recomputed during this read-only audit.

| Segment, absolute interval | Boxes | IDs within segment | Motorcycle / car / bus boxes | GT SHA256 |
|---|---:|---:|---:|---|
| Dense `[10700,11300)` | 21,749 | 344 | 19,213 / 2,536 / 0 | `f4338ee06a1b878c07b80e681ed00721f2a57c97b508028d0b91db81dc927a50` |
| Freeflow `[6400,7000)` | 2,503 | 48 | 2,294 / 209 / 0 | `89a6a7de2c4ed047b234810e3042bfd226766872cbabfd7dc0386742aa9de07a` |
| Mixed `[2500,3100)` | 9,168 | 154 | 7,268 / 1,715 / 185 | `64e1720ee4cb5b31f776c6f3a4980dac83b1acb465bfb4f4bc652ec60611bc0f` |

Total 33,420 boxes; do not call the sum of segment IDs unique physical vehicles.
The manuscript statement that all annotations contain only cars/motorcycles misses
Mixed's 185 bus boxes. GT review is valuable but does not establish completeness.

## Result-family validity

| Family | Valid use | Invalid inference |
|---|---|---|
| `best85_roi_final`, four sizes | Fixed-checkpoint masked-ROI development comparison; full-alpha HOTA available | Independent test; completed CPU Pareto frontier |
| `yolo11vn_roi_final2/1280` | Reference under same mask, branch-specific expiry fix | Fully audited training provenance or same detector architecture |
| `best85_roi_nomask2`, four sizes; `yolo11vn_roi_nomask2/1280` | Completed mask ablation under filter-only branch | Every scene necessarily improves without the mask |
| `*_ocsortctrv` | Negative/null result for a specified filter-swap arm with ORU deviations | Proof that all possible motorcycle-aware models cannot help |
| `gt_ablation`, early seed-bias files | Historical seed-generation and audit provenance | Directly comparable new-checkpoint/new-mask runtime |
| v4, failed/interrupted generations | Failure diagnosis and preserved checkpoints | Final results |
| v5/old Pareto | Exploratory operating-point evidence with stated limitations | Final C1 calibration or final timing |

The no-mask runs are now score-complete according to their receipts; the workflow
document still describes them as running. This is a documentation lag, not a reason
to rerun or overwrite them.

## Reuse, retire, redesign

**Reuse:** native-coordinate detector contract, frozen weights, sequential decoder,
ROI validation, hashed receipts/chunks, review/editor infrastructure, upstream source
verification, official HOTA bridge, fixed detection baselines, stage-timer ideas.

**Retire from the new contribution:** C1 regime rules, C2 as the proposed novelty,
C3 downstream filtering, MAPPO training, accident/severity evaluation, hand-picked
HOTA localization thresholds, and detector-only/replay FPS as end-to-end evidence.
Keep their source and results intact as controls/history.

**Redesign later:** tracker preview/commit boundary; crop-aware detector interface;
action cache keyed by frame/crop/tensor/model/scope/fusion version; discovery policy;
causal feature logging; common fusion; complete all-backbone CPU profiler; independent
GT lock. These are proposed tasks, not changes made by this audit.
