import pytest
from unittest.mock import ANY, MagicMock

from batch4llm.service.login_service import LoginService


@pytest.fixture
def db():
    db = MagicMock()
    db.users.get_by_username.return_value = None
    return db


@pytest.fixture
def login_service(db):
    return LoginService(
        db, secret_key="secret", algorithm="HS256", token_expire_minutes=1
    )


def test_ensure_bootstrap_admin_creates_when_missing(login_service, db):
    created = login_service.ensure_bootstrap_admin("admin", "changeme")

    assert created is True
    db.users.add.assert_called_once_with(
        username="admin", password_hash=ANY, is_admin=True
    )


def test_ensure_bootstrap_admin_skips_when_username_taken(login_service, db):
    db.users.get_by_username.return_value = {"username": "admin"}

    created = login_service.ensure_bootstrap_admin("admin", "changeme")

    assert created is False
    db.users.add.assert_not_called()


def test_ensure_bootstrap_admin_raises_on_invalid_username(login_service, db):
    with pytest.raises(ValueError, match="Username must be"):
        login_service.ensure_bootstrap_admin("ab", "changeme")
    db.users.add.assert_not_called()


def test_ensure_bootstrap_admin_raises_on_invalid_password(login_service, db):
    with pytest.raises(ValueError, match="Password must be"):
        login_service.ensure_bootstrap_admin("admin", "short")
    db.users.add.assert_not_called()
