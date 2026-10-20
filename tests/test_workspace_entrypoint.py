import pytest

from tools import caap


def test_help_and_retired_commands_never_launch_anything(monkeypatch, capsys):
    monkeypatch.setattr(caap.subprocess, 'call', lambda *a, **kw: pytest.fail('Unexpected launch'))
    assert caap.main([]) == 0
    assert 'fresh workspace' in capsys.readouterr().out
    assert caap.main(['review']) == 2
    assert caap.main(['reproduce']) == 2


@pytest.mark.parametrize('command', ['detector-train', 'detector-package', 'detector-preview'])
def test_no_implicit_training_packaging_or_inference(monkeypatch, command):
    calls = []
    monkeypatch.setattr(caap.subprocess, 'call', lambda args, **kw: calls.append((args, kw)) or 7)
    assert caap.main([command]) == 7
    assert calls[0][0][-1] == '--help'
    assert calls[0][1] == {'cwd': caap.ROOT}
