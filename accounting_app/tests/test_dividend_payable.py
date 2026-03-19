"""
Tests for Dividend Payable Service - TK 332 dividend management.
Circular 99/2025/TT-BTC compliant tests.
"""

import pytest
from datetime import date
from decimal import Decimal

from app import create_app
from core.database import db
from services.dividend_payable_service import DividendPayableService
from models.dividend_payable import (
    DividendPayable,
    ShareholderType,
    DividendPaymentStatus,
)


@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


class TestDividendPayable:
    """Tests for dividend payable management."""

    def test_create_dividend_individual(self, app):
        """Test creating dividend for individual shareholder."""
        with app.app_context():
            success, result = DividendPayableService.create_dividend(
                shareholder_name="Nguyen Van A",
                shareholder_type=ShareholderType.INDIVIDUAL,
                share_quantity=Decimal("1000"),
                dividend_per_share=Decimal("10000"),
                declaration_date=date.today(),
                due_date=date(2026, 6, 30),
                created_by=1,
            )

            assert success is True
            assert result["shareholder_name"] == "Nguyen Van A"
            assert result["total_amount"] == 10000000
            assert result["withholding_tax"] == 500000
            assert result["net_amount"] == 9500000
            assert result["status"] == DividendPaymentStatus.PENDING

    def test_create_dividend_corporate(self, app):
        """Test creating dividend for corporate shareholder."""
        with app.app_context():
            success, result = DividendPayableService.create_dividend(
                shareholder_name="ABC Corp",
                shareholder_type=ShareholderType.CORPORATE,
                share_quantity=Decimal("10000"),
                dividend_per_share=Decimal("5000"),
                declaration_date=date.today(),
                created_by=1,
            )

            assert success is True
            assert result["shareholder_type"] == ShareholderType.CORPORATE
            assert result["total_amount"] == 50000000

    def test_record_payment(self, app):
        """Test recording dividend payment."""
        with app.app_context():
            success, dividend = DividendPayableService.create_dividend(
                shareholder_name="Test Shareholder",
                shareholder_type=ShareholderType.INDIVIDUAL,
                share_quantity=Decimal("500"),
                dividend_per_share=Decimal("20000"),
                declaration_date=date.today(),
                created_by=1,
            )

            success, result = DividendPayableService.record_payment(
                dividend_id=dividend["id"],
                payment_date=date.today(),
                payment_method="bank_transfer",
                bank_account="123456789",
            )

            assert success is True
            assert result["status"] == DividendPaymentStatus.PAID
            assert result["payment_method"] == "bank_transfer"

    def test_cancel_dividend(self, app):
        """Test cancelling dividend obligation."""
        with app.app_context():
            success, dividend = DividendPayableService.create_dividend(
                shareholder_name="Cancelled Shareholder",
                shareholder_type=ShareholderType.INDIVIDUAL,
                share_quantity=Decimal("100"),
                dividend_per_share=Decimal("5000"),
                declaration_date=date.today(),
                created_by=1,
            )

            success, result = DividendPayableService.cancel_dividend(
                dividend_id=dividend["id"],
                reason="Shareholder request",
            )

            assert success is True
            assert result["status"] == DividendPaymentStatus.CANCELLED


class TestDividendQueries:
    """Tests for dividend queries."""

    def test_get_dividends_by_status(self, app):
        """Test getting dividends by status."""
        with app.app_context():
            DividendPayableService.create_dividend(
                shareholder_name="Pending Shareholder",
                shareholder_type=ShareholderType.INDIVIDUAL,
                share_quantity=Decimal("100"),
                dividend_per_share=Decimal("1000"),
                declaration_date=date.today(),
                created_by=1,
            )

            dividends = DividendPayableService.get_dividends(
                status=DividendPaymentStatus.PENDING
            )

            assert len(dividends) >= 1
            for div in dividends:
                assert div["status"] == DividendPaymentStatus.PENDING

    def test_get_outstanding_dividends(self, app):
        """Test getting outstanding dividend totals."""
        with app.app_context():
            DividendPayableService.create_dividend(
                shareholder_name="Outstanding 1",
                shareholder_type=ShareholderType.INDIVIDUAL,
                share_quantity=Decimal("200"),
                dividend_per_share=Decimal("5000"),
                declaration_date=date.today(),
                created_by=1,
            )

            outstanding = DividendPayableService.get_outstanding_dividends()

            assert "pending_count" in outstanding
            assert "pending_amount" in outstanding
            assert "total_outstanding" in outstanding

    def test_get_dividend_summary(self, app):
        """Test getting dividend summary by fiscal year."""
        with app.app_context():
            DividendPayableService.create_dividend(
                shareholder_name="Summary Test",
                shareholder_type=ShareholderType.INDIVIDUAL,
                share_quantity=Decimal("500"),
                dividend_per_share=Decimal("10000"),
                declaration_date=date(2026, 3, 15),
                created_by=1,
            )

            summary = DividendPayableService.get_dividend_summary(2026)

            assert summary["fiscal_year"] == 2026
            assert summary["total_dividends"] >= 1
            assert summary["total_gross_amount"] == 5000000


class TestDividendWHT:
    """Tests for withholding tax calculation."""

    def test_wht_rate_is_five_percent(self, app):
        """Test that WHT rate is 5%."""
        with app.app_context():
            success, result = DividendPayableService.create_dividend(
                shareholder_name="WHT Test",
                shareholder_type=ShareholderType.INDIVIDUAL,
                share_quantity=Decimal("100"),
                dividend_per_share=Decimal("10000"),
                declaration_date=date.today(),
                created_by=1,
            )

            gross = Decimal(str(result["total_amount"]))
            wht = result["withholding_tax"]

            expected_wht = gross * Decimal("0.05")
            assert wht == float(expected_wht)
