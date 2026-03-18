from datetime import datetime, timezone
from typing import Optional, List

from core.database import db


def utc_now():
    """Return current UTC datetime."""
    return datetime.now(timezone.utc)


class Account(db.Model):
    """Chart of Accounts model - Vietnamese standard (Circular 99/2025/TT-BTC).

    Hierarchy structure:
    - Level 1: Major groups (1-9)
    - Level 2: Sub-groups (2 digits)
    - Level 3: Accounts (3 digits)
    - Level 4: Sub-accounts (4 digits)
    """

    __tablename__ = "accounts"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False, index=True)
    name_vi = db.Column(db.String(200), nullable=False)
    name_en = db.Column(db.String(200), nullable=True)
    parent_id = db.Column(db.Integer, db.ForeignKey("accounts.id"), nullable=True, index=True)
    level = db.Column(db.Integer, nullable=False, default=1)
    account_type = db.Column(db.String(50), nullable=False, index=True)
    normal_balance = db.Column(db.String(10), nullable=False, default="debit")
    is_postable = db.Column(db.Boolean, default=False, nullable=False, index=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    parent = db.relationship("Account", remote_side=[id], backref="children", lazy="selectin")
    journal_entries = db.relationship("JournalEntry", backref="account", lazy="dynamic")

    __table_args__ = (
        db.Index("ix_accounts_code_type", "code", "account_type"),
        db.Index("ix_accounts_parent_active", "parent_id", "is_active"),
        db.Index("ix_accounts_level", "level"),
    )

    def __repr__(self) -> str:
        return f"<Account {self.code} - {self.name_vi}>"

    @property
    def account_name(self) -> str:
        """Backward compatibility property."""
        return self.name_vi

    @property
    def account_code(self) -> str:
        """Backward compatibility property."""
        return self.code

    @property
    def full_code(self) -> str:
        """Get full account code with parent codes."""
        if self.parent:
            return f"{self.parent.full_code}.{self.code}"
        return self.code

    @property
    def is_detail(self) -> bool:
        """Backward compatibility property."""
        return self.is_postable


class AccountType:
    """Account type constants."""

    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    REVENUE = "revenue"
    EXPENSE = "expense"

    CHOICES = [
        (ASSET, "Tài sản"),
        (LIABILITY, "Nợ phải trả"),
        (EQUITY, "Vốn chủ sở hữu"),
        (REVENUE, "Doanh thu"),
        (EXPENSE, "Chi phí"),
    ]


class NormalBalance:
    """Normal balance constants."""

    DEBIT = "debit"
    CREDIT = "credit"
