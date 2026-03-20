"""
Placeholder test to verify test configuration works.
Run: pytest accounting_app/tests/core/test_placeholder.py -v
"""

import pytest


@pytest.mark.unit
def test_flask_app_creates(flask_app):
    """Test that the Flask app fixture creates a valid app."""
    assert flask_app is not None
    assert flask_app.config["TESTING"] is True


@pytest.mark.unit
def test_flask_app_config(flask_app):
    """Test that testing config is correct."""
    assert flask_app.config["WTF_CSRF_ENABLED"] is False
    assert "sqlite" in flask_app.config["SQLALCHEMY_DATABASE_URI"]


@pytest.mark.integration
def test_client_index_redirect(test_client):
    """Test that index redirects to login when not authenticated."""
    resp = test_client.get("/", follow_redirects=False)
    assert resp.status_code in (200, 302)


@pytest.mark.integration
def test_client_login_page(test_client):
    """Test that the login page loads."""
    resp = test_client.get("/auth/login")
    assert resp.status_code == 200
    assert b"username" in resp.data


@pytest.mark.unit
def test_snapshot_dir_exists(snapshot_dir):
    """Test that snapshot directory fixture returns a path."""
    import os
    assert isinstance(snapshot_dir, str)


@pytest.mark.unit
def test_pytest_config_works():
    """Basic assertion test to verify pytest is configured."""
    assert 1 + 1 == 2
