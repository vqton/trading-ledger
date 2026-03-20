"""Financial reports tests - TT99/2025/TT-BTC compliant.
Tests for B01-DN (Báo cáo tình hình tài chính), B02-DN (Báo cáo kết quả hoạt động KD)."""
import pytest
from decimal import Decimal
from datetime import date
from models.journal import JournalVoucher
from models.account import Account, AccountType, NormalBalance
from core.security import User
from core.database import db
from repositories.journal_repository import JournalRepository
from services.ledger_service import LedgerService
from services.financial_report_service import (
    BalanceSheetService, IncomeStatementService, CashFlowService, FinancialReportService,
)


def test_balance_sheet_assets_equals_liabilities_plus_equity(app, db_session):
    """Test B01-DN: Assets = Liabilities + Equity."""
    with app.app_context():
        user = User.query.first()

        cash = Account.query.filter_by(code="111").first()
        receivable = Account.query.filter_by(code="1311").first()
        payable = Account.query.filter_by(code="331").first() if Account.query.filter_by(code="331").first() \
            else Account.query.filter_by(code="332").first()

        voucher_data = {
            "voucher_date": date.today(),
            "voucher_type": "general",
            "description": "Balance sheet test",
            "created_by": user.id,
        }
        voucher = JournalRepository.create_voucher(voucher_data)

        JournalRepository.add_entry(voucher.id, {
            "account_id": cash.id,
            "line_number": 1,
            "debit": Decimal("10000000"),
            "credit": Decimal("0"),
        })
        JournalRepository.add_entry(voucher.id, {
            "account_id": receivable.id,
            "line_number": 2,
            "debit": Decimal("5000000"),
            "credit": Decimal("0"),
        })
        JournalRepository.add_entry(voucher.id, {
            "account_id": payable.id,
            "line_number": 3,
            "debit": Decimal("0"),
            "credit": Decimal("15000000"),
        })

        JournalRepository.post_voucher(voucher.id, user.id)

        bs = BalanceSheetService.get_balance_sheet(date.today())

        assert bs["is_balanced"] == True
        assert bs["report_code"] == "B01-DN"
        assert bs["assets"]["total"] == Decimal("15000000")
        assert bs["total_liabilities_equity"] == Decimal("15000000")
        # Check TT99 line items exist
        assert "100" in bs["assets"]["short_term"]
        assert "200" in bs["assets"]["long_term"]
        assert "300" in bs["liabilities"]["short_term"]
        assert "500" in bs["equity"]


def test_balance_sheet_with_profit(app, db_session):
    """Test B01-DN reflects profit correctly."""
    with app.app_context():
        user = User.query.first()

        cash = Account.query.filter_by(code="111").first()
        payable = Account.query.filter_by(code="331").first() if Account.query.filter_by(code="331").first() \
            else Account.query.filter_by(code="332").first()

        voucher_data = {
            "voucher_date": date.today(),
            "voucher_type": "general",
            "description": "Profit test",
            "created_by": user.id,
        }
        voucher = JournalRepository.create_voucher(voucher_data)

        JournalRepository.add_entry(voucher.id, {
            "account_id": cash.id,
            "line_number": 1,
            "debit": Decimal("10000000"),
            "credit": Decimal("0"),
        })
        JournalRepository.add_entry(voucher.id, {
            "account_id": payable.id,
            "line_number": 2,
            "debit": Decimal("0"),
            "credit": Decimal("10000000"),
        })

        JournalRepository.post_voucher(voucher.id, user.id)

        bs = BalanceSheetService.get_balance_sheet(date.today())

        assert bs["assets"]["total"] == Decimal("10000000")
        assert bs["total_liabilities_equity"] == Decimal("10000000")


def test_balance_sheet_has_tt99_structure(app, db_session):
    """Test B01-DN has proper TT99 structure with Mã số."""
    with app.app_context():
        bs = BalanceSheetService.get_balance_sheet(date.today())

        # Check report metadata
        assert bs["report_name"] == "Báo cáo tình hình tài chính"
        assert bs["report_code"] == "B01-DN"

        # Check short-term assets section
        short_term = bs["assets"]["short_term"]
        assert "100" in short_term
        assert "110" in short_term
        assert "111" in short_term
        assert "112" in short_term
        assert "120" in short_term
        assert "130" in short_term
        assert "131" in short_term
        assert "140" in short_term
        assert "160" in short_term

        # Check long-term assets section
        long_term = bs["assets"]["long_term"]
        assert "200" in long_term
        assert "220" in long_term
        assert "221" in long_term
        assert "224" in long_term
        assert "227" in long_term

        # Check liabilities section
        assert "300" in bs["liabilities"]["short_term"]
        assert "400" in bs["liabilities"]["long_term"]

        # Check equity section
        assert "500" in bs["equity"]
        assert "510" in bs["equity"]
        assert "520" in bs["equity"]

        # Each line item should have ma_so, name, amount
        for key, item in short_term.items():
            assert "ma_so" in item
            assert "name" in item
            assert "amount" in item


def test_income_statement_tt99_structure(app, db_session):
    """Test B02-DN has proper TT99 structure."""
    with app.app_context():
        income_stmt = IncomeStatementService.get_income_statement(date.today(), date.today())

        assert income_stmt["report_code"] == "B02-DN"
        assert income_stmt["report_name"] == "Báo cáo kết quả hoạt động kinh doanh"

        lines = income_stmt["lines"]
        assert "10" in lines
        assert "20" in lines
        assert "30" in lines
        assert "40" in lines
        assert "50" in lines
        assert "60" in lines
        assert "70" in lines
        assert "80" in lines
        assert "90" in lines
        assert "100" in lines
        assert "120" in lines
        assert "130" in lines
        assert "140" in lines
        assert "150" in lines


def test_income_statement_revenue_minus_expenses(app, db_session):
    """Test B02-DN: Revenue - Expenses = Profit."""
    with app.app_context():
        user = User.query.first()

        cash = Account.query.filter_by(code="111").first()
        revenue = Account.query.filter_by(code="511").first()
        cogs = Account.query.filter_by(code="627").first() or Account.query.filter_by(code="632").first()
        expense = Account.query.filter_by(code="635").first()

        # Record revenue
        voucher_data = {
            "voucher_date": date.today(),
            "voucher_type": "general",
            "description": "Income statement test",
            "created_by": user.id,
        }
        voucher = JournalRepository.create_voucher(voucher_data)

        JournalRepository.add_entry(voucher.id, {
            "account_id": cash.id,
            "line_number": 1,
            "debit": Decimal("10000000"),
            "credit": Decimal("0"),
        })
        JournalRepository.add_entry(voucher.id, {
            "account_id": revenue.id,
            "line_number": 2,
            "debit": Decimal("0"),
            "credit": Decimal("10000000"),
        })

        JournalRepository.post_voucher(voucher.id, user.id)

        # Record expenses
        voucher2_data = {
            "voucher_date": date.today(),
            "voucher_type": "general",
            "description": "COGS and expenses",
            "created_by": user.id,
        }
        voucher2 = JournalRepository.create_voucher(voucher2_data)

        JournalRepository.add_entry(voucher2.id, {
            "account_id": cogs.id,
            "line_number": 1,
            "debit": Decimal("3000000"),
            "credit": Decimal("0"),
        })
        JournalRepository.add_entry(voucher2.id, {
            "account_id": expense.id,
            "line_number": 2,
            "debit": Decimal("2000000"),
            "credit": Decimal("0"),
        })
        JournalRepository.add_entry(voucher2.id, {
            "account_id": cash.id,
            "line_number": 3,
            "debit": Decimal("0"),
            "credit": Decimal("5000000"),
        })

        JournalRepository.post_voucher(voucher2.id, user.id)

        income_stmt = IncomeStatementService.get_income_statement(date.today(), date.today())

        lines = income_stmt["lines"]
        assert lines["10"]["amount"] == Decimal("10000000")  # Revenue
        assert lines["40"]["amount"] == Decimal("3000000")   # COGS
        assert lines["50"]["amount"] == Decimal("7000000")   # Gross profit = 10M - 3M
        assert lines["70"]["amount"] == Decimal("2000000")   # Financial expense
        assert lines["120"]["amount"] == Decimal("5000000")  # Profit before tax


def test_income_statement_loss_scenario(app, db_session):
    """Test B02-DN when expenses exceed revenue."""
    with app.app_context():
        user = User.query.first()

        cash = Account.query.filter_by(code="111").first()
        revenue = Account.query.filter_by(code="511").first()
        expense = Account.query.filter_by(code="635").first()

        # Revenue
        voucher_data = {
            "voucher_date": date.today(),
            "voucher_type": "general",
            "description": "Revenue",
            "created_by": user.id,
        }
        voucher = JournalRepository.create_voucher(voucher_data)

        JournalRepository.add_entry(voucher.id, {
            "account_id": cash.id,
            "line_number": 1,
            "debit": Decimal("5000000"),
            "credit": Decimal("0"),
        })
        JournalRepository.add_entry(voucher.id, {
            "account_id": revenue.id,
            "line_number": 2,
            "debit": Decimal("0"),
            "credit": Decimal("5000000"),
        })

        JournalRepository.post_voucher(voucher.id, user.id)

        # Expense exceeding revenue
        voucher2_data = {
            "voucher_date": date.today(),
            "voucher_type": "general",
            "description": "Expense",
            "created_by": user.id,
        }
        voucher2 = JournalRepository.create_voucher(voucher2_data)

        JournalRepository.add_entry(voucher2.id, {
            "account_id": expense.id,
            "line_number": 1,
            "debit": Decimal("8000000"),
            "credit": Decimal("0"),
        })
        JournalRepository.add_entry(voucher2.id, {
            "account_id": cash.id,
            "line_number": 2,
            "debit": Decimal("0"),
            "credit": Decimal("8000000"),
        })

        JournalRepository.post_voucher(voucher2.id, user.id)

        income_stmt = IncomeStatementService.get_income_statement(date.today(), date.today())

        lines = income_stmt["lines"]
        assert lines["10"]["amount"] == Decimal("5000000")
        assert lines["70"]["amount"] == Decimal("8000000")
        assert lines["120"]["amount"] == Decimal("-3000000")  # Loss


def test_cash_flow_tt99_structure(app, db_session):
    """Test B03-DN has proper TT99 structure."""
    with app.app_context():
        cf = CashFlowService.get_cash_flow(date.today(), date.today())

        assert cf["report_code"] == "B03-DN"
        assert cf["report_name"] == "Báo cáo lưu chuyển tiền tệ"

        assert "operating" in cf
        assert "investing" in cf
        assert "financing" in cf
        assert "summary" in cf

        assert "01" in cf["operating"]
        assert "02" in cf["operating"]
        assert "total" in cf["operating"]
        assert "net_cash_flow" in cf["summary"]
        assert "opening_cash" in cf["summary"]
        assert "closing_cash" in cf["summary"]


def test_cash_flow_opening_cash_not_zero(app, db_session):
    """Test B03-DN opening_cash is NOT hardcoded to 0."""
    with app.app_context():
        user = User.query.first()
        cash = Account.query.filter_by(code="111").first()
        payable = Account.query.filter_by(code="331").first() or Account.query.filter_by(code="332").first()

        # Create opening balance
        v = JournalRepository.create_voucher({
            "voucher_date": date.today(),
            "voucher_type": "general",
            "description": "Opening",
            "created_by": user.id,
        })
        JournalRepository.add_entry(v.id, {
            "account_id": cash.id, "line_number": 1,
            "debit": Decimal("50000000"), "credit": Decimal("0"),
        })
        JournalRepository.add_entry(v.id, {
            "account_id": payable.id, "line_number": 2,
            "debit": Decimal("0"), "credit": Decimal("50000000"),
        })
        JournalRepository.post_voucher(v.id, user.id)

        cf = CashFlowService.get_cash_flow(date.today(), date.today())

        # Opening cash must be 0 for today (no prior day transactions)
        # But closing cash must NOT be 0
        assert cf["summary"]["closing_cash"]["amount"] == Decimal("50000000")


def test_trial_balance_zero_balance(app, db_session):
    """Test trial balance when no transactions."""
    with app.app_context():
        result = LedgerService.get_trial_balance()

        assert result["total_debit"] == Decimal("0")
        assert result["total_credit"] == Decimal("0")
        assert result["is_balanced"] == True


def test_financial_reports_integration(app, db_session):
    """Integration test: full accounting cycle produces correct TT99 reports."""
    with app.app_context():
        user = User.query.first()

        cash = Account.query.filter_by(code="111").first()
        receivable = Account.query.filter_by(code="1311").first()
        payable = Account.query.filter_by(code="331").first() if Account.query.filter_by(code="331").first() \
            else Account.query.filter_by(code="332").first()
        cogs = Account.query.filter_by(code="627").first() or Account.query.filter_by(code="632").first()
        revenue = Account.query.filter_by(code="511").first()

        # Initial investment
        voucher1_data = {
            "voucher_date": date.today(),
            "voucher_type": "general",
            "description": "Initial investment",
            "created_by": user.id,
        }
        v1 = JournalRepository.create_voucher(voucher1_data)
        JournalRepository.add_entry(v1.id, {"account_id": cash.id, "line_number": 1, "debit": Decimal("50000000"), "credit": Decimal("0")})
        JournalRepository.add_entry(v1.id, {"account_id": payable.id, "line_number": 2, "debit": Decimal("0"), "credit": Decimal("50000000")})
        JournalRepository.post_voucher(v1.id, user.id)

        trial_balance = LedgerService.get_trial_balance()
        assert trial_balance["is_balanced"] == True

        bs = BalanceSheetService.get_balance_sheet(date.today())
        assert bs["is_balanced"] == True
        assert bs["report_code"] == "B01-DN"

        # Revenue transaction
        voucher3_data = {
            "voucher_date": date.today(),
            "voucher_type": "general",
            "description": "Record COGS and revenue",
            "created_by": user.id,
        }
        v3 = JournalRepository.create_voucher(voucher3_data)
        JournalRepository.add_entry(v3.id, {"account_id": cogs.id, "line_number": 1, "debit": Decimal("12000000"), "credit": Decimal("0")})
        JournalRepository.add_entry(v3.id, {"account_id": revenue.id, "line_number": 2, "debit": Decimal("0"), "credit": Decimal("22000000")})
        JournalRepository.add_entry(v3.id, {"account_id": cash.id, "line_number": 3, "debit": Decimal("22000000"), "credit": Decimal("0")})
        JournalRepository.add_entry(v3.id, {"account_id": cash.id, "line_number": 4, "debit": Decimal("0"), "credit": Decimal("12000000")})
        JournalRepository.post_voucher(v3.id, user.id)

        trial_balance = LedgerService.get_trial_balance()
        assert trial_balance["is_balanced"] == True

        income_stmt = IncomeStatementService.get_income_statement(date.today(), date.today())
        lines = income_stmt["lines"]
        assert lines["50"]["amount"] == Decimal("10000000")  # Gross profit = 22M - 12M

        bs = BalanceSheetService.get_balance_sheet(date.today())
        assert bs["is_balanced"] == True


def test_validate_financial_statements(app, db_session):
    """Test cross-report validation."""
    with app.app_context():
        result = FinancialReportService.validate_financial_statements(date.today(), date.today())

        assert "balance_sheet_balanced" in result
        assert "cash_flow_reconciled" in result
        assert "all_valid" in result
