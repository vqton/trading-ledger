"""
E2E tests for authentication flows.
"""

import pytest
from playwright.sync_api import Page, expect


def test_login_page_loads(page: Page, flask_server: str):
    """Test that the login page loads without errors."""
    page.goto(f"{flask_server}/auth/login")
    page.wait_for_load_state("networkidle")
    
    assert page.title() == "Đăng nhập - VAS Accounting"
    assert page.locator("#username").is_visible()
    assert page.locator("#password").is_visible()
    assert page.locator('button[type="submit"]').is_visible()


def test_successful_login(page: Page, flask_server: str):
    """Test successful login with valid credentials."""
    page.goto(f"{flask_server}/auth/login")
    page.wait_for_load_state("networkidle")
    page.fill("#username", "admin")
    page.fill("#password", "admin123")
    page.click('button[type="submit"]')
    page.wait_for_load_state("networkidle")
    
    assert "Dashboard" in page.content() or page.url != f"{flask_server}/auth/login"


def test_failed_login(page: Page, flask_server: str):
    """Test login with invalid credentials."""
    page.goto(f"{flask_server}/auth/login")
    page.wait_for_load_state("networkidle")
    page.fill("#username", "admin")
    page.fill("#password", "wrongpassword")
    page.click('button[type="submit"]')
    page.wait_for_load_state("networkidle")
    
    assert page.locator(".alert-danger, .alert-warning").is_visible() or page.url == f"{flask_server}/auth/login"


def test_logout(page: Page, logged_in_page: Page, flask_server: str):
    """Test logout functionality."""
    page.click("a:has-text('Đăng xuất'), a:has-text('Logout'), a[href*='logout']")
    page.wait_for_load_state("networkidle")
    
    assert page.locator("#username").is_visible() or page.url == f"{flask_server}/auth/login"


def test_authenticated_redirect(page: Page, flask_server: str):
    """Test that authenticated users are redirected away from login page."""
    page.goto(f"{flask_server}/auth/login")
    page.wait_for_load_state("networkidle")
    page.fill("#username", "admin")
    page.fill("#password", "admin123")
    page.click('button[type="submit"]')
    page.wait_for_load_state("networkidle")
    
    page.goto(f"{flask_server}/auth/login")
    page.wait_for_load_state("networkidle")
    assert page.url != f"{flask_server}/auth/login"
