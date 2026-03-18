"""Financial reports tests - Balance Sheet, Income Statement."""
import pytest
from decimal import Decimal
from datetime import date
from models.journal import JournalVoucher
from models.account import Account, AccountType, NormalBalance
from core.security import User
from core.database import db
from repositories.journal_repository import JournalRepository
from services.ledger_service import LedgerService
from services.financial_report_service import BalanceSheetService, IncomeStatementService


def test_balance_sheet_assets_equals_liabilities_plus_equity(app, db_session):
    """Test balance sheet: Assets = Liabilities + Equity."""
    with app.app_context():
        user = User.query.first()
        
        cash = Account.query.filter_by(code="111").first()
        receivable = Account.query.filter_by(code="1311").first()
        payable = Account.query.filter_by(code="332").first()
        revenue = Account.query.filter_by(code="511").first()
        
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
        assert bs["total_assets"] == Decimal("15000000")
        assert bs["total_liab_equity"] == Decimal("15000000")


def test_balance_sheet_with_profit(app, db_session):
    """Test balance sheet reflects profit correctly."""
    with app.app_context():
        user = User.query.first()
        
        cash = Account.query.filter_by(code="111").first()
        payable = Account.query.filter_by(code="332").first()
        revenue = Account.query.filter_by(code="511").first()
        
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
        
        assert bs["total_assets"] == Decimal("10000000")
        assert bs["total_liab_equity"] == Decimal("10000000")


def test_income_statement_revenue_minus_expenses(app, db_session):
    """Test income statement: Profit = Revenue - Expenses."""
    with app.app_context():
        user = User.query.first()
        
        cash = Account.query.filter_by(code="111").first()
        revenue = Account.query.filter_by(code="511").first()
        cogs = Account.query.filter_by(code="627").first()
        expense = Account.query.filter_by(code="635").first()
        
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
        
        assert income_stmt["total_revenue"] == Decimal("10000000")
        assert income_stmt["total_expenses"] == Decimal("5000000")
        assert income_stmt["gross_profit"] == Decimal("5000000")
        assert income_stmt["net_profit_after_tax"] == Decimal("5000000")


def test_income_statement_loss_scenario(app, db_session):
    """Test income statement when expenses exceed revenue."""
    with app.app_context():
        user = User.query.first()
        
        cash = Account.query.filter_by(code="111").first()
        revenue = Account.query.filter_by(code="511").first()
        expense = Account.query.filter_by(code="635").first()
        
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
        
        assert income_stmt["total_revenue"] == Decimal("5000000")
        assert income_stmt["total_expenses"] == Decimal("8000000")
        assert income_stmt["gross_profit"] == Decimal("-3000000")


def test_trial_balance_zero_balance(app, db_session):
    """Test trial balance when no transactions."""
    with app.app_context():
        result = LedgerService.get_trial_balance()
        
        assert result["total_debit"] == Decimal("0")
        assert result["total_credit"] == Decimal("0")
        assert result["is_balanced"] == True


def test_financial_reports_integration(app, db_session):
    """Integration test: full accounting cycle produces correct reports."""
    with app.app_context():
        user = User.query.first()
        
        cash = Account.query.filter_by(code="111").first()
        receivable = Account.query.filter_by(code="1311").first()
        payable = Account.query.filter_by(code="332").first()
        cogs = Account.query.filter_by(code="627").first()
        revenue = Account.query.filter_by(code="511").first()
        
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
        assert income_stmt["gross_profit"] == Decimal("10000000")
        
        bs = BalanceSheetService.get_balance_sheet(date.today())
        assert bs["is_balanced"] == True
