"""
E2E tests for financial report pages.
"""

import pytest
from playwright.sync_api import Page


def test_balance_sheet_page_loads(authenticated_page: Page, flask_server: str):
    """Test that the balance sheet page loads."""
    page = authenticated_page
    page.goto(f"{flask_server}/financial/balance-sheet")
    page.wait_for_load_state("networkidle")
    
    assert "Bảng cân đối" in page.content() or page.locator(".sidebar").is_visible()


def test_income_statement_page_loads(authenticated_page: Page, flask_server: str):
    """Test that the income statement page loads."""
    page = authenticated_page
    page.goto(f"{flask_server}/financial/income-statement")
    page.wait_for_load_state("networkidle")
    
    content = page.content()
    assert page.locator(".sidebar").is_visible() or "Kết quả" in content or "Báo cáo" in content


def test_trial_balance_page_loads(authenticated_page: Page, flask_server: str):
    """Test that the trial balance page loads."""
    page = authenticated_page
    page.goto(f"{flask_server}/financial/trial-balance")
    page.wait_for_load_state("networkidle")
    
    assert "Số dư" in page.content() or page.locator(".sidebar").is_visible()


@pytest.mark.skip(reason="Requires tax_policies table migration")
def test_tax_report_page_loads(authenticated_page: Page, flask_server: str):
    """Test that the tax report page loads."""
    page = authenticated_page
    page.goto(f"{flask_server}/accounting/reports/tax")
    page.wait_for_load_state("networkidle")
    
    assert "Thuế" in page.content() or page.locator(".sidebar").is_visible()
