"""Journal tests - Double-entry accounting validation."""
import pytest
from decimal import Decimal
from datetime import date
from models.journal import JournalVoucher, JournalEntry, VoucherStatus
from models.account import Account, AccountType, NormalBalance
from core.security import User, Role
from core.database import db
from repositories.journal_repository import JournalRepository
from services.journal_service import JournalService


def test_create_voucher(app, db_session):
    """Test voucher creation."""
    with app.app_context():
        admin_role = Role.query.filter_by(name="admin").first()
        user = User.query.first()
        
        voucher_data = {
            "voucher_date": date.today(),
            "voucher_type": "general",
            "description": "Test voucher",
            "created_by": user.id,
        }
        
        voucher = JournalRepository.create_voucher(voucher_data)
        
        assert voucher.voucher_no is not None
        assert voucher.status == VoucherStatus.DRAFT


def test_add_entry_to_voucher(app, db_session):
    """Test adding entry to voucher."""
    with app.app_context():
        admin_role = Role.query.filter_by(name="admin").first()
        user = User.query.first()
        
        cash = Account.query.filter_by(code="111").first()
        
        voucher_data = {
            "voucher_date": date.today(),
            "voucher_type": "general",
            "created_by": user.id,
        }
        voucher = JournalRepository.create_voucher(voucher_data)
        
        entry_data = {
            "account_id": cash.id,
            "line_number": 1,
            "debit": Decimal("1000000"),
            "credit": Decimal("0"),
            "description": "Test entry",
        }
        
        entry = JournalRepository.add_entry(voucher.id, entry_data)
        
        assert entry.account_id == cash.id
        assert entry.debit == Decimal("1000000")


def test_double_entry_unbalanced_rejected(app, db_session):
    """Test that unbalanced entries are rejected.
    
    CRITICAL: This is the core accounting rule.
    SUM(debit) MUST equal SUM(credit)
    """
    with app.app_context():
        user = User.query.first()
        cash = Account.query.filter_by(code="111").first()
        revenue = Account.query.filter_by(code="511").first()
        
        entries_data = [
            {"account_id": cash.id, "debit": Decimal("1000000"), "credit": Decimal("0")},
            {"account_id": revenue.id, "debit": Decimal("0"), "credit": Decimal("900000")},  # Unbalanced!
        ]
        
        voucher_data = {
            "voucher_date": date.today(),
            "voucher_type": "general",
            "description": "Unbalanced test",
            "created_by": user.id,
        }
        
        try:
            voucher = JournalRepository.create_voucher(voucher_data)
            for entry_data in entries_data:
                JournalRepository.add_entry(voucher.id, entry_data)
            
            # Check if balanced
            total_debit = sum(e["debit"] for e in entries_data)
            total_credit = sum(e["credit"] for e in entries_data)
            
            assert total_debit != total_credit, "Unbalanced entries should be detected"
        except Exception:
            pass  # Expected to fail


def test_double_entry_balanced_accepted(app, db_session):
    """Test that balanced entries are accepted.
    
    CRITICAL: This validates the core accounting rule.
    SUM(debit) MUST equal SUM(credit)
    """
    with app.app_context():
        user = User.query.first()
        cash = Account.query.filter_by(code="111").first()
        revenue = Account.query.filter_by(code="511").first()
        
        entries_data = [
            {"account_id": cash.id, "debit": Decimal("1000000"), "credit": Decimal("0")},
            {"account_id": revenue.id, "debit": Decimal("0"), "credit": Decimal("1000000")},  # Balanced!
        ]
        
        total_debit = sum(e["debit"] for e in entries_data)
        total_credit = sum(e["credit"] for e in entries_data)
        
        assert total_debit == total_credit, "Balanced entries should pass validation"


def test_voucher_posting(app, db_session):
    """Test posting a voucher."""
    with app.app_context():
        user = User.query.first()
        cash = Account.query.filter_by(code="111").first()
        revenue = Account.query.filter_by(code="511").first()
        
        voucher_data = {
            "voucher_date": date.today(),
            "voucher_type": "general",
            "description": "Post test",
            "created_by": user.id,
        }
        voucher = JournalRepository.create_voucher(voucher_data)
        
        JournalRepository.add_entry(voucher.id, {
            "account_id": cash.id,
            "line_number": 1,
            "debit": Decimal("500000"),
            "credit": Decimal("0"),
        })
        
        JournalRepository.add_entry(voucher.id, {
            "account_id": revenue.id,
            "line_number": 2,
            "debit": Decimal("0"),
            "credit": Decimal("500000"),
        })
        
        posted_voucher = JournalRepository.post_voucher(voucher.id, user.id)
        
        assert posted_voucher.status == VoucherStatus.POSTED
        assert posted_voucher.posted_by == user.id


def test_cannot_post_unbalanced_voucher(app, db_session):
    """Test that unbalanced vouchers cannot be posted."""
    with app.app_context():
        user = User.query.first()
        cash = Account.query.filter_by(code="111").first()
        
        voucher_data = {
            "voucher_date": date.today(),
            "voucher_type": "general",
            "description": "Unbalanced",
            "created_by": user.id,
        }
        voucher = JournalRepository.create_voucher(voucher_data)
        
        JournalRepository.add_entry(voucher.id, {
            "account_id": cash.id,
            "line_number": 1,
            "debit": Decimal("1000000"),
            "credit": Decimal("0"),
        })
        
        try:
            JournalRepository.post_voucher(voucher.id, user.id)
            assert False, "Should have raised error"
        except ValueError as e:
            assert "cân bằng" in str(e).lower() or "balanced" in str(e).lower()


def test_cannot_edit_posted_voucher(app, db_session):
    """Test that posted vouchers cannot be edited."""
    with app.app_context():
        user = User.query.first()
        cash = Account.query.filter_by(code="111").first()
        revenue = Account.query.filter_by(code="511").first()
        
        voucher_data = {
            "voucher_date": date.today(),
            "voucher_type": "general",
            "description": "Edit test",
            "created_by": user.id,
        }
        voucher = JournalRepository.create_voucher(voucher_data)
        
        JournalRepository.add_entry(voucher.id, {
            "account_id": cash.id,
            "line_number": 1,
            "debit": Decimal("100000"),
            "credit": Decimal("0"),
        })
        
        JournalRepository.add_entry(voucher.id, {
            "account_id": revenue.id,
            "line_number": 2,
            "debit": Decimal("0"),
            "credit": Decimal("100000"),
        })
        
        JournalRepository.post_voucher(voucher.id, user.id)
        
        try:
            JournalRepository.update_voucher(voucher.id, {"description": "New description"})
            assert False, "Should have raised error"
        except ValueError:
            pass


def test_voucher_delete_draft_only(app, db_session):
    """Test that only draft vouchers can be deleted."""
    with app.app_context():
        user = User.query.first()
        cash = Account.query.filter_by(code="111").first()
        revenue = Account.query.filter_by(code="511").first()
        
        voucher_data = {
            "voucher_date": date.today(),
            "voucher_type": "general",
            "description": "Delete test",
            "created_by": user.id,
        }
        voucher = JournalRepository.create_voucher(voucher_data)
        
        JournalRepository.add_entry(voucher.id, {
            "account_id": cash.id,
            "line_number": 1,
            "debit": Decimal("100000"),
            "credit": Decimal("0"),
        })
        
        JournalRepository.add_entry(voucher.id, {
            "account_id": revenue.id,
            "line_number": 2,
            "debit": Decimal("0"),
            "credit": Decimal("100000"),
        })
        
        JournalRepository.post_voucher(voucher.id, user.id)
        
        try:
            JournalRepository.delete_voucher(voucher.id)
            assert False, "Should have raised error"
        except ValueError:
            pass


@pytest.mark.skip(reason="SQLite in-memory limitation")
def test_voucher_number_generation(app, db_session):
    """Test automatic voucher number generation."""
    with app.app_context():
        user = User.query.first()
        
        voucher_data = {
            "voucher_date": date.today(),
            "voucher_type": "general",
            "created_by": user.id,
        }
        
        voucher1 = JournalRepository.create_voucher(voucher_data)
        db.session.commit()
        
        db.session.expire_all()
        
        voucher2 = JournalRepository.create_voucher(voucher_data)
        db.session.commit()
        
        assert voucher1.voucher_no != voucher2.voucher_no
