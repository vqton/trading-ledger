"""Account tests."""
import pytest
from decimal import Decimal
from models.account import Account, AccountType, NormalBalance
from core.database import db
from repositories.account_repository import AccountRepository
from services.account_service import AccountService


def test_create_account(app, db_session):
    """Test account creation."""
    with app.app_context():
        account_data = {
            "account_code": "999",
            "account_name": "Test Account",
            "account_type": AccountType.ASSET,
            "normal_balance": NormalBalance.DEBIT,
            "is_detail": True,
            "is_active": True,
        }
        
        account = AccountRepository.create(account_data)
        
        assert account.account_code == "999"
        assert account.account_name == "Test Account"
        assert account.account_type == AccountType.ASSET
        assert account.is_active is True


def test_get_account_by_code(app, db_session):
    """Test get account by code."""
    with app.app_context():
        account_data = {
            "account_code": "888",
            "account_name": "Get Test",
            "account_type": AccountType.LIABILITY,
            "normal_balance": NormalBalance.CREDIT,
            "is_detail": True,
            "is_active": True,
        }
        
        AccountRepository.create(account_data)
        account = AccountRepository.get_by_code("888")
        
        assert account is not None
        assert account.account_name == "Get Test"


def test_duplicate_account_code(app, db_session):
    """Test duplicate account code is rejected."""
    with app.app_context():
        account_data = {
            "account_code": "777",
            "account_name": "Duplicate Test",
            "account_type": AccountType.ASSET,
            "normal_balance": NormalBalance.DEBIT,
            "is_detail": True,
            "is_active": True,
        }
        
        AccountRepository.create(account_data)
        
        try:
            AccountRepository.create(account_data)
            assert False, "Should have raised error"
        except Exception:
            pass


def test_update_account(app, db_session):
    """Test account update."""
    with app.app_context():
        account_data = {
            "account_code": "666",
            "account_name": "Original Name",
            "account_type": AccountType.ASSET,
            "normal_balance": NormalBalance.DEBIT,
            "is_detail": True,
            "is_active": True,
        }
        
        account = AccountRepository.create(account_data)
        
        updated = AccountRepository.update(account.id, {"account_name": "New Name"})
        
        assert updated.account_name == "New Name"


def test_soft_delete_account(app, db_session):
    """Test soft delete (deactivate) account."""
    with app.app_context():
        account_data = {
            "account_code": "555",
            "account_name": "Delete Test",
            "account_type": AccountType.ASSET,
            "normal_balance": NormalBalance.DEBIT,
            "is_detail": True,
            "is_active": True,
        }
        
        account = AccountRepository.create(account_data)
        result = AccountRepository.delete(account.id)
        
        assert result is True
        
        deleted_account = AccountRepository.get_by_id(account.id)
        assert deleted_account.is_active is False


def test_get_all_accounts(app, db_session):
    """Test get all accounts."""
    with app.app_context():
        accounts = AccountRepository.get_all()
        assert len(accounts) > 0


def test_get_active_accounts(app, db_session):
    """Test get active accounts."""
    with app.app_context():
        accounts = AccountRepository.get_active()
        for account in accounts:
            assert account.is_active is True


def test_get_detail_accounts(app, db_session):
    """Test get detail accounts only."""
    with app.app_context():
        detail_accounts = AccountRepository.get_detail_accounts()
        for account in detail_accounts:
            assert account.is_detail is True


def test_account_hierarchy(app, db_session):
    """Test account parent-child relationship."""
    with app.app_context():
        parent_data = {
            "account_code": "10",
            "account_name": "Parent Account",
            "account_type": AccountType.ASSET,
            "normal_balance": NormalBalance.DEBIT,
            "is_detail": False,
            "is_active": True,
        }
        
        child_data = {
            "account_code": "101",
            "account_name": "Child Account",
            "account_type": AccountType.ASSET,
            "normal_balance": NormalBalance.DEBIT,
            "is_detail": True,
            "is_active": True,
        }
        
        parent = AccountRepository.create(parent_data)
        child_data["parent_id"] = parent.id
        child = AccountRepository.create(child_data)
        
        assert child.parent_id == parent.id
        assert len(parent.children) > 0


def test_search_accounts(app, db_session):
    """Test account search by code or name."""
    with app.app_context():
        results = AccountRepository.search("111")
        assert len(results) > 0
        
        results = AccountRepository.search("Tiền")
        assert len(results) > 0
