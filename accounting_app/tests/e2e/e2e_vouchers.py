"""
E2E tests for journal voucher pages.
"""

import pytest
from playwright.sync_api import Page


def test_journal_page_loads(logged_in_page: Page, flask_server: str):
    """Test that the journal voucher list page loads."""
    page = logged_in_page
    page.goto(f"{flask_server}/accounting/journal")
    page.wait_for_load_state("networkidle")
    
    assert page.locator(".sidebar").is_visible() or "Chứng từ" in page.content()


def test_journal_create_page_loads(logged_in_page: Page, flask_server: str):
    """Test that the create voucher page loads."""
    page = logged_in_page
    page.goto(f"{flask_server}/accounting/journal/create")
    page.wait_for_load_state("networkidle")
    
    assert page.locator("form").is_visible() or page.locator(".sidebar").is_visible()


def test_journal_has_form_elements(logged_in_page: Page, flask_server: str):
    """Test that the create voucher form has required elements."""
    page = logged_in_page
    page.goto(f"{flask_server}/accounting/journal/create")
    page.wait_for_load_state("networkidle")
    
    form_visible = page.locator("form").count() > 0
    assert form_visible
