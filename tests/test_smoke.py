"""Bootstrap smoke tests — keep the package importable and CLI wired."""

from __future__ import annotations

from click.testing import CliRunner

import gestureos
from gestureos.cli import main


def test_version_is_set() -> None:
    assert gestureos.__version__ == "0.1.0"


def test_cli_no_command_runs() -> None:
    result = CliRunner().invoke(main, [])
    assert result.exit_code == 0
    assert "gestureos" in result.output


def test_cli_version_flag() -> None:
    result = CliRunner().invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output
