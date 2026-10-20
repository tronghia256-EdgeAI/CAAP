import pytest

from tools import caap


def test_help_and_retired_commands_never_launch_anything(monkeypatch, capsys):
    monkeypatch.setattr(caap.subprocess, 'call', lambda *a, **kw: pytest.fail('Unexpected launch'))
    assert caap.main([]) == 0
    assert 'seed bias' in capsys.readouterr().out
    for retired in ('review', 'reproduce', 'detector-train', 'detector-review'):
        assert caap.main([retired]) == 2


def test_test_command_runs_pytest_from_repo_root(monkeypatch):
    calls = []
    monkeypatch.setattr(caap.subprocess, 'call', lambda args, **kw: calls.append((args, kw)) or 0)
    assert caap.main(['test', '-q']) == 0
    assert calls[0][0][-2:] == ['pytest', '-q']
    assert calls[0][1] == {'cwd': caap.ROOT}
