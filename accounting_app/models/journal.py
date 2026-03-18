from datetime import datetime, timezone, date
from decimal import Decimal
from typing import Optional, List

from core.database import db


def utc_now():
    """Return current UTC datetime."""
    return datetime.now(timezone.utc)


class JournalVoucher(db.Model):
    """Journal Voucher model - double-entry accounting documents."""

    __tablename__ = "journal_vouchers"

    id = db.Column(db.Integer, primary_key=True)
    voucher_no = db.Column(db.String(50), unique=True, nullable=False, index=True)
    voucher_date = db.Column(db.Date, nullable=False, index=True)
    voucher_type = db.Column(db.String(50), nullable=False, default="general", index=True)
    description = db.Column(db.String(500), nullable=True)
    reference = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(20), nullable=False, default="draft", index=True)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    posted_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)
    posted_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    creator = db.relationship("User", foreign_keys=[created_by], backref="created_vouchers", lazy="selectin")
    poster = db.relationship("User", foreign_keys=[posted_by], backref="posted_vouchers", lazy="selectin")
    entries = db.relationship("JournalEntry", backref="voucher", lazy="selectin", cascade="all, delete-orphan")

    __table_args__ = (
        db.Index("ix_voucher_date_status", "voucher_date", "status"),
        db.Index("ix_voucher_created_by", "created_by"),
        db.Index("ix_voucher_posted_by", "posted_by"),
    )

    def __repr__(self) -> str:
        return f"<JournalVoucher {self.voucher_no}>"

    @property
    def total_debit(self) -> Decimal:
        """Calculate total debit amount."""
        return sum(entry.debit for entry in self.entries)

    @property
    def total_credit(self) -> Decimal:
        """Calculate total credit amount."""
        return sum(entry.credit for entry in self.entries)

    @property
    def is_balanced(self) -> bool:
        """Check if journal entries are balanced."""
        return self.total_debit == self.total_credit

    @classmethod
    def generate_voucher_no(cls) -> str:
        """Generate next voucher number."""
        from datetime import datetime
        from core.database import db
        year = datetime.now().year
        
        result = db.session.execute(
            db.text("SELECT voucher_no FROM journal_vouchers WHERE voucher_no LIKE :pattern ORDER BY voucher_no DESC LIMIT 1"),
            {"pattern": f"JV-{year}%"}
        ).fetchone()

        if result:
            last_num = int(result[0].split("-")[-1])
            new_num = last_num + 1
        else:
            new_num = 1

        return f"JV-{year}-{new_num:05d}"


class JournalEntry(db.Model):
    """Journal Entry model - individual debit/credit lines."""

    __tablename__ = "journal_entries"

    id = db.Column(db.Integer, primary_key=True)
    voucher_id = db.Column(db.Integer, db.ForeignKey("journal_vouchers.id"), nullable=False, index=True)
    account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"), nullable=False, index=True)
    line_number = db.Column(db.Integer, nullable=False)
    debit = db.Column(db.Numeric(18, 2), default=Decimal("0.00"))
    credit = db.Column(db.Numeric(18, 2), default=Decimal("0.00"))
    description = db.Column(db.String(200), nullable=True)
    reference = db.Column(db.String(100), nullable=True)
    cost_center = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)

    __table_args__ = (
        db.Index("ix_entry_voucher_account", "voucher_id", "account_id"),
        db.Index("ix_entry_date", "voucher_id", "line_number"),
    )

    def __repr__(self) -> str:
        return f"<JournalEntry {self.account_id} Dr:{self.debit} Cr:{self.credit}>"

    @property
    def amount(self) -> Decimal:
        """Get the amount (debit or credit)."""
        return self.debit if self.debit > 0 else self.credit


class VoucherStatus:
    """Voucher status constants."""

    DRAFT = "draft"
    POSTED = "posted"
    LOCKED = "locked"
    CANCELLED = "cancelled"

    CHOICES = [
        (DRAFT, "Nháp"),
        (POSTED, "Đã ghi sổ"),
        (LOCKED, "Khóa"),
        (CANCELLED, "Hủy"),
    ]


class VoucherType:
    """Voucher type constants."""

    GENERAL = "general"
    CASH_RECEIPT = "cash_receipt"
    CASH_PAYMENT = "cash_payment"
    BANK_RECEIPT = "bank_receipt"
    BANK_PAYMENT = "bank_payment"
    PURCHASE = "purchase"
    SALES = "sales"

    CHOICES = [
        (GENERAL, "Chứng từ chung"),
        (CASH_RECEIPT, "Thu tiền"),
        (CASH_PAYMENT, "Chi tiền"),
        (BANK_RECEIPT, "Thu ngân hàng"),
        (BANK_PAYMENT, "Chi ngân hàng"),
        (PURCHASE, "Mua hàng"),
        (SALES, "Bán hàng"),
    ]
