"""Bank & Cash Models - Bank reconciliation and cash flow."""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from core.database import db
from core.utils import utc_now


class BankAccount(db.Model):
    """Bank Account model."""

    __tablename__ = "bank_accounts"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    bank_name = db.Column(db.String(200), nullable=True)
    account_number = db.Column(db.String(50), nullable=True)
    account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"), nullable=False)
    currency = db.Column(db.String(3), default="VND")
    opening_balance = db.Column(db.Numeric(18, 2), default=Decimal("0"))
    current_balance = db.Column(db.Numeric(18, 2), default=Decimal("0"))
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    account = db.relationship("Account", backref="bank_accounts")
    statements = db.relationship("BankStatement", backref="bank_account", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<BankAccount {self.code} - {self.name}>"


class BankStatement(db.Model):
    """Bank Statement model for reconciliation."""

    __tablename__ = "bank_statements"

    id = db.Column(db.Integer, primary_key=True)
    bank_account_id = db.Column(db.Integer, db.ForeignKey("bank_accounts.id"), nullable=False)
    statement_date = db.Column(db.Date, nullable=False)
    statement_no = db.Column(db.String(50), nullable=False, index=True)
    description = db.Column(db.String(500), nullable=True)
    debit = db.Column(db.Numeric(18, 2), default=Decimal("0"))
    credit = db.Column(db.Numeric(18, 2), default=Decimal("0"))
    balance = db.Column(db.Numeric(18, 2), default=Decimal("0"))
    reference = db.Column(db.String(100), nullable=True)
    is_reconciled = db.Column(db.Boolean, default=False)
    journal_entry_id = db.Column(db.Integer, db.ForeignKey("journal_entries.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)

    __table_args__ = (
        db.Index("ix_statement_bank_date", "bank_account_id", "statement_date"),
    )

    def __repr__(self) -> str:
        return f"<BankStatement {self.statement_no} - {self.statement_date}>"


class BankReconciliation(db.Model):
    """Bank Reconciliation model."""

    __tablename__ = "bank_reconciliations"

    id = db.Column(db.Integer, primary_key=True)
    bank_account_id = db.Column(db.Integer, db.ForeignKey("bank_accounts.id"), nullable=False)
    reconciliation_date = db.Column(db.Date, nullable=False)
    period_year = db.Column(db.Integer, nullable=False)
    period_month = db.Column(db.Integer, nullable=False)
    bank_balance = db.Column(db.Numeric(18, 2), nullable=False)
    book_balance = db.Column(db.Numeric(18, 2), nullable=False)
    deposit_in_transit = db.Column(db.Numeric(18, 2), default=Decimal("0"))
    outstanding_checks = db.Column(db.Numeric(18, 2), default=Decimal("0"))
    bank_charges = db.Column(db.Numeric(18, 2), default=Decimal("0"))
    interest_income = db.Column(db.Numeric(18, 2), default=Decimal("0"))
    reconciled_balance = db.Column(db.Numeric(18, 2), nullable=False)
    notes = db.Column(db.String(500), nullable=True)
    status = db.Column(db.String(20), default="draft")
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)

    bank_account = db.relationship("BankAccount", backref="reconciliations")
    creator = db.relationship("User", backref="bank_reconciliations")

    __table_args__ = (
        db.Index("ix_recon_period", "period_year", "period_month"),
    )

    def __repr__(self) -> str:
        return f"<BankReconciliation {self.period_year}-{self.period_month}>"


class ReconciliationStatus:
    """Reconciliation status constants."""

    DRAFT = "draft"
    COMPLETED = "completed"

    CHOICES = [
        (DRAFT, "Nháp"),
        (COMPLETED, "Hoàn thành"),
    ]
