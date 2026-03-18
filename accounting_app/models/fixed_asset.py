"""Fixed Asset Models - Circular 45/2023/TT-BTC."""

from datetime import date
from decimal import Decimal
from typing import Optional

from core.database import db
from core.utils import utc_now


class FixedAssetCategory(db.Model):
    """Fixed Asset Category model."""

    __tablename__ = "fixed_asset_categories"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    depreciation_method = db.Column(db.String(20), nullable=False, default="straight_line")
    useful_life_years = db.Column(db.Integer, nullable=True)
    depreciation_rate = db.Column(db.Numeric(5, 2), default=Decimal("0"))
    account_asset_id = db.Column(db.Integer, db.ForeignKey("accounts.id"), nullable=True)
    account_depreciation_id = db.Column(db.Integer, db.ForeignKey("accounts.id"), nullable=True)
    account_expense_id = db.Column(db.Integer, db.ForeignKey("accounts.id"), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)

    assets = db.relationship("FixedAsset", backref="category", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<FixedAssetCategory {self.code} - {self.name}>"


class FixedAsset(db.Model):
    """Fixed Asset model."""

    __tablename__ = "fixed_assets"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("fixed_asset_categories.id"), nullable=False)
    purchase_date = db.Column(db.Date, nullable=False)
    useful_life_years = db.Column(db.Integer, nullable=False)
    original_cost = db.Column(db.Numeric(18, 2), nullable=False)
    residual_value = db.Column(db.Numeric(18, 2), default=Decimal("0"))
    depreciation_method = db.Column(db.String(20), nullable=False, default="straight_line")
    depreciation_rate = db.Column(db.Numeric(5, 2), default=Decimal("0"))
    accumulated_depreciation = db.Column(db.Numeric(18, 2), default=Decimal("0"))
    net_book_value = db.Column(db.Numeric(18, 2), default=Decimal("0"))
    location = db.Column(db.String(200), nullable=True)
    serial_number = db.Column(db.String(100), nullable=True)
    description = db.Column(db.String(500), nullable=True)
    status = db.Column(db.String(20), default="in_use")
    account_asset_id = db.Column(db.Integer, db.ForeignKey("accounts.id"), nullable=True)
    account_depreciation_id = db.Column(db.Integer, db.ForeignKey("accounts.id"), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    creator = db.relationship("User", backref="fixed_assets")

    __table_args__ = (
        db.Index("ix_fa_category", "category_id"),
        db.Index("fa_status", "status"),
    )

    def __repr__(self) -> str:
        return f"<FixedAsset {self.code} - {self.name}>"

    def calculate_depreciation(self) -> Decimal:
        """Calculate annual depreciation."""
        if self.depreciation_method == "straight_line":
            depreciable = self.original_cost - self.residual_value
            return depreciable / self.useful_life_years if self.useful_life_years > 0 else Decimal("0")
        elif self.depreciation_method == "declining_balance":
            rate = self.depreciation_rate / 100 if self.depreciation_rate else Decimal("0.1")
            return self.net_book_value * rate
        return Decimal("0")

    def update_net_book_value(self) -> None:
        """Update net book value."""
        self.net_book_value = self.original_cost - self.accumulated_depreciation


class DepreciationEntry(db.Model):
    """Depreciation Entry model for tracking depreciation."""

    __tablename__ = "depreciation_entries"

    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey("fixed_assets.id"), nullable=False)
    period_year = db.Column(db.Integer, nullable=False)
    period_month = db.Column(db.Integer, nullable=False)
    depreciation_amount = db.Column(db.Numeric(18, 2), nullable=False)
    accumulated_before = db.Column(db.Numeric(18, 2), nullable=False)
    accumulated_after = db.Column(db.Numeric(18, 2), nullable=False)
    journal_voucher_id = db.Column(db.Integer, db.ForeignKey("journal_vouchers.id"), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)

    asset = db.relationship("FixedAsset", backref="depreciation_entries")
    voucher = db.relationship("JournalVoucher", backref="depreciation_entries")

    __table_args__ = (
        db.Index("ix_depr_period", "period_year", "period_month"),
    )

    def __repr__(self) -> str:
        return f"<DepreciationEntry {self.asset_id} {self.period_year}-{self.period_month}>"


class DepreciationMethod:
    """Depreciation method constants."""

    STRAIGHT_LINE = "straight_line"
    DECLINING_BALANCE = "declining_balance"
    SUM_OF_YEARS = "sum_of_years"
    UNITS_OF_PRODUCTION = "units_of_production"

    CHOICES = [
        (STRAIGHT_LINE, "Khấu hao đường thẳng"),
        (DECLINING_BALANCE, "Khấu hao theo số dư giảm dần"),
        (SUM_OF_YEARS, "Khấu hao theo tổng số năm"),
        (UNITS_OF_PRODUCTION, "Khấu hao theo sản lượng"),
    ]


class AssetStatus:
    """Fixed asset status constants."""

    IN_USE = "in_use"
    UNDER_CONSTRUCTION = "under_construction"
    SUSPENDED = "suspended"
    DISPOSED = "disposed"
    LIQUIDATED = "liquidated"

    CHOICES = [
        (IN_USE, "Đang sử dụng"),
        (UNDER_CONSTRUCTION, "Đang xây dựng"),
        (SUSPENDED, "Tạm ngừng"),
        (DISPOSED, "Đã thanh lý"),
        (LIQUIDATED, "Đã nhượng bán"),
    ]
