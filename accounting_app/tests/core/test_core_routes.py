"""
Phase 2: Core Route Tests
=========================
Tests for login, dashboard, and settings routes.
Uses authenticated_page fixture for routes requiring login.

Run: pytest accounting_app/tests/core/test_core_routes.py -v
"""

import pytest
from playwright.sync_api import Page, expect


# ========================================================================
# Helpers
# ========================================================================

def expect_no_500(page: Page, url: str, wait_until="networkidle"):
    """Navigate to URL and assert no server error.

    Returns the response object for further assertions.
    """
    response = page.goto(url, wait_until=wait_until)
    body = page.locator("body").text_content()
    assert "Internal Server Error" not in body, f"500 error at {url}"
    assert "Traceback" not in body, f"Python traceback at {url}"
    assert response.status < 500, f"Server error {response.status} at {url}"
    return response


# ========================================================================
# Login Tests
# ========================================================================

@pytest.mark.e2e
def test_login_page_loads(page: Page, flask_server: str):
    """GET /auth/login → 200, has login form."""
    response = page.goto(f"{flask_server}/auth/login")
    assert response.status == 200
    expect(page.locator("#username")).to_be_visible()
    expect(page.locator("#password")).to_be_visible()
    expect(page.locator('button[type="submit"]')).to_be_visible()


@pytest.mark.e2e
def test_login_success(page: Page, flask_server: str):
    """POST /auth/login with valid credentials → redirect to dashboard."""
    page.goto(f"{flask_server}/auth/login")
    page.wait_for_load_state("networkidle")
    page.fill("#username", "admin")
    page.fill("#password", "admin123")
    page.click('button[type="submit"]')
    page.wait_for_load_state("networkidle")

    # Should be on dashboard or index, not login page
    assert "/auth/login" not in page.url, f"Login failed, still on: {page.url}"
    assert page.locator(".sidebar").is_visible(), "Sidebar not visible after login"


@pytest.mark.e2e
def test_login_wrong_password(page: Page, flask_server: str):
    """POST /auth/login with wrong password → stays on login page."""
    page.goto(f"{flask_server}/auth/login")
    page.wait_for_load_state("networkidle")
    page.fill("#username", "admin")
    page.fill("#password", "wrongpassword")
    page.click('button[type="submit"]')
    page.wait_for_load_state("networkidle")

    # Should show error or stay on login
    assert "/auth/login" in page.url or page.locator(".alert").is_visible()


# ========================================================================
# Dashboard Tests
# ========================================================================

@pytest.mark.e2e
def test_dashboard_loads(authenticated_page: Page, flask_server: str):
    """GET / → 200, has sidebar and content area."""
    page = authenticated_page
    response = expect_no_500(page, f"{flask_server}/")
    assert response.status == 200
    expect(page.locator(".sidebar")).to_be_visible()
    expect(page.locator(".content-area")).to_be_visible()


@pytest.mark.e2e
def test_dashboard_has_sidebar_nav(authenticated_page: Page, flask_server: str):
    """Dashboard sidebar has navigation links."""
    page = authenticated_page
    page.goto(f"{flask_server}/")
    page.wait_for_load_state("networkidle")

    # Check key nav items exist in sidebar
    sidebar = page.locator(".sidebar")
    expect(sidebar.locator(".nav-link").first).to_be_visible()
    expect(sidebar.get_by_role("link", name="Dashboard").first).to_be_visible()


# ========================================================================
# Settings Tests
# ========================================================================

@pytest.mark.e2e
def test_settings_index_no_500(authenticated_page: Page, flask_server: str):
    """GET /settings/ → 200, no Internal Server Error."""
    page = authenticated_page
    response = expect_no_500(page, f"{flask_server}/settings/")
    assert response.status == 200


@pytest.mark.e2e
def test_settings_company_no_500(authenticated_page: Page, flask_server: str):
    """GET /settings/company → 200, no Internal Server Error."""
    page = authenticated_page
    response = expect_no_500(page, f"{flask_server}/settings/company")
    assert response.status == 200


@pytest.mark.e2e
def test_settings_accounting_no_500(authenticated_page: Page, flask_server: str):
    """GET /settings/accounting → 200, no Internal Server Error."""
    page = authenticated_page
    response = expect_no_500(page, f"{flask_server}/settings/accounting")
    assert response.status == 200


@pytest.mark.e2e
def test_settings_all_no_500(authenticated_page: Page, flask_server: str):
    """GET /settings/all → 200, no Internal Server Error."""
    page = authenticated_page
    response = expect_no_500(page, f"{flask_server}/settings/all")
    assert response.status == 200


# ========================================================================
# Auth Route Tests
# ========================================================================

@pytest.mark.e2e
def test_users_page_no_500(authenticated_page: Page, flask_server: str):
    """GET /auth/users → 200 (admin only)."""
    page = authenticated_page
    response = expect_no_500(page, f"{flask_server}/auth/users")
    assert response.status == 200


@pytest.mark.e2e
def test_change_password_page_no_500(authenticated_page: Page, flask_server: str):
    """GET /auth/change-password → 200."""
    page = authenticated_page
    response = expect_no_500(page, f"{flask_server}/auth/change-password")
    assert response.status == 200


@pytest.mark.e2e
def test_roles_page_no_500(authenticated_page: Page, flask_server: str):
    """GET /auth/roles → 200 (admin only)."""
    page = authenticated_page
    response = expect_no_500(page, f"{flask_server}/auth/roles")
    assert response.status == 200
