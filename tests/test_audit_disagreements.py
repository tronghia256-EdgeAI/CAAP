"""Run grouping and IoU matching behind the disagreement audit."""

from code.scripts.audit_disagreements import runs, unmatched


def test_unmatched_keeps_only_boxes_without_an_iou_partner():
    a = [(1, [0, 0, 10, 10]), (2, [50, 50, 60, 60])]
    assert unmatched(a, [(9, [1, 1, 11, 11])]) == [1]
    assert unmatched(a, []) == [0, 1]


def test_runs_break_on_frame_gaps_and_id_changes():
    b = [0, 0, 1, 1]
    fl = [[(1, b), (2, b)], [(1, b)], [], [(1, b)]]
    found = runs(fl, [[0, 1], [0], [], [0]])
    assert sorted((r[0][1], len(r)) for r in found) == [(1, 1), (1, 2), (2, 1)]
