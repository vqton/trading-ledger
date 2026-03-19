from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List

from core.database import db
from core.utils import utc_now


class Project(db.Model):
    """Project model for project-based revenue/expense tracking (B02, B05).

    Tracks projects for revenue and expense allocation per Vietnamese
    accounting standards for financial reporting.
    """

    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    customer_id = db.Column(db.Integer, nullable=True, index=True)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    expected_completion_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), default="planning", index=True)
    project_type = db.Column(db.String(50), default="service", index=True)
    total_contract_value = db.Column(db.Numeric(18, 2), default=Decimal("0.00"))
    total_revenue = db.Column(db.Numeric(18, 2), default=Decimal("0.00"))
    total_expense = db.Column(db.Numeric(18, 2), default=Decimal("0.00"))
    completion_percentage = db.Column(db.Numeric(5, 2), default=Decimal("0.00"))
    manager_id = db.Column(db.Integer, nullable=True)
    cost_center_id = db.Column(db.Integer, nullable=True, index=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    creator = db.relationship("User", backref="projects")

    __table_args__ = (
        db.Index("ix_project_name", "name"),
        db.Index("ix_project_status_active", "status", "is_active"),
    )

    def __repr__(self) -> str:
        return f"<Project {self.code} - {self.name}>"

    @property
    def profit(self) -> Decimal:
        """Calculate project profit."""
        return self.total_revenue - self.total_expense

    @property
    def profit_margin(self) -> Decimal:
        """Calculate profit margin percentage."""
        if self.total_revenue == 0:
            return Decimal("0.00")
        return (self.profit / self.total_revenue) * 100

    def get_revenue_from_journal(self) -> Decimal:
        """Calculate total revenue from journal entries."""
        from models.journal import JournalEntry, JournalVoucher, VoucherStatus
        from models.account import Account

        revenue_accounts = Account.query.filter(
            Account.code.like("5%"),
            Account.is_detail == True
        ).all()
        revenue_ids = [acc.id for acc in revenue_accounts]

        if not revenue_ids:
            return Decimal("0.00")

        result = db.session.query(
            db.func.sum(JournalEntry.credit)
        ).join(
            JournalVoucher, JournalEntry.voucher_id == JournalVoucher.id
        ).filter(
            JournalEntry.account_id.in_(revenue_ids),
            JournalEntry.reference == self.code,
            JournalVoucher.status == VoucherStatus.POSTED
        ).scalar() or Decimal("0.00")

        return Decimal(str(result))

    def get_expense_from_journal(self) -> Decimal:
        """Calculate total expense from journal entries."""
        from models.journal import JournalEntry, JournalVoucher, VoucherStatus
        from models.account import Account

        expense_accounts = Account.query.filter(
            Account.code.like("6%"),
            Account.is_detail == True
        ).all()
        expense_ids = [acc.id for acc in expense_accounts]

        if not expense_ids:
            return Decimal("0.00")

        result = db.session.query(
            db.func.sum(JournalEntry.debit)
        ).join(
            JournalVoucher, JournalEntry.voucher_id == JournalVoucher.id
        ).filter(
            JournalEntry.account_id.in_(expense_ids),
            JournalEntry.reference == self.code,
            JournalVoucher.status == VoucherStatus.POSTED
        ).scalar() or Decimal("0.00")

        return Decimal(str(result))

    def update_totals(self) -> None:
        """Update total revenue and expense from journal entries."""
        self.total_revenue = self.get_revenue_from_journal()
        self.total_expense = self.get_expense_from_journal()
        db.session.commit()

    @classmethod
    def generate_code(cls) -> str:
        """Generate next project code."""
        year = datetime.now().year
        last_proj = cls.query.filter(
            cls.code.like(f"PRJ-{year}%")
        ).order_by(cls.code.desc()).first()

        if last_proj:
            last_num = int(last_proj.code.split("-")[-1])
            new_num = last_num + 1
        else:
            new_num = 1

        return f"PRJ-{year}-{new_num:04d}"

    def to_dict(self) -> dict:
        """Convert project to dictionary."""
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "description": self.description,
            "customer_id": self.customer_id,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "expected_completion_date": self.expected_completion_date.isoformat() if self.expected_completion_date else None,
            "status": self.status,
            "project_type": self.project_type,
            "total_contract_value": float(self.total_contract_value) if self.total_contract_value else 0.0,
            "total_revenue": float(self.total_revenue) if self.total_revenue else 0.0,
            "total_expense": float(self.total_expense) if self.total_expense else 0.0,
            "profit": float(self.profit),
            "profit_margin": float(self.profit_margin),
            "completion_percentage": float(self.completion_percentage) if self.completion_percentage else 0.0,
            "manager_id": self.manager_id,
            "cost_center_id": self.cost_center_id,
            "is_active": self.is_active,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ProjectStatus:
    """Project status constants."""

    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

    CHOICES = [
        (PLANNING, "Lập kế hoạch"),
        (ACTIVE, "Đang thực hiện"),
        (ON_HOLD, "Tạm dừng"),
        (COMPLETED, "Hoàn thành"),
        (CANCELLED, "Hủy bỏ"),
    ]


class ProjectType:
    """Project type constants."""

    SERVICE = "service"
    CONSTRUCTION = "construction"
    MANUFACTURING = "manufacturing"
    CONSULTING = "consulting"
    SOFTWARE = "software"

    CHOICES = [
        (SERVICE, "Dịch vụ"),
        (CONSTRUCTION, "Xây dựng"),
        (MANUFACTURING, "Sản xuất"),
        (CONSULTING, "Tư vấn"),
        (SOFTWARE, "Phần mềm"),
    ]
