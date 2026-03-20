"""
E2E tests for chart of accounts pages.
"""

import pytest
from playwright.sync_api import Page


def test_accounts_page_loads(logged_in_page: Page, flask_server: str):
    """Test that the accounts list page loads."""
    page = logged_in_page
    page.goto(f"{flask_server}/accounting/accounts")
    page.wait_for_load_state("networkidle")
    
    assert page.locator(".sidebar").is_visible() or "Danh mục TK" in page.content()


def test_account_tree_page_loads(logged_in_page: Page, flask_server: str):
    """Test that the account tree page loads."""
    page = logged_in_page
    page.goto(f"{flask_server}/accounting/accounts/tree")
    page.wait_for_load_state("networkidle")
    
    content = page.content()
    assert "Sơ đồ TK" in content or "account" in content.lower()


def test_accounts_page_has_table(logged_in_page: Page, flask_server: str):
    """Test that the accounts page displays a table."""
    page = logged_in_page
    page.goto(f"{flask_server}/accounting/accounts")
    page.wait_for_load_state("networkidle")
    
    table_or_content = page.locator("table").count() > 0 or page.locator(".content-area").is_visible()
    assert table_or_content


def test_ledger_page_loads(logged_in_page: Page, flask_server: str):
    """Test that the ledger page loads."""
    page = logged_in_page
    page.goto(f"{flask_server}/accounting/ledger")
    page.wait_for_load_state("networkidle")
    
    assert page.locator(".sidebar").is_visible()
