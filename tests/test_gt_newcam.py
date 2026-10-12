"""New-camera GT (code/scripts/gt_newcam.py): the pre-registered window rule and the held-out label."""

import json

from code.scripts import gt_mixed_review, gt_newcam
from code.scripts.gt_newcam import densest_window
from tests.test_gt_mixed_review import complete_audit, factory  # noqa: F401  (fixture)


def test_densest_window_skips_the_warmup_and_finds_the_dense_block():
    counts = {f: 1 for f in range(0, 3000, 5)}
    counts.update({f: 50 for f in range(0, 600, 5)})       # denser, but inside the warm-up
    counts.update({f: 20 for f in range(1500, 2100, 5)})
    assert densest_window(counts, 3000) == (1500, 20.0)


def test_finalize_relabels_the_mixed_role_as_held_out(factory, tmp_path, monkeypatch):
    store = factory()
    complete_audit(store)
    monkeypatch.setattr(gt_mixed_review, "MixedStore", lambda bundle: store)
    monkeypatch.setattr(gt_newcam, "ROOT", tmp_path)
    (tmp_path / "cam/dumps").mkdir(parents=True)
    (tmp_path / "cam/window.json").write_text(
        json.dumps({"start": 0, "end": 6, "rule": "r", "profile": {"0": 1}}), encoding="utf-8")
    frames = [[] for _ in range(6)]
    for (f, _), p in store.preview()[0].items():
        x, y, w, h = map(float, p[2:6])
        frames[f - 1].append([int(p[1]), int(p[7]) - 1, [x, y, x + w, y + h]])
    (tmp_path / "cam/dumps/tracks_baseline.json").write_text(
        json.dumps(dict(start_frame=0, frames=frames)), encoding="utf-8")

    gt_newcam.finalize("cam", "Nghĩa")

    report = json.loads((tmp_path / "cam/reviewed/review.json").read_text(encoding="utf-8"))
    assert report["evaluation_role"] == gt_newcam.HELD_OUT_ROLE
    assert report["window"] == {"start": 0, "end": 6, "rule": "r"}
    assert report["prelabel_seed"]["detector"] == gt_newcam.EVAL_WEIGHTS
    summary = (tmp_path / "cam/reviewed/summary.md").read_text(encoding="utf-8")
    assert gt_newcam.HELD_OUT_ROLE in summary and "development" not in summary
