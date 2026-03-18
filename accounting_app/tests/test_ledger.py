"""Ledger tests - Account balance and posting validation."""
import pytest
from decimal import Decimal
from datetime import date
from models.journal import JournalVoucher, JournalEntry, VoucherStatus
from models.account import Account, AccountType, NormalBalance
from core.security import User, Role
from core.database import db
from repositories.journal_repository import JournalRepository
from repositories.ledger_repository import LedgerRepository
from services.ledger_service import LedgerService


def test_posting_updates_account_balance(app, db_session):
    """Test that posting voucher updates account balances correctly."""
    with app.app_context():
        user = User.query.first()
        cash = Account.query.filter_by(code="111").first()
        revenue = Account.query.filter_by(code="511").first()
        
        balance_before = LedgerRepository.get_account_balance(cash.id)
        assert balance_before == Decimal("0")
        
        voucher_data = {
            "voucher_date": date.today(),
            "voucher_type": "general",
            "description": "Test posting balance",
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
        
        balance_after = LedgerRepository.get_account_balance(cash.id)
        assert balance_after == Decimal("5000000")


def test_ledger_accumulate_multiple_vouchers(app, db_session):
    """Test ledger accumulates balances from multiple vouchers."""
    with app.app_context():
        user = User.query.first()
        cash = Account.query.filter_by(code="111").first()
        bank = Account.query.filter_by(code="112").first()
        
        for i in range(3):
            voucher_data = {
                "voucher_date": date.today(),
                "voucher_type": "general",
                "description": f"Test voucher {i}",
                "created_by": user.id,
            }
            voucher = JournalRepository.create_voucher(voucher_data)
            
            JournalRepository.add_entry(voucher.id, {
                "account_id": cash.id,
                "line_number": 1,
                "debit": Decimal("1000000"),
                "credit": Decimal("0"),
            })
            JournalRepository.add_entry(voucher.id, {
                "account_id": bank.id,
                "line_number": 2,
                "debit": Decimal("0"),
                "credit": Decimal("1000000"),
            })
            
            JournalRepository.post_voucher(voucher.id, user.id)
        
        cash_balance = LedgerRepository.get_account_balance(cash.id)
        assert cash_balance == Decimal("3000000")


def test_trial_balance_debit_equals_credit(app, db_session):
    """Test trial balance: total debit must equal total credit."""
    with app.app_context():
        user = User.query.first()
        cash = Account.query.filter_by(code="111").first()
        revenue = Account.query.filter_by(code="511").first()
        
        voucher_data = {
            "voucher_date": date.today(),
            "voucher_type": "general",
            "description": "Trial balance test",
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
        
        result = LedgerService.get_trial_balance()
        
        assert result["is_balanced"] == True
        assert result["total_debit"] == result["total_credit"]


def test_trial_balance_with_multiple_vouchers(app, db_session):
    """Test trial balance with multiple balanced vouchers."""
    with app.app_context():
        user = User.query.first()
        cash = Account.query.filter_by(code="111").first()
        bank = Account.query.filter_by(code="112").first()
        revenue = Account.query.filter_by(code="511").first()
        expense = Account.query.filter_by(code="635").first()
        
        for amount in [Decimal("1000000"), Decimal("2000000"), Decimal("3000000")]:
            voucher_data = {
                "voucher_date": date.today(),
                "voucher_type": "general",
                "description": "Multiple vouchers test",
                "created_by": user.id,
            }
            voucher = JournalRepository.create_voucher(voucher_data)
            
            JournalRepository.add_entry(voucher.id, {
                "account_id": cash.id,
                "line_number": 1,
                "debit": amount,
                "credit": Decimal("0"),
            })
            JournalRepository.add_entry(voucher.id, {
                "account_id": revenue.id,
                "line_number": 2,
                "debit": Decimal("0"),
                "credit": amount,
            })
            
            JournalRepository.post_voucher(voucher.id, user.id)
        
        result = LedgerService.get_trial_balance()
        
        assert result["is_balanced"] == True
        assert result["total_debit"] == Decimal("6000000")
        assert result["total_credit"] == Decimal("6000000")


def test_ledger_entry_history_unchanged(app, db_session):
    """Test that historical ledger entries remain unchanged after new entries."""
    with app.app_context():
        user = User.query.first()
        cash = Account.query.filter_by(code="111").first()
        revenue = Account.query.filter_by(code="511").first()
        
        voucher1_data = {
            "voucher_date": date.today(),
            "voucher_type": "general",
            "description": "First voucher",
            "created_by": user.id,
        }
        voucher1 = JournalRepository.create_voucher(voucher1_data)
        
        JournalRepository.add_entry(voucher1.id, {
            "account_id": cash.id,
            "line_number": 1,
            "debit": Decimal("1000000"),
            "credit": Decimal("0"),
        })
        JournalRepository.add_entry(voucher1.id, {
            "account_id": revenue.id,
            "line_number": 2,
            "debit": Decimal("0"),
            "credit": Decimal("1000000"),
        })
        
        JournalRepository.post_voucher(voucher1.id, user.id)
        
        ledger_before = LedgerService.get_ledger(cash.id)
        
        voucher2_data = {
            "voucher_date": date.today(),
            "voucher_type": "general",
            "description": "Second voucher",
            "created_by": user.id,
        }
        voucher2 = JournalRepository.create_voucher(voucher2_data)
        
        JournalRepository.add_entry(voucher2.id, {
            "account_id": cash.id,
            "line_number": 1,
            "debit": Decimal("500000"),
            "credit": Decimal("0"),
        })
        JournalRepository.add_entry(voucher2.id, {
            "account_id": revenue.id,
            "line_number": 2,
            "debit": Decimal("0"),
            "credit": Decimal("500000"),
        })
        
        JournalRepository.post_voucher(voucher2.id, user.id)
        
        ledger_after = LedgerService.get_ledger(cash.id)
        
        assert len(ledger_after["entries"]) > len(ledger_before["entries"])
        assert ledger_after["closing_balance"] == Decimal("1500000")


def test_get_ledger_by_date_range(app, db_session):
    """Test ledger queries by date range."""
    with app.app_context():
        user = User.query.first()
        cash = Account.query.filter_by(code="111").first()
        revenue = Account.query.filter_by(code="511").first()
        
        voucher_data = {
            "voucher_date": date.today(),
            "voucher_type": "general",
            "description": "Date range test",
            "created_by": user.id,
        }
        voucher = JournalRepository.create_voucher(voucher_data)
        
        JournalRepository.add_entry(voucher.id, {
            "account_id": cash.id,
            "line_number": 1,
            "debit": Decimal("2000000"),
            "credit": Decimal("0"),
        })
        JournalRepository.add_entry(voucher.id, {
            "account_id": revenue.id,
            "line_number": 2,
            "debit": Decimal("0"),
            "credit": Decimal("2000000"),
        })
        
        JournalRepository.post_voucher(voucher.id, user.id)
        
        ledger = LedgerService.get_ledger(cash.id, end_date=date.today())
        
        assert ledger["closing_balance"] == Decimal("2000000")
        assert len(ledger["entries"]) > 0
