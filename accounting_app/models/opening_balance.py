from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List

from core.database import db
from core.utils import utc_now


class OpeningBalance(db.Model):
    """Opening Balance model for initial account balances.

    Tracks opening balances for accounts at the start of fiscal year
    for B03 Cash Flow Statement and proper period transitions.
    """

    __tablename__ = "opening_balances"

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"), nullable=False, index=True)
    fiscal_year = db.Column(db.Integer, nullable=False, index=True)
    period_type = db.Column(db.String(20), default="year", index=True)
    opening_date = db.Column(db.Date, nullable=False)
    debit = db.Column(db.Numeric(18, 2), default=Decimal("0.00"))
    credit = db.Column(db.Numeric(18, 2), default=Decimal("0.00"))
    description = db.Column(db.String(500), nullable=True)
    source = db.Column(db.String(50), default="manual")
    voucher_id = db.Column(db.Integer, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    account = db.relationship("Account", backref="opening_balances")
    creator = db.relationship("User", backref="opening_balances")

    __table_args__ = (
        db.UniqueConstraint("account_id", "fiscal_year", "period_type", name="uq_opening_account_year"),
        db.Index("ix_opening_fiscal_year", "fiscal_year"),
    )

    def __repr__(self) -> str:
        return f"<OpeningBalance {self.account_id} FY{self.fiscal_year} Dr:{self.debit} Cr:{self.credit}>"

    @property
    def net_balance(self) -> Decimal:
        """Get net balance (debit - credit)."""
        return self.debit - self.credit

    @classmethod
    def get_for_account(cls, account_id: int, fiscal_year: int, period_type: str = "year") -> Optional["OpeningBalance"]:
        """Get opening balance for an account and year."""
        return cls.query.filter_by(
            account_id=account_id,
            fiscal_year=fiscal_year,
            period_type=period_type
        ).first()

    @classmethod
    def get_all_for_year(cls, fiscal_year: int, period_type: str = "year") -> List["OpeningBalance"]:
        """Get all opening balances for a fiscal year."""
        return cls.query.filter_by(
            fiscal_year=fiscal_year,
            period_type=period_type
        ).all()

    @classmethod
    def create_or_update(
        cls,
        account_id: int,
        fiscal_year: int,
        debit: Decimal,
        credit: Decimal,
        created_by: int,
        description: str = "",
        source: str = "manual",
        period_type: str = "year"
    ) -> "OpeningBalance":
        """Create or update opening balance for an account."""
        existing = cls.get_for_account(account_id, fiscal_year, period_type)
        
        if existing:
            existing.debit = debit
            existing.credit = credit
            existing.description = description
            existing.source = source
            db.session.commit()
            return existing
        else:
            opening_date = date(fiscal_year, 1, 1)
            ob = cls(
                account_id=account_id,
                fiscal_year=fiscal_year,
                period_type=period_type,
                opening_date=opening_date,
                debit=debit,
                credit=credit,
                description=description,
                source=source,
                created_by=created_by
            )
            db.session.add(ob)
            db.session.commit()
            return ob

    def to_dict(self) -> dict:
        """Convert opening balance to dictionary."""
        return {
            "id": self.id,
            "account_id": self.account_id,
            "account_code": self.account.code if self.account else None,
            "account_name": self.account.name_vi if self.account else None,
            "fiscal_year": self.fiscal_year,
            "period_type": self.period_type,
            "opening_date": self.opening_date.isoformat() if self.opening_date else None,
            "debit": float(self.debit) if self.debit else 0.0,
            "credit": float(self.credit) if self.credit else 0.0,
            "net_balance": float(self.net_balance),
            "description": self.description,
            "source": self.source,
            "voucher_id": self.voucher_id,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class PeriodType:
    """Period type constants."""

    YEAR = "year"
    QUARTER = "quarter"
    MONTH = "month"

    CHOICES = [
        (YEAR, "Năm tài chính"),
        (QUARTER, "Quý"),
        (MONTH, "Tháng"),
    ]


class OpeningBalanceSource:
    """Opening balance source constants."""

    MANUAL = "manual"
    CONVERSION = "conversion"
    PREVIOUS_PERIOD = "previous_period"
    ADJUSTMENT = "adjustment"

    CHOICES = [
        (MANUAL, "Nhập thủ công"),
        (CONVERSION, "Chuyển đổi"),
        (PREVIOUS_PERIOD, "Kỳ trước"),
        (ADJUSTMENT, "Điều chỉnh"),
    ]
