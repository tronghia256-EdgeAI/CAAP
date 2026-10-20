from types import SimpleNamespace
import sys

import numpy as np
import pytest

from code.detection.detector import Detector


class Tensor:
    def __init__(self, values):
        self.values = np.asarray(values)

    def cpu(self):
        return self

    def numpy(self):
        return self.values


class Boxes:
    xyxy = Tensor([[1, 2, 10, 20], [5, 6, 15, 25], [7, 8, 17, 28]])
    conf = Tensor([.9, .8, .7])
    cls = Tensor([0, 3, 9])

    def __len__(self):
        return 3


def mock_model(monkeypatch, names, boxes):
    calls = []
    class Model:
        def __init__(self, *args, **kwargs):
            self.names = names
            calls.append(('load', args, kwargs))

        def __call__(self, frame, **kwargs):
            calls.append(('infer', frame, kwargs))
            return [SimpleNamespace(boxes=boxes)]
    monkeypatch.setitem(sys.modules, 'ultralytics', SimpleNamespace(YOLO=Model))
    return calls


def test_missing_checkpoint_never_loads_or_substitutes_a_model(monkeypatch, tmp_path):
    monkeypatch.setitem(sys.modules, 'ultralytics', SimpleNamespace(
        YOLO=lambda *a, **kw: pytest.fail('Must not load or download fallback weights')))
    with pytest.raises(FileNotFoundError):
        Detector(str(tmp_path / 'missing.pt'))


def test_project_classes_remain_canonical_and_no_old_roi_is_applied(monkeypatch, tmp_path):
    weights = tmp_path / 'detector.pt'
    weights.write_bytes(b'test checkpoint')
    calls = mock_model(monkeypatch, {0: 'Accident', 3: 'motorcycle', 9: 'person'}, Boxes())
    detector = Detector(str(weights), img_size=448, task='detect')
    frame = np.full((32, 32, 3), 123, dtype=np.uint8)
    result = detector.detect(frame)
    assert result.shape == (2, 6)
    assert result[:, 5].tolist() == [4, 1]
    np.testing.assert_array_equal(result[:, :4], [[1, 2, 10, 20], [5, 6, 15, 25]])
    assert calls[0] == ('load', (str(weights),), {'task': 'detect'})
    assert calls[1][1] is frame
    assert calls[1][2] == dict(conf=.1, imgsz=448, verbose=False)


def test_empty_detection_contract(monkeypatch, tmp_path):
    weights = tmp_path / 'detector.pt'
    weights.write_bytes(b'test')
    mock_model(monkeypatch, ['car'], None)
    assert Detector(str(weights)).detect(np.zeros((2, 2, 3))).shape == (0, 6)


def test_unrelated_class_map_is_rejected(monkeypatch, tmp_path):
    weights = tmp_path / 'detector.pt'
    weights.write_bytes(b'test')
    mock_model(monkeypatch, {0: 'person'}, None)
    with pytest.raises(ValueError, match='supported vehicle classes'):
        Detector(str(weights))
