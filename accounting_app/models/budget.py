"""Budget Models - Budget management and tracking."""

from datetime import date
from decimal import Decimal
from typing import Optional

from core.database import db
from core.utils import utc_now


class Budget(db.Model):
    """Budget model for annual budget planning."""

    __tablename__ = "budgets"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    fiscal_year = db.Column(db.Integer, nullable=False, index=True)
    period_type = db.Column(db.String(20), nullable=False, default="annual")
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default="draft")
    description = db.Column(db.String(500), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    creator = db.relationship("User", backref="budgets")
    details = db.relationship("BudgetDetail", backref="budget", lazy="dynamic", cascade="all, delete-orphan")

    __table_args__ = (
        db.Index("ix_budget_year", "fiscal_year"),
    )

    def __repr__(self) -> str:
        return f"<Budget {self.code} - {self.fiscal_year}>"


class BudgetDetail(db.Model):
    """Budget detail by account."""

    __tablename__ = "budget_details"

    id = db.Column(db.Integer, primary_key=True)
    budget_id = db.Column(db.Integer, db.ForeignKey("budgets.id"), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"), nullable=False)
    budget_amount = db.Column(db.Numeric(18, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)

    account = db.relationship("Account", backref="budget_details")

    __table_args__ = (
        db.Index("ix_budget_detail_budget_account", "budget_id", "account_id"),
    )

    def __repr__(self) -> str:
        return f"<BudgetDetail {self.budget_id} - {self.account_id}>"


class BudgetActual(db.Model):
    """Budget actuals - tracks actual amounts vs budget."""

    __tablename__ = "budget_actuals"

    id = db.Column(db.Integer, primary_key=True)
    budget_detail_id = db.Column(db.Integer, db.ForeignKey("budget_details.id"), nullable=False)
    period_year = db.Column(db.Integer, nullable=False)
    period_month = db.Column(db.Integer, nullable=False)
    actual_amount = db.Column(db.Numeric(18, 2), default=Decimal("0"))
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)

    budget_detail = db.relationship("BudgetDetail", backref="actuals")

    __table_args__ = (
        db.Index("ix_budget_actual_period", "period_year", "period_month"),
    )

    def __repr__(self) -> str:
        return f"<BudgetActual {self.period_year}-{self.period_month}>"


class BudgetStatus:
    """Budget status constants."""

    DRAFT = "draft"
    APPROVED = "approved"
    CLOSED = "closed"

    CHOICES = [
        (DRAFT, "Nháp"),
        (APPROVED, "Đã duyệt"),
        (CLOSED, "Đã đóng"),
    ]


class BudgetPeriodType:
    """Budget period type constants."""

    ANNUAL = "annual"
    QUARTERLY = "quarterly"
    MONTHLY = "monthly"

    CHOICES = [
        (ANNUAL, "Năm"),
        (QUARTERLY, "Quý"),
        (MONTHLY, "Tháng"),
    ]
