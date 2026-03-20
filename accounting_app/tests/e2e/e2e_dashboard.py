"""
E2E tests for dashboard page.
"""

import pytest
from playwright.sync_api import Page


def test_dashboard_loads(logged_in_page: Page, flask_server: str):
    """Test that the dashboard loads after login."""
    page = logged_in_page
    page.wait_for_load_state("networkidle")
    content = page.content()
    assert page.url.endswith("/") or "Dashboard" in content or page.locator(".sidebar").is_visible()


def test_dashboard_sidebar_visible(logged_in_page: Page):
    """Test that the sidebar navigation is visible."""
    page = logged_in_page
    page.wait_for_load_state("networkidle")
    assert page.locator(".sidebar").is_visible()
    assert page.locator("text=Dashboard").is_visible()


def test_dashboard_user_info_visible(logged_in_page: Page):
    """Test that user info is displayed in the top bar."""
    page = logged_in_page
    page.wait_for_load_state("networkidle")
    assert page.locator(".user-info").is_visible()
    assert page.locator(".user-info span").is_visible()
