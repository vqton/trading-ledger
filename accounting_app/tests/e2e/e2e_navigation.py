"""
E2E tests for navigation across all pages.
"""

import pytest
from playwright.sync_api import Page


def test_navigate_to_accounts_from_sidebar(logged_in_page: Page, flask_server: str):
    """Test navigation to accounts from sidebar."""
    page = logged_in_page
    page.goto(f"{flask_server}/")
    page.wait_for_load_state("networkidle")
    
    page.click("a:has-text('Danh mục TK')")
    page.wait_for_load_state("networkidle")
    assert "/accounting/accounts" in page.url


def test_navigate_to_journal_from_sidebar(logged_in_page: Page, flask_server: str):
    """Test navigation to journal from sidebar."""
    page = logged_in_page
    page.goto(f"{flask_server}/")
    page.wait_for_load_state("networkidle")
    
    page.click("a:has-text('Chứng từ')")
    page.wait_for_load_state("networkidle")
    assert "/accounting/journal" in page.url


def test_navigate_to_account_tree_from_sidebar(logged_in_page: Page, flask_server: str):
    """Test navigation to account tree from sidebar."""
    page = logged_in_page
    page.goto(f"{flask_server}/")
    page.wait_for_load_state("networkidle")
    
    page.click("a:has-text('Sơ đồ TK')")
    page.wait_for_load_state("networkidle")
    assert "/accounting/accounts/tree" in page.url


def test_navigate_to_balance_sheet_from_sidebar(logged_in_page: Page, flask_server: str):
    """Test navigation to balance sheet from sidebar."""
    page = logged_in_page
    page.goto(f"{flask_server}/")
    page.wait_for_load_state("networkidle")
    
    page.click("a:has-text('Bảng cân đối')")
    page.wait_for_load_state("networkidle")
    assert "/financial/balance-sheet" in page.url


def test_navigate_to_income_statement_from_sidebar(logged_in_page: Page, flask_server: str):
    """Test navigation to income statement from sidebar."""
    page = logged_in_page
    page.goto(f"{flask_server}/")
    page.wait_for_load_state("networkidle")
    
    page.click("a:has-text('Báo cáo KQKD')")
    page.wait_for_load_state("networkidle")
    assert "/financial/income-statement" in page.url


def test_navigate_to_trial_balance_from_sidebar(logged_in_page: Page, flask_server: str):
    """Test navigation to trial balance from sidebar."""
    page = logged_in_page
    page.goto(f"{flask_server}/")
    page.wait_for_load_state("networkidle")
    
    page.click("a:has-text('Số dư TK')")
    page.wait_for_load_state("networkidle")
    assert "/financial/trial-balance" in page.url


def test_navigate_to_ledger_from_sidebar(logged_in_page: Page, flask_server: str):
    """Test navigation to ledger from sidebar."""
    page = logged_in_page
    page.goto(f"{flask_server}/")
    page.wait_for_load_state("networkidle")
    
    page.click("a:has-text('Sổ cái')")
    page.wait_for_load_state("networkidle")
    assert "/accounting/ledger" in page.url


def test_navigate_to_tax_report_from_sidebar(logged_in_page: Page, flask_server: str):
    """Test navigation to tax report from sidebar."""
    page = logged_in_page
    page.goto(f"{flask_server}/")
    page.wait_for_load_state("networkidle")
    
    page.click("a:has-text('Báo cáo thuế')")
    page.wait_for_load_state("networkidle")
    assert "/accounting/reports/tax" in page.url


def test_navigate_to_users_from_sidebar(logged_in_page: Page, flask_server: str):
    """Test navigation to users page from sidebar (admin only)."""
    page = logged_in_page
    page.goto(f"{flask_server}/")
    page.wait_for_load_state("networkidle")
    
    if page.locator("a:has-text('Người dùng')").count() > 0:
        page.click("a:has-text('Người dùng')")
        page.wait_for_load_state("networkidle")
        assert "/auth/users" in page.url


def test_navigate_to_settings_from_sidebar(logged_in_page: Page, flask_server: str):
    """Test navigation to settings page from sidebar (admin only)."""
    page = logged_in_page
    page.goto(f"{flask_server}/")
    page.wait_for_load_state("networkidle")
    
    if page.locator("a:has-text('Cài đặt')").count() > 0:
        page.click("a:has-text('Cài đặt')")
        page.wait_for_load_state("networkidle")
        assert "/settings" in page.url
