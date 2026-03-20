"""
Phase 3: Data Entry Form Tests
===============================
Tests for journal voucher creation form.
Uses authenticated_page fixture.

Run: pytest accounting_app/tests/accounting/test_data_entry.py -v
"""

import os
import pytest
from playwright.sync_api import Page, expect


TEST_DIR = os.path.dirname(os.path.abspath(__file__))
SNAP_DIR = os.path.join(TEST_DIR, "..", "e2e", "snapshots")
os.makedirs(SNAP_DIR, exist_ok=True)


# ========================================================================
# Helpers
# ========================================================================

def goto_voucher_form(page: Page, base_url: str):
    """Navigate to the create voucher form."""
    page.goto(f"{base_url}/accounting/journal/create")
    page.wait_for_load_state("networkidle")


def screenshot_on_fail(page: Page, name: str):
    """Save screenshot for debugging."""
    try:
        page.screenshot(path=os.path.join(SNAP_DIR, f"{name}.png"), full_page=True)
    except Exception:
        pass


# ========================================================================
# Form Load Tests
# ========================================================================

@pytest.mark.e2e
def test_voucher_form_loads(authenticated_page: Page, flask_server: str):
    """Voucher create form renders without errors."""
    page = authenticated_page
    goto_voucher_form(page, flask_server)

    body = page.locator("body").text_content()
    assert "Internal Server Error" not in body
    assert "Traceback" not in body

    # Check form elements exist
    expect(page.locator("form#voucherForm")).to_be_visible()
    expect(page.locator("select[name='account_id[]']")).to_be_visible()
    expect(page.locator("input[name='debit[]']")).to_be_visible()
    expect(page.locator("input[name='credit[]']")).to_be_visible()


@pytest.mark.e2e
def test_voucher_form_has_add_entry_button(authenticated_page: Page, flask_server: str):
    """Form has 'Add row' button and it works."""
    page = authenticated_page
    goto_voucher_form(page, flask_server)

    # Initially 1 entry row
    rows = page.locator("#entries-body tr")
    assert rows.count() == 1

    # Click add row
    page.click("button:has-text('Thêm dòng')")

    # Should have 2 rows now
    assert rows.count() == 2


@pytest.mark.e2e
def test_voucher_form_has_remove_entry_button(authenticated_page: Page, flask_server: str):
    """Form has 'Remove row' button and it works."""
    page = authenticated_page
    goto_voucher_form(page, flask_server)

    # Add a second row
    page.click("button:has-text('Thêm dòng')")
    assert page.locator("#entries-body tr").count() == 2

    # Click remove on second row
    page.locator("#entries-body tr").nth(1).locator("button.btn-outline-danger").click()

    # Should be back to 1 row
    assert page.locator("#entries-body tr").count() == 1


@pytest.mark.e2e
def test_voucher_form_has_action_buttons(authenticated_page: Page, flask_server: str):
    """Form has Save and Go Back buttons."""
    page = authenticated_page
    goto_voucher_form(page, flask_server)

    # Check action buttons exist
    expect(page.locator("button[type='submit']").first).to_be_visible()
    expect(page.locator("a:has-text('Hủy')")).to_be_visible()


# ========================================================================
# Balance Check Tests (Client-side JS)
# ========================================================================

@pytest.mark.e2e
def test_balance_shows_initially_as_zero(authenticated_page: Page, flask_server: str):
    """Balance totals start at 0 with 'Chưa cân' status."""
    page = authenticated_page
    goto_voucher_form(page, flask_server)

    total_debit = page.locator("#total-debit").text_content()
    total_credit = page.locator("#total-credit").text_content()
    status = page.locator("#balance-status").text_content()

    assert "0" in total_debit
    assert "0" in total_credit
    assert "Chưa" in status


@pytest.mark.e2e
def test_balance_updates_on_debit_input(authenticated_page: Page, flask_server: str):
    """Entering a debit amount updates the total."""
    page = authenticated_page
    goto_voucher_form(page, flask_server)

    # Enter 1000000 in debit
    page.fill("input[name='debit[]']", "1000000")

    # Trigger input event (JS listens on input)
    page.locator("input[name='debit[]']").dispatch_event("input")

    total_debit = page.locator("#total-debit").text_content()
    assert "1.000.000" in total_debit or "1000000" in total_debit


@pytest.mark.e2e
def test_balance_shows_balanced_status(authenticated_page: Page, flask_server: str):
    """Equal debit and credit shows 'Đã cân' status."""
    page = authenticated_page
    goto_voucher_form(page, flask_server)

    # Enter equal debit and credit
    page.fill("input[name='debit[]']", "500000")
    page.locator("input[name='debit[]']").dispatch_event("input")
    page.fill("input[name='credit[]']", "500000")
    page.locator("input[name='credit[]']").dispatch_event("input")

    status = page.locator("#balance-status").text_content()
    assert "Đã cân" in status


@pytest.mark.e2e
def test_balance_shows_unbalanced_status(authenticated_page: Page, flask_server: str):
    """Unequal debit and credit shows 'Chưa cân' status."""
    page = authenticated_page
    goto_voucher_form(page, flask_server)

    # Enter unequal amounts
    page.fill("input[name='debit[]']", "500000")
    page.locator("input[name='debit[]']").dispatch_event("input")
    page.fill("input[name='credit[]']", "300000")
    page.locator("input[name='credit[]']").dispatch_event("input")

    status = page.locator("#balance-status").text_content()
    assert "Chưa cân" in status


@pytest.mark.e2e
def test_balance_removes_row_updates_total(authenticated_page: Page, flask_server: str):
    """Removing a row recalculates totals."""
    page = authenticated_page
    goto_voucher_form(page, flask_server)

    # Add second row with values
    page.click("button:has-text('Thêm dòng')")
    page.locator("#entries-body tr").nth(1).locator("input[name='debit[]']").fill("200000")
    page.locator("#entries-body tr").nth(1).locator("input[name='debit[]']").dispatch_event("input")

    total_debit = page.locator("#total-debit").text_content()
    assert "200.000" in total_debit or "200000" in total_debit

    # Remove second row
    page.locator("#entries-body tr").nth(1).locator("button.btn-outline-danger").click()

    total_debit = page.locator("#total-debit").text_content()
    assert "200.000" not in total_debit and "200000" not in total_debit


# ========================================================================
# Form Submission Tests
# ========================================================================

@pytest.mark.e2e
def test_voucher_submit_shows_flash(authenticated_page: Page, flask_server: str):
    """Submitting voucher form shows result (success or validation error)."""
    page = authenticated_page
    goto_voucher_form(page, flask_server)

    # Fill basic fields
    page.fill("input[name='description']", "Test voucher E2E")
    page.select_option("select[name='account_id[]']", index=1)  # first account
    page.fill("input[name='debit[]']", "100000")
    page.locator("input[name='debit[]']").dispatch_event("input")
    page.fill("input[name='credit[]']", "100000")
    page.locator("input[name='credit[]']").dispatch_event("input")

    # Submit
    page.locator("button[type='submit']").first.click()
    page.wait_for_load_state("networkidle")

    body = page.locator("body").text_content()
    # Either success flash, validation error, or redirect back to journal
    assert "Internal Server Error" not in body, "500 on voucher submit"
