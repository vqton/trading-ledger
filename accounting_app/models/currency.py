"""Multi-Currency Models - Exchange rates and foreign currency transactions."""

from datetime import date
from decimal import Decimal
from typing import Optional

from core.database import db
from core.utils import utc_now


class Currency(db.Model):
    """Currency model."""

    __tablename__ = "currencies"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(3), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    symbol = db.Column(db.String(10), nullable=True)
    exchange_rate = db.Column(db.Numeric(18, 6), default=Decimal("1"))
    is_base = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    def __repr__(self) -> str:
        return f"<Currency {self.code}>"


class ExchangeRate(db.Model):
    """Exchange Rate model."""

    __tablename__ = "exchange_rates"

    id = db.Column(db.Integer, primary_key=True)
    from_currency_id = db.Column(db.Integer, db.ForeignKey("currencies.id"), nullable=False)
    to_currency_id = db.Column(db.Integer, db.ForeignKey("currencies.id"), nullable=False)
    rate = db.Column(db.Numeric(18, 6), nullable=False)
    effective_date = db.Column(db.Date, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)

    from_currency = db.relationship("Currency", foreign_keys=[from_currency_id], backref="exchange_rates_from")
    to_currency = db.relationship("Currency", foreign_keys=[to_currency_id], backref="exchange_rates_to")

    __table_args__ = (
        db.Index("ix_rate_currencies", "from_currency_id", "to_currency_id", "effective_date"),
    )

    def __repr__(self) -> str:
        return f"<ExchangeRate {self.from_currency_id}->{self.to_currency_id} {self.rate}>"


class ExchangeRateMethod:
    """Exchange rate method constants."""

    SPOT = "spot"
    AVERAGE = "average"
    FIFO = "fifo"

    CHOICES = [
        (SPOT, "Tỷ giá giao ngay"),
        (AVERAGE, "Tỷ giá bình quân"),
        (FIFO, "Nhập trước xuất trước"),
    ]


class ForeignCurrencyTransaction(db.Model):
    """Foreign Currency Transaction model."""

    __tablename__ = "fc_transactions"

    id = db.Column(db.Integer, primary_key=True)
    transaction_no = db.Column(db.String(50), unique=True, nullable=False, index=True)
    transaction_date = db.Column(db.Date, nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)
    currency_id = db.Column(db.Integer, db.ForeignKey("currencies.id"), nullable=False)
    amount = db.Column(db.Numeric(18, 2), nullable=False)
    exchange_rate = db.Column(db.Numeric(18, 6), nullable=False)
    amount_vnd = db.Column(db.Numeric(18, 2), nullable=False)
    journal_voucher_id = db.Column(db.Integer, db.ForeignKey("journal_vouchers.id"), nullable=True)
    reference = db.Column(db.String(100), nullable=True)
    description = db.Column(db.String(500), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)

    currency = db.relationship("Currency", backref="fc_transactions")
    voucher = db.relationship("JournalVoucher", backref="fc_transactions")

    __table_args__ = (
        db.Index("ix_fc_date", "transaction_date"),
    )

    def __repr__(self) -> str:
        return f"<FCTransaction {self.transaction_no} {self.amount} {self.currency_id}>"

    @classmethod
    def generate_transaction_no(cls, transaction_type: str) -> str:
        """Generate transaction number."""
        from datetime import datetime
        year = datetime.now().year
        prefix = "FCT"
        last_txn = cls.query.filter(
            cls.transaction_no.like(f"{prefix}-{year}%")
        ).order_by(cls.transaction_no.desc()).first()

        if last_txn:
            last_num = int(last_txn.transaction_no.split("-")[-1])
            new_num = last_num + 1
        else:
            new_num = 1

        return f"{prefix}-{year}-{new_num:05d}"


class UnrealizedExchangeDiff(db.Model):
    """Unrealized Exchange Difference model."""

    __tablename__ = "unrealized_exchange_diff"

    id = db.Column(db.Integer, primary_key=True)
    currency_id = db.Column(db.Integer, db.ForeignKey("currencies.id"), nullable=False)
    period_year = db.Column(db.Integer, nullable=False)
    period_month = db.Column(db.Integer, nullable=False)
    exchange_rate_old = db.Column(db.Numeric(18, 6), nullable=False)
    exchange_rate_new = db.Column(db.Numeric(18, 6), nullable=False)
    amount_old = db.Column(db.Numeric(18, 2), nullable=False)
    amount_new = db.Column(db.Numeric(18, 2), nullable=False)
    exchange_diff = db.Column(db.Numeric(18, 2), nullable=False)
    is_realized = db.Column(db.Boolean, default=False)
    journal_voucher_id = db.Column(db.Integer, db.ForeignKey("journal_vouchers.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)

    currency = db.relationship("Currency", backref="unrealized_diffs")

    __table_args__ = (
        db.Index("ix_ued_period", "period_year", "period_month"),
    )

    def __repr__(self) -> str:
        return f"<UnrealizedExchangeDiff {self.currency_id} {self.period_year}-{self.period_month}>"


class FCTransactionType:
    """Foreign currency transaction type constants."""

    PURCHASE = "purchase"
    SALE = "sale"
    PAYMENT = "payment"
    RECEIPT = "receipt"

    CHOICES = [
        (PURCHASE, "Mua ngoại tệ"),
        (SALE, "Bán ngoại tệ"),
        (PAYMENT, "Thanh toán ngoại tệ"),
        (RECEIPT, "Thu ngoại tệ"),
    ]
