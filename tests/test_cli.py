import json
import os

from rul_audit.cli import main


def test_demo_command(capsys):
    code = main(["demo"])
    out = capsys.readouterr().out
    assert code == 0
    assert "Uncensored truth leaderboard" in out


def test_evaluate_command_writes_results(tmp_path):
    out_dir = str(tmp_path / "results")
    code = main(["evaluate", "--out", out_dir])
    assert code == 0
    for name in ("evaluation.json", "evaluation.csv",
                 "evaluation_summary.md", "HEADLINE.md"):
        assert os.path.isfile(os.path.join(out_dir, name))
    with open(os.path.join(out_dir, "evaluation.json")) as fh:
        payload = json.load(fh)
    assert payload["n_seeds"] == 20
    assert "headline" in payload


def test_no_command_prints_help(capsys):
    code = main([])
    assert code == 2
