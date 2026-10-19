"""Camera isolation, resumable human decisions and annotation-only export."""
import json
import pytest

from code.scripts import gt_mixed_review, gt_newcam, gt_newcam_review, gt_roi_scope
from code.scripts.gt_mixed_review import MixedStore
from code.scripts.gt_roi import save_roi
from tests.test_gt_mixed_review import factory  # noqa: F401


@pytest.fixture
def camera(factory, tmp_path, monkeypatch):
    parent = factory()
    root = tmp_path/'newcam'
    (root/'cam').mkdir(parents=True)
    (root/'cam/window.json').write_text(json.dumps(dict(start=0,end=6,profile={})), encoding='utf8')
    (root/'cam/seed.json').write_text(json.dumps(dict(trackers=['proposalA','proposalB'])), encoding='utf8')
    monkeypatch.setattr(gt_newcam, 'ROOT', root)
    monkeypatch.setattr(gt_newcam, 'CAMERAS', {'cam': ('source.asf',8)})
    monkeypatch.setattr(gt_newcam, 'parent_bundle', lambda _:parent.bundle)
    monkeypatch.setattr(gt_roi_scope, 'REPO_ROOT', tmp_path)
    monkeypatch.setattr(gt_roi_scope, 'POINTER', tmp_path/'mixed_pointer.json')
    return parent, root


def enable_roi(parent):
    save_roi(parent.bundle, [[0,0],[200,0],[200,450],[0,450]], True,
             'Nghĩa','Readable road',1,None)


def complete(store):
    store.record_seen(range(1,store.manifest['n_frames']+1))
    for i in range(len(store.rows)):
        store.save(i,'KEEP','Human fixture review')


def test_no_saved_roi_never_creates_or_approves_review(camera):
    parent, root = camera
    before = parent.path.read_bytes()
    with pytest.raises(ValueError,match='enabled ROI'):
        gt_newcam_review.prepare_review('cam',progress=None)
    assert parent.path.read_bytes()==before
    assert gt_newcam.roi_child('cam') is None


def test_prepare_resume_preserves_parent_and_existing_decisions(camera):
    parent, root = camera
    enable_roi(parent)
    snapshot={n:(parent.bundle/n).read_bytes() for n in ['decisions.csv','edits.json','roi.json']}
    child=gt_newcam_review.prepare_review('cam',progress=None)
    store=MixedStore(child)
    # A real saved manual edit belongs to the new review, not to its parent.
    fields=list(store.source_rows[(1,1)]);fields[2]='110'
    store.add_event(dict(op='upsert',fields=fields,case_rank=1))
    edited=store.edit_path.read_bytes()
    assert gt_newcam_review.prepare_review('cam',progress=None)==child
    assert MixedStore(child).edit_path.read_bytes()==edited
    assert all((parent.bundle/n).read_bytes()==raw for n,raw in snapshot.items())
    assert not gt_roi_scope.POINTER.exists()


def test_export_rejects_pending_gt_without_scoring(camera,monkeypatch):
    parent, root=camera;enable_roi(parent)
    child=gt_newcam_review.prepare_review('cam',progress=None)
    monkeypatch.setattr(gt_mixed_review,'score_variants',lambda *a,**kw:pytest.fail('Test score must remain sealed'))
    with pytest.raises(ValueError):
        gt_newcam_review.export_review('cam',child,'Nghĩa')
    assert not list((root/'cam/reviewed').glob('*/review.json'))


def test_export_is_annotation_only_versioned_and_uses_camera_folder(camera,monkeypatch):
    parent, root=camera;enable_roi(parent)
    child=gt_newcam_review.prepare_review('cam',progress=None)
    complete(MixedStore(child))
    monkeypatch.setattr(gt_mixed_review,'score_variants',lambda *a,**kw:pytest.fail('Test score must remain sealed'))
    first=gt_newcam_review.export_review('cam',child,'Nghĩa')
    original=(first/'gt_roi.txt').read_bytes()
    second=gt_newcam_review.export_review('cam',child,'Nghĩa')
    assert first!=second and first.parent==second.parent==root/'cam/reviewed'
    assert (first/'gt_roi.txt').read_bytes()==original
    report=json.loads((first/'review.json').read_text(encoding='utf8'))
    assert report['camera']=='cam' and report['reviewer']=='Nghĩa'
    assert not report['evaluation_performed'] and report['variants']=={}
    assert report['scored_detector'] is None and report['proposed_detector']['name']=='best_640'
    assert report['protocol_status']=='ANNOTATION_ONLY_NOT_SCORED'
    assert 'independence checks remain separate' in report['evaluation_role']


def test_changed_parent_roi_cannot_export_a_different_session(camera):
    parent,root=camera;enable_roi(parent)
    child=gt_newcam_review.prepare_review('cam',progress=None)
    complete(MixedStore(child))
    save_roi(parent.bundle,[[0,0],[220,0],[220,450],[0,450]],True,'Nghĩa','New scope',1,
             gt_roi_scope.sha256(parent.bundle/'roi.json'))
    with pytest.raises(ValueError,match='parent ROI changed'):
        gt_newcam_review.export_review('cam',child,'Nghĩa')


def test_parent_window_mismatch_fails_before_review(camera):
    parent,root=camera
    (root/'cam/window.json').write_text(json.dumps(dict(start=1,end=7)),encoding='utf8')
    with pytest.raises(ValueError,match='window'):
        gt_newcam_review.check_parent('cam')
