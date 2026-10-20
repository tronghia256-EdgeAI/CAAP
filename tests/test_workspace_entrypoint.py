"""The entry point must not accidentally run experiments or change paths."""
from pathlib import Path

import pytest

from tools import caap


def test_no_command_only_shows_help(monkeypatch, capsys):
    monkeypatch.setattr(caap.subprocess, 'call', lambda *a, **kw: pytest.fail('Unexpected execution'))
    assert caap.main([]) == 0
    assert 'Usage:' in capsys.readouterr().out
    assert caap.main(['unknown']) == 2


@pytest.mark.parametrize('command', ['reproduce', 'detector-train'])
def test_experiment_tools_without_arguments_only_show_their_help(monkeypatch, command):
    calls = []
    monkeypatch.setattr(caap.subprocess, 'call', lambda args, **kw: calls.append((args, kw)) or 0)
    assert caap.main([command]) == 0
    assert calls[0][0][-1] == '--help'
    assert calls[0][1] == {'cwd': caap.ROOT}


def test_review_forwards_space_containing_arguments_and_exit_status(monkeypatch, tmp_path):
    calls = []
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(caap.subprocess, 'call', lambda args, **kw: calls.append((args, kw)) or 7)
    assert caap.main(['review', '--reviewer', 'Nghĩa with spaces']) == 7
    args, options = calls[0]
    assert args[-5:] == ['code.scripts.gt_newcam_review', '--camera', 'duongbatrac_0800',
                        '--reviewer', 'Nghĩa with spaces']
    assert options == {'cwd': caap.ROOT}
    assert Path.cwd() == tmp_path
