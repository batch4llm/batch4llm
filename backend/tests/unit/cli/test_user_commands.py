import pytest
from typer.testing import CliRunner
from unittest.mock import MagicMock

from batch4llm.cli.user_commands import user_app
import batch4llm.cli.user_commands as user_commands

runner = CliRunner()


@pytest.fixture
def login_service(monkeypatch):
    service = MagicMock()
    monkeypatch.setattr(user_commands, "get_login_service", lambda: service)
    return service


def test_ensure_admin_skips_when_unset(monkeypatch, login_service):
    monkeypatch.delenv("ADMIN_USERNAME", raising=False)
    monkeypatch.delenv("ADMIN_PASSWORD", raising=False)

    result = runner.invoke(user_app, ["ensure-admin"])

    assert result.exit_code == 0
    login_service.ensure_bootstrap_admin.assert_not_called()


def test_ensure_admin_fails_when_only_one_set(monkeypatch, login_service):
    monkeypatch.setenv("ADMIN_USERNAME", "admin")
    monkeypatch.delenv("ADMIN_PASSWORD", raising=False)

    result = runner.invoke(user_app, ["ensure-admin"])

    assert result.exit_code == 1
    login_service.ensure_bootstrap_admin.assert_not_called()


def test_ensure_admin_creates(monkeypatch, login_service):
    monkeypatch.setenv("ADMIN_USERNAME", "admin")
    monkeypatch.setenv("ADMIN_PASSWORD", "changeme")
    login_service.ensure_bootstrap_admin.return_value = True

    result = runner.invoke(user_app, ["ensure-admin"])

    assert result.exit_code == 0
    login_service.ensure_bootstrap_admin.assert_called_once_with("admin", "changeme")
    assert "Created admin" in result.output


def test_ensure_admin_skips_when_already_exists(monkeypatch, login_service):
    monkeypatch.setenv("ADMIN_USERNAME", "admin")
    monkeypatch.setenv("ADMIN_PASSWORD", "changeme")
    login_service.ensure_bootstrap_admin.return_value = False

    result = runner.invoke(user_app, ["ensure-admin"])

    assert result.exit_code == 0
    assert "already exists" in result.output


def test_ensure_admin_fails_on_invalid_credentials(monkeypatch, login_service):
    monkeypatch.setenv("ADMIN_USERNAME", "ab")
    monkeypatch.setenv("ADMIN_PASSWORD", "changeme")
    login_service.ensure_bootstrap_admin.side_effect = ValueError(
        "Username must be at least 3 characters"
    )

    result = runner.invoke(user_app, ["ensure-admin"])

    assert result.exit_code == 1
    assert "Username must be" in result.output
