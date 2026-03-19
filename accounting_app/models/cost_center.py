from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List

from core.database import db
from core.utils import utc_now


class CostCenter(db.Model):
    """Cost Center model for expense allocation (TK 641, 642).

    Tracks cost centers for B02 Income Statement expense allocation
    per Vietnamese accounting standards.
    """

    __tablename__ = "cost_centers"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    parent_id = db.Column(db.Integer, db.ForeignKey("cost_centers.id"), nullable=True, index=True)
    manager_id = db.Column(db.Integer, nullable=True)
    department = db.Column(db.String(100), nullable=True, index=True)
    budget_allocated = db.Column(db.Numeric(18, 2), default=Decimal("0.00"))
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    creator = db.relationship("User", backref="cost_centers")
    parent = db.relationship("CostCenter", remote_side=[id], backref="children", lazy="selectin")

    __table_args__ = (
        db.Index("ix_cost_center_name", "name"),
        db.Index("ix_cost_center_dept_active", "department", "is_active"),
    )

    def __repr__(self) -> str:
        return f"<CostCenter {self.code} - {self.name}>"

    @property
    def full_code(self) -> str:
        """Get full cost center code with parent codes."""
        if self.parent:
            return f"{self.parent.full_code}.{self.code}"
        return self.code

    def get_budget_used(self, start_date: Optional[date] = None, end_date: Optional[date] = None) -> Decimal:
        """Calculate budget used from journal entries."""
        from models.journal import JournalEntry, JournalVoucher, VoucherStatus

        query = db.session.query(
            db.func.sum(JournalEntry.debit)
        ).join(
            JournalVoucher, JournalEntry.voucher_id == JournalVoucher.id
        ).filter(
            JournalEntry.cost_center == self.code,
            JournalVoucher.status == VoucherStatus.POSTED
        )

        if start_date:
            query = query.filter(JournalVoucher.voucher_date >= start_date)
        if end_date:
            query = query.filter(JournalVoucher.voucher_date <= end_date)

        result = query.scalar() or Decimal("0.00")
        return Decimal(str(result))

    def get_budget_remaining(self) -> Decimal:
        """Calculate remaining budget."""
        return self.budget_allocated - self.get_budget_used()

    @classmethod
    def generate_code(cls) -> str:
        """Generate next cost center code."""
        year = datetime.now().year
        last_cc = cls.query.filter(
            cls.code.like(f"CC-{year}%")
        ).order_by(cls.code.desc()).first()

        if last_cc:
            last_num = int(last_cc.code.split("-")[-1])
            new_num = last_num + 1
        else:
            new_num = 1

        return f"CC-{year}-{new_num:04d}"

    def to_dict(self) -> dict:
        """Convert cost center to dictionary."""
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "description": self.description,
            "parent_id": self.parent_id,
            "full_code": self.full_code,
            "department": self.department,
            "budget_allocated": float(self.budget_allocated) if self.budget_allocated else 0.0,
            "budget_used": float(self.get_budget_used()),
            "budget_remaining": float(self.get_budget_remaining()),
            "is_active": self.is_active,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class CostCenterType:
    """Cost center type constants."""

    DEPARTMENT = "department"
    PROJECT = "project"
    PRODUCT = "product"
    REGION = "region"

    CHOICES = [
        (DEPARTMENT, "Phòng ban"),
        (PROJECT, "Dự án"),
        (PRODUCT, "Sản phẩm"),
        (REGION, "Khu vực"),
    ]
