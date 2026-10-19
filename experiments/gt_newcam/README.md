# New-camera annotation: DuongBaTrac reopened

**Decision (Nghĩa, 2026-10-19).** Resume human GT review for **DuongBaTrac only**.
The other two cameras remain parked. This is annotation preparation, not an
automatic certification of independence or permission to unlock test scores.

Double-click **`review_gt_duongbatrac.cmd`** from the repository root:

1. First launch opens the correct camera's ROI editor. Draw the readable road
   region, save ROI and close that window.
2. The launcher builds an isolated ROI queue and opens the familiar A/K/V/E
   reviewer with Nghĩa's name. Decisions/edits autosave; reopening resumes.
3. Finish exports a **versioned annotation-only** GT under
   `experiments/gt_newcam/duongbatrac_0800/reviewed/`. No tracker is scored.

Use `review_gt_duongbatrac.cmd --edit-roi` to draw a new scope; older sessions
are preserved. The Mixed/NKKN active review pointer is untouched. Do not use the
generic Mixed finish button for new-camera exports.

Current proposals come from the existing12 detector/pipeline outputs. That
improves proposal coverage but does not remove seed dependence or establish
completeness. Inspect raw frames as well as boxes; add missed vehicles and mark
unobservable identity relationships for later adjudication. Full-frame playback
coverage recorded by the tool is not independent annotation agreement.

`gt_newcam finalize` now exports without evaluation by default; `--evaluate`
is an explicit separate operation after the evaluation protocol is locked.
Python callers retain their legacy default for compatibility; the new camera
app always passes `evaluate=False` and checks the expected ROI session.

The decision below is historical and remains applicable to the parked cameras.

**Decision (Nghĩa, 2026-10-13).** The paper reports development results on the
NKKN camera only, and states that as a limitation. No GT for an independent
camera will be reviewed for this submission.

**What exists, if the test is taken up later** (`code/scripts/gt_newcam.py`):

1. **Windows.** One 600-frame window per camera was pre-registered and
   committed in `53d5b1a`, before any tracker ran on these clips.
2. **Detections.** Cached for each window with yolo11_vn@1280 and with best.pt
   at 640 and 448 (gitignored `detections_*.npz`).
3. **Review bundles.** `experiments/gt_qa/<camera>_review` holds pre-labels
   seeded from the union of 12 (detector, variant) outputs. See `seed.json`.
   - This seed roughly triples the review cases relative to a baseline-only
     seed: 825, 974 and 1,647 cases before the ROI.
   - The bundles have not been reviewed.
   - The baseline-only bundles are kept, unreviewed, in
     `data/processed/superseded_bundles/`.

**Open design choice.** The choice between a union seed and a baseline seed
plus a blind crop pass over the disagreements is open
(`experiments/seed_bias/evidence.md`).
