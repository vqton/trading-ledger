from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List

from core.database import db
from core.utils import utc_now


class DividendPayable(db.Model):
    """Dividend Payable model (TK 332 - NEW in Circular 99/2025/TT-BTC).

    Tracks dividends declared but not yet paid to shareholders.
    TK 332 is a new account added in TT99 replacing portions of TK 338.
    """

    __tablename__ = "dividend_payables"

    id = db.Column(db.Integer, primary_key=True)
    voucher_no = db.Column(db.String(50), unique=True, nullable=False, index=True)
    declaration_date = db.Column(db.Date, nullable=False, index=True)
    shareholder_id = db.Column(db.Integer, nullable=True, index=True)
    shareholder_name = db.Column(db.String(200), nullable=False)
    shareholder_type = db.Column(db.String(20), default="individual", index=True)
    shares_owned = db.Column(db.Numeric(18, 4), default=Decimal("0.0000"))
    dividend_per_share = db.Column(db.Numeric(18, 2), default=Decimal("0.00"))
    gross_amount = db.Column(db.Numeric(18, 2), default=Decimal("0.00"))
    withholding_tax_rate = db.Column(db.Numeric(5, 4), default=Decimal("0.0000"))
    withholding_tax_amount = db.Column(db.Numeric(18, 2), default=Decimal("0.00"))
    net_amount = db.Column(db.Numeric(18, 2), default=Decimal("0.00"))
    payment_date = db.Column(db.Date, nullable=True, index=True)
    payment_status = db.Column(db.String(20), default="pending", index=True)
    payment_method = db.Column(db.String(20), nullable=True)
    bank_account = db.Column(db.String(50), nullable=True)
    tax_id = db.Column(db.String(20), nullable=True)
    fiscal_year = db.Column(db.Integer, nullable=False, index=True)
    period = db.Column(db.String(20), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    voucher_id = db.Column(db.Integer, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    creator = db.relationship("User", backref="dividend_payables")

    __table_args__ = (
        db.Index("ix_dividend_fiscal_year", "fiscal_year"),
        db.Index("ix_dividend_status_date", "payment_status", "payment_date"),
        db.Index("ix_dividend_shareholder", "shareholder_id"),
    )

    def __repr__(self) -> str:
        return f"<DividendPayable {self.voucher_no} - {self.shareholder_name}>"

    @property
    def status(self) -> str:
        return self.payment_status

    @status.setter
    def status(self, value: str) -> None:
        self.payment_status = value

    def calculate_amounts(self) -> None:
        """Calculate gross and net dividend amounts."""
        self.gross_amount = self.shares_owned * self.dividend_per_share
        self.withholding_tax_amount = self.gross_amount * self.withholding_tax_rate
        self.net_amount = self.gross_amount - self.withholding_tax_amount
        db.session.commit()

    @classmethod
    def generate_voucher_no(cls) -> str:
        """Generate next dividend voucher number."""
        year = datetime.now().year
        last_voucher = cls.query.filter(
            cls.voucher_no.like(f"DIV-{year}%")
        ).order_by(cls.voucher_no.desc()).first()

        if last_voucher:
            last_num = int(last_voucher.voucher_no.split("-")[-1])
            new_num = last_num + 1
        else:
            new_num = 1

        return f"DIV-{year}-{new_num:05d}"

    @classmethod
    def generate_payment_no(cls) -> str:
        """Generate next dividend payment number."""
        year = datetime.now().year
        last_payment = cls.query.filter(
            cls.voucher_no.like(f"PAY-{year}%")
        ).order_by(cls.voucher_no.desc()).first()

        if last_payment:
            last_num = int(last_payment.voucher_no.split("-")[-1])
            new_num = last_num + 1
        else:
            new_num = 1

        return f"PAY-{year}-{new_num:05d}"

    @classmethod
    def get_total_declared(cls, fiscal_year: int) -> Decimal:
        """Get total dividends declared for a fiscal year."""
        result = db.session.query(
            db.func.sum(cls.gross_amount)
        ).filter(cls.fiscal_year == fiscal_year).scalar() or Decimal("0.00")
        return Decimal(str(result))

    @classmethod
    def get_total_paid(cls, fiscal_year: int) -> Decimal:
        """Get total dividends paid for a fiscal year."""
        result = db.session.query(
            db.func.sum(cls.net_amount)
        ).filter(
            cls.fiscal_year == fiscal_year,
            cls.payment_status == "paid"
        ).scalar() or Decimal("0.00")
        return Decimal(str(result))

    @classmethod
    def get_total_outstanding(cls, fiscal_year: int) -> Decimal:
        """Get total dividends outstanding for a fiscal year."""
        result = db.session.query(
            db.func.sum(cls.net_amount)
        ).filter(
            cls.fiscal_year == fiscal_year,
            cls.payment_status.in_(["pending", "partial"])
        ).scalar() or Decimal("0.00")
        return Decimal(str(result))

    def to_dict(self) -> dict:
        """Convert dividend payable to dictionary."""
        return {
            "id": self.id,
            "voucher_no": self.voucher_no,
            "declaration_date": self.declaration_date.isoformat() if self.declaration_date else None,
            "shareholder_id": self.shareholder_id,
            "shareholder_name": self.shareholder_name,
            "shareholder_type": self.shareholder_type,
            "shares_owned": float(self.shares_owned) if self.shares_owned else 0.0,
            "dividend_per_share": float(self.dividend_per_share) if self.dividend_per_share else 0.0,
            "gross_amount": float(self.gross_amount) if self.gross_amount else 0.0,
            "total_amount": float(self.gross_amount) if self.gross_amount else 0.0,
            "withholding_tax_rate": float(self.withholding_tax_rate) if self.withholding_tax_rate else 0.0,
            "withholding_tax_amount": float(self.withholding_tax_amount) if self.withholding_tax_amount else 0.0,
            "withholding_tax": float(self.withholding_tax_amount) if self.withholding_tax_amount else 0.0,
            "net_amount": float(self.net_amount) if self.net_amount else 0.0,
            "payment_date": self.payment_date.isoformat() if self.payment_date else None,
            "payment_status": self.payment_status,
            "status": self.payment_status,
            "payment_method": self.payment_method,
            "bank_account": self.bank_account,
            "tax_id": self.tax_id,
            "fiscal_year": self.fiscal_year,
            "period": self.period,
            "notes": self.notes,
            "voucher_id": self.voucher_id,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ShareholderType:
    """Shareholder type constants."""

    INDIVIDUAL = "individual"
    CORPORATE = "corporate"
    FOREIGN = "foreign"
    GOVERNMENT = "government"

    CHOICES = [
        (INDIVIDUAL, "Cá nhân"),
        (CORPORATE, "Doanh nghiệp"),
        (FOREIGN, "Người nước ngoài"),
        (GOVERNMENT, "Nhà nước"),
    ]


class DividendPaymentStatus:
    """Dividend payment status constants."""

    PENDING = "pending"
    PARTIAL = "partial"
    PAID = "paid"
    CANCELLED = "cancelled"

    CHOICES = [
        (PENDING, "Chưa thanh toán"),
        (PARTIAL, "Thanh toán một phần"),
        (PAID, "Đã thanh toán"),
        (CANCELLED, "Hủy"),
    ]


class DividendPaymentMethod:
    """Dividend payment method constants."""

    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"
    STOCK_DIVIDEND = "stock_dividend"
    SCRIP = "scrip"

    CHOICES = [
        (CASH, "Tiền mặt"),
        (BANK_TRANSFER, "Chuyển khoản"),
        (STOCK_DIVIDEND, "Cổ tức bằng cổ phiếu"),
        (SCRIP, "Phiếu lưu ký"),
    ]
