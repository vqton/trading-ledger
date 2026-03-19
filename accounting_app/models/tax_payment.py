from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List

from core.database import db
from core.utils import utc_now


class TaxPayment(db.Model):
    """Tax Payment model for tracking tax obligations and payments.

    Tracks VAT, CIT, PIT, and other tax payments for compliance
    with Vietnamese tax regulations.
    """

    __tablename__ = "tax_payments"

    id = db.Column(db.Integer, primary_key=True)
    payment_no = db.Column(db.String(50), unique=True, nullable=False, index=True)
    tax_type = db.Column(db.String(20), nullable=False, index=True)
    declaration_no = db.Column(db.String(50), nullable=True)
    declaration_date = db.Column(db.Date, nullable=True)
    period_year = db.Column(db.Integer, nullable=False, index=True)
    period_month = db.Column(db.Integer, nullable=True)
    period_quarter = db.Column(db.Integer, nullable=True)
    taxable_amount = db.Column(db.Numeric(18, 2), default=Decimal("0.00"))
    tax_rate = db.Column(db.Numeric(5, 4), default=Decimal("0.0000"))
    tax_amount = db.Column(db.Numeric(18, 2), default=Decimal("0.00"))
    interest_amount = db.Column(db.Numeric(18, 2), default=Decimal("0.00"))
    penalty_amount = db.Column(db.Numeric(18, 2), default=Decimal("0.00"))
    total_amount = db.Column(db.Numeric(18, 2), default=Decimal("0.00"))
    payment_date = db.Column(db.Date, nullable=True, index=True)
    due_date = db.Column(db.Date, nullable=True, index=True)
    payment_status = db.Column(db.String(20), default="pending", index=True)
    payment_method = db.Column(db.String(20), nullable=True)
    bank_payment_date = db.Column(db.Date, nullable=True)
    bank_transaction_no = db.Column(db.String(100), nullable=True)
    tax_authority = db.Column(db.String(200), nullable=True)
    tax_office_code = db.Column(db.String(20), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    voucher_id = db.Column(db.Integer, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    creator = db.relationship("User", backref="tax_payments")

    __table_args__ = (
        db.Index("ix_tax_payment_year_type", "period_year", "tax_type"),
        db.Index("ix_tax_payment_status_date", "payment_status", "payment_date"),
        db.Index("ix_tax_payment_due_date", "due_date"),
    )

    def __repr__(self) -> str:
        return f"<TaxPayment {self.payment_no} - {self.tax_type} {self.total_amount}>"

    @property
    def is_overdue(self) -> bool:
        """Check if payment is overdue."""
        if self.payment_status == "paid":
            return False
        if self.due_date:
            return date.today() > self.due_date
        return False

    @property
    def days_overdue(self) -> int:
        """Calculate days overdue."""
        if not self.is_overdue or not self.due_date:
            return 0
        return (date.today() - self.due_date).days

    def calculate_total(self) -> None:
        """Calculate total amount including interest and penalty."""
        self.total_amount = self.tax_amount + self.interest_amount + self.penalty_amount
        db.session.commit()

    @classmethod
    def generate_payment_no(cls, tax_type: str) -> str:
        """Generate next tax payment number."""
        year = datetime.now().year
        prefix_map = {
            "vat": "TVA",
            "cit": "TCN",
            "pit": "TTN",
            "wht": "TKH",
            "other": "TQT",
        }
        prefix = prefix_map.get(tax_type, "TAX")

        last_payment = cls.query.filter(
            cls.payment_no.like(f"{prefix}-{year}%")
        ).order_by(cls.payment_no.desc()).first()

        if last_payment:
            last_num = int(last_payment.payment_no.split("-")[-1])
            new_num = last_num + 1
        else:
            new_num = 1

        return f"{prefix}-{year}-{new_num:05d}"

    @classmethod
    def get_total_by_type(cls, tax_type: str, fiscal_year: int) -> Decimal:
        """Get total tax paid for a type and year."""
        result = db.session.query(
            db.func.sum(cls.total_amount)
        ).filter(
            cls.tax_type == tax_type,
            cls.period_year == fiscal_year,
            cls.payment_status == "paid"
        ).scalar() or Decimal("0.00")
        return Decimal(str(result))

    @classmethod
    def get_outstanding_by_type(cls, tax_type: str, fiscal_year: int) -> Decimal:
        """Get outstanding tax for a type and year."""
        result = db.session.query(
            db.func.sum(cls.total_amount)
        ).filter(
            cls.tax_type == tax_type,
            cls.period_year == fiscal_year,
            cls.payment_status.in_(["pending", "partial", "overdue"])
        ).scalar() or Decimal("0.00")
        return Decimal(str(result))

    def to_dict(self) -> dict:
        """Convert tax payment to dictionary."""
        return {
            "id": self.id,
            "payment_no": self.payment_no,
            "tax_type": self.tax_type,
            "declaration_no": self.declaration_no,
            "declaration_date": self.declaration_date.isoformat() if self.declaration_date else None,
            "period_year": self.period_year,
            "period_month": self.period_month,
            "period_quarter": self.period_quarter,
            "taxable_amount": float(self.taxable_amount) if self.taxable_amount else 0.0,
            "tax_rate": float(self.tax_rate) if self.tax_rate else 0.0,
            "tax_amount": float(self.tax_amount) if self.tax_amount else 0.0,
            "interest_amount": float(self.interest_amount) if self.interest_amount else 0.0,
            "penalty_amount": float(self.penalty_amount) if self.penalty_amount else 0.0,
            "total_amount": float(self.total_amount) if self.total_amount else 0.0,
            "payment_date": self.payment_date.isoformat() if self.payment_date else None,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "payment_status": self.payment_status,
            "payment_method": self.payment_method,
            "bank_payment_date": self.bank_payment_date.isoformat() if self.bank_payment_date else None,
            "bank_transaction_no": self.bank_transaction_no,
            "tax_authority": self.tax_authority,
            "tax_office_code": self.tax_office_code,
            "is_overdue": self.is_overdue,
            "days_overdue": self.days_overdue,
            "notes": self.notes,
            "voucher_id": self.voucher_id,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class TaxType:
    """Tax type constants."""

    VAT = "vat"
    CIT = "cit"
    PIT = "pit"
    WHT = "wht"
    PBT = "pbt"
    OTHER = "other"

    CHOICES = [
        (VAT, "Thuế GTGT"),
        (CIT, "Thuế TNDN"),
        (PIT, "Thuế TNCN"),
        (WHT, "Thuế khấu trừ"),
        (PBT, "Thuế bất động sản"),
        (OTHER, "Thuế khác"),
    ]


class TaxPaymentStatus:
    """Tax payment status constants."""

    PENDING = "pending"
    PARTIAL = "partial"
    PAID = "paid"
    OVERDUE = "overdue"
    EXEMPTED = "exempted"
    CANCELLED = "cancelled"

    CHOICES = [
        (PENDING, "Chưa nộp"),
        (PARTIAL, "Nộp một phần"),
        (PAID, "Đã nộp"),
        (OVERDUE, "Quá hạn"),
        (EXEMPTED, "Được miễn"),
        (CANCELLED, "Hủy bỏ"),
    ]


class TaxPaymentMethod:
    """Tax payment method constants."""

    BANK_TRANSFER = "bank_transfer"
    CASH = "cash"
    CHEQUE = "cheque"
    OFFSET = "offset"

    CHOICES = [
        (BANK_TRANSFER, "Chuyển khoản"),
        (CASH, "Tiền mặt"),
        (CHEQUE, "Séc"),
        (OFFSET, "Bù trừ"),
    ]
