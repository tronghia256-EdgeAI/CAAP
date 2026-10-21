# Scope after the restart — 20 October 2026

Nghĩa asked for the old tracking GT and all of the old paper material to be removed from the repository so the work can be redone.
This decision supersedes the old GT, ROI, C1/C2/C3, deadline and draft plans.

## Research question (fixed 20 October 2026)

**Seed bias in MOT ground truth annotated with tracker assistance.** When GT is created by
reviewing the output of a tracker, how much does that GT favour the seed tracker (IDF1, HOTA@0.5)? How does the bias depend
on reviewer recall, and at what level are the rankings between trackers reversed? Which cheap protocol
(union seeding, blind adjudication of disagreement regions, bracket bound) removes this bias?

- The "truth" is the public GT of FastTrack (traffic CCTV), MOT17 and DanceTrack. Seed-then-review GT is
  simulated from tracker output and the public GT. The human mini-study is deferred: it is done only if reviewers
  request it in the revision round (Nghĩa's decision, 20 October 2026).
- No new tracking GT needs to be created, there is no need to beat SOTA, and latency is not measured.
- The seed-bias finding from the previous research round is mentioned only qualitatively, as the observation that led to the question.
  No numbers are quoted, and no GT or evidence is restored from the backup.
- Venue: Q1 by SJR (Scopus). The candidates and rationale are in `CLAUDE.md`. The quartile must be rechecked on
  scimagojr.com before submission.
- Protocol, hypotheses and stopping rules: `docs/PROTOCOL.md`, approved by Nghĩa and frozen on
  20 October 2026.

## Status

- No tracking GT, ROI, pre-labels, review sessions or old results remain in the
  working tree; the backup is outside the repository and is not to be retrieved on one's own initiative as an evaluation source.
- On 20 October 2026, the HCMC videos, the detector training dataset/labels, `detector.pt`, the training provenance, the detector
  tool and the vendored ByteTrack were moved to `C:/Users/ASUS/Desktop/CAAP_detector_backup_20261020`
  (with `MANIFEST.sha256`); do not restore them on your own initiative.
- Keep the metrics (`code/evaluation/`) as a base tool; they are not considered a new contribution.
- The C1/C2/C3 pipeline, severity classifier, Telegram and the MAPPO branch are no longer present.
- Severity remains out of scope.

## When redoing the work

Design the objective, the camera/source split, the annotation conventions and the protocol before
creating new GT/evaluation. A pre-label source is not ground truth; completeness and identity must be
checked independently of the model being evaluated. Using an old model to create pre-labels does not by itself
prove the GT wrong or right.

The old detector training metrics (now in the backup) are not evidence for the new paper.

From 20 October 2026, the code and docs of the new direction are pushed to the branch `paper/seed-bias` (approved
by Nghĩa). Do not release data, videos, labels or weights without new instructions. Moving the
backup does not rewrite the Git history.
