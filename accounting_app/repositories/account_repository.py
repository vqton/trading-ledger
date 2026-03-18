from typing import List, Optional

from models.account import Account, AccountType
from core.database import db


class AccountRepository:
    """Repository for Account database operations."""

    @staticmethod
    def get_all() -> List[Account]:
        """Get all accounts ordered by code."""
        return Account.query.order_by(Account.code).all()

    @staticmethod
    def get_by_id(account_id: int) -> Optional[Account]:
        """Get account by ID."""
        return db.session.get(Account, account_id)

    @staticmethod
    def get_by_code(account_code: str) -> Optional[Account]:
        """Get account by code."""
        return Account.query.filter_by(code=account_code).first()

    @staticmethod
    def get_active() -> List[Account]:
        """Get all active accounts."""
        return Account.query.filter_by(is_active=True).order_by(Account.code).all()

    @staticmethod
    def get_detail_accounts() -> List[Account]:
        """Get detail accounts (postable accounts - leaf nodes)."""
        return Account.query.filter_by(
            is_postable=True, is_active=True
        ).order_by(Account.code).all()

    @staticmethod
    def get_by_type(account_type: str) -> List[Account]:
        """Get accounts by type."""
        return Account.query.filter_by(
            account_type=account_type, is_active=True
        ).order_by(Account.code).all()

    @staticmethod
    def get_parent_accounts() -> List[Account]:
        """Get parent accounts (non-postable - group accounts)."""
        return Account.query.filter_by(
            is_postable=False, is_active=True
        ).order_by(Account.code).all()

    @staticmethod
    def get_children(parent_id: int) -> List[Account]:
        """Get child accounts of a parent."""
        return Account.query.filter_by(parent_id=parent_id).all()

    @staticmethod
    def create(account_data: dict) -> Account:
        """Create new account."""
        account = Account(
            code=account_data.get("code") or account_data.get("account_code"),
            name_vi=account_data.get("name_vi") or account_data.get("account_name"),
            account_type=account_data["account_type"],
            parent_id=account_data.get("parent_id"),
            normal_balance=account_data.get("normal_balance", "debit"),
            is_active=account_data.get("is_active", True),
            is_postable=account_data.get("is_postable", account_data.get("is_detail", True)),
            level=account_data.get("level", 3),
        )
        db.session.add(account)
        db.session.commit()
        return account

    @staticmethod
    def update(account_id: int, account_data: dict) -> Account:
        """Update existing account."""
        account = db.session.get(Account, account_id)
        if not account:
            raise ValueError(f"Account {account_id} not found")

        if "name_vi" in account_data:
            account.name_vi = account_data["name_vi"]
        if "account_name" in account_data:
            account.name_vi = account_data["account_name"]
        if "account_type" in account_data:
            account.account_type = account_data["account_type"]
        if "parent_id" in account_data:
            account.parent_id = account_data["parent_id"]
        if "normal_balance" in account_data:
            account.normal_balance = account_data["normal_balance"]
        if "is_active" in account_data:
            account.is_active = account_data["is_active"]
        if "is_postable" in account_data:
            account.is_postable = account_data["is_postable"]
        if "is_detail" in account_data:
            account.is_postable = account_data["is_detail"]

        db.session.commit()
        return account

    @staticmethod
    def delete(account_id: int) -> bool:
        """Delete account (soft delete)."""
        account = db.session.get(Account, account_id)
        if not account:
            return False

        account.is_active = False
        db.session.commit()
        return True

    @staticmethod
    def has_children(account_id: int) -> bool:
        """Check if account has child accounts."""
        return Account.query.filter_by(parent_id=account_id).count() > 0

    @staticmethod
    def has_transactions(account_id: int) -> bool:
        """Check if account has journal entries."""
        from models.journal import JournalEntry
        return JournalEntry.query.filter_by(account_id=account_id).count() > 0

    @staticmethod
    def search(query: str) -> List[Account]:
        """Search accounts by code or name."""
        return Account.query.filter(
            db.or_(
                Account.code.ilike(f"%{query}%"),
                Account.name_vi.ilike(f"%{query}%"),
            )
        ).order_by(Account.code).all()
