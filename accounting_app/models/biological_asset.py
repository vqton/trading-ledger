from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List

from core.database import db
from core.utils import utc_now


class BiologicalAsset(db.Model):
    """Biological Asset model (TK 215 - NEW in Circular 99/2025/TT-BTC).

    Tracks biological assets (plants, animals) at fair value less costs to sell
    per Vietnamese accounting standards. This is a new account added in TT99.
    """

    __tablename__ = "biological_assets"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    asset_type = db.Column(db.String(50), nullable=False, index=True)
    category = db.Column(db.String(100), nullable=True, index=True)
    acquisition_date = db.Column(db.Date, nullable=True)
    initial_quantity = db.Column(db.Numeric(18, 4), default=Decimal("0.0000"))
    current_quantity = db.Column(db.Numeric(18, 4), default=Decimal("0.0000"))
    unit = db.Column(db.String(20), nullable=True)
    fair_value_per_unit = db.Column(db.Numeric(18, 2), default=Decimal("0.00"))
    total_fair_value = db.Column(db.Numeric(18, 2), default=Decimal("0.00"))
    costs_to_sell = db.Column(db.Numeric(18, 2), default=Decimal("0.00"))
    net_value = db.Column(db.Numeric(18, 2), default=Decimal("0.00"))
    location = db.Column(db.String(200), nullable=True)
    related_account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"), nullable=True)
    warehouse_id = db.Column(db.Integer, db.ForeignKey("warehouses.id"), nullable=True)
    status = db.Column(db.String(20), default="active", index=True)
    notes = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    creator = db.relationship("User", backref="biological_assets")
    related_account = db.relationship("Account", backref="biological_assets")
    warehouse = db.relationship("Warehouse", backref="biological_assets")

    __table_args__ = (
        db.Index("ix_bio_asset_name", "name"),
        db.Index("ix_bio_asset_type_active", "asset_type", "status"),
        db.Index("ix_bio_asset_category", "category"),
    )

    def __repr__(self) -> str:
        return f"<BiologicalAsset {self.code} - {self.name}>"

    def calculate_fair_value(self) -> Decimal:
        """Calculate total fair value."""
        return self.current_quantity * self.fair_value_per_unit

    def calculate_net_value(self) -> Decimal:
        """Calculate net fair value less costs to sell."""
        return self.calculate_fair_value() - self.costs_to_sell

    def update_net_value(self) -> None:
        """Update net value based on current quantity and fair value."""
        self.total_fair_value = self.calculate_fair_value()
        self.net_value = self.calculate_net_value()
        db.session.commit()

    @classmethod
    def generate_code(cls) -> str:
        """Generate next biological asset code."""
        year = datetime.now().year
        last_asset = cls.query.filter(
            cls.code.like(f"BIO-{year}%")
        ).order_by(cls.code.desc()).first()

        if last_asset:
            last_num = int(last_asset.code.split("-")[-1])
            new_num = last_num + 1
        else:
            new_num = 1

        return f"BIO-{year}-{new_num:04d}"

    def to_dict(self) -> dict:
        """Convert biological asset to dictionary."""
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "description": self.description,
            "asset_type": self.asset_type,
            "category": self.category,
            "acquisition_date": self.acquisition_date.isoformat() if self.acquisition_date else None,
            "initial_quantity": float(self.initial_quantity) if self.initial_quantity else 0.0,
            "current_quantity": float(self.current_quantity) if self.current_quantity else 0.0,
            "unit": self.unit,
            "fair_value_per_unit": float(self.fair_value_per_unit) if self.fair_value_per_unit else 0.0,
            "total_fair_value": float(self.total_fair_value) if self.total_fair_value else 0.0,
            "costs_to_sell": float(self.costs_to_sell) if self.costs_to_sell else 0.0,
            "net_value": float(self.net_value) if self.net_value else 0.0,
            "location": self.location,
            "related_account_id": self.related_account_id,
            "related_account_code": self.related_account.code if self.related_account else None,
            "warehouse_id": self.warehouse_id,
            "warehouse_name": self.warehouse.name if self.warehouse else None,
            "status": self.status,
            "notes": self.notes,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class BiologicalAssetType:
    """Biological asset type constants."""

    CONSUMABLE = "consumable"
    BEARER = "bearer"
    AGRICULTURAL_PRODUCE = "agricultural_produce"

    CHOICES = [
        (CONSUMABLE, "Tài sản sinh học tiêu thụ"),
        (BEARER, "Tài sản sinh học cho thu hoạch"),
        (AGRICULTURAL_PRODUCE, "Nông sản/Sản phẩm"),
    ]


class BiologicalAssetCategory:
    """Biological asset category constants."""

    LIVESTOCK = "livestock"
    POULTRY = "poultry"
    AQUACULTURE = "aquaculture"
    PERENNIAL_CROPS = "perennial_crops"
    ANNUAL_CROPS = "annual_crops"
    FORESTRY = "forestry"
    OTHER = "other"

    CHOICES = [
        (LIVESTOCK, "Gia súc"),
        (POULTRY, "Gia cầm"),
        (AQUACULTURE, "Thủy sản"),
        (PERENNIAL_CROPS, "Cây lâu năm"),
        (ANNUAL_CROPS, "Cây hàng năm"),
        (FORESTRY, "Lâm nghiệp"),
        (OTHER, "Khác"),
    ]


class BiologicalAssetStatus:
    """Biological asset status constants."""

    ACTIVE = "active"
    GROWING = "growing"
    HARVESTED = "harvested"
    SOLD = "sold"
    DEAD = "dead"
    WRITE_OFF = "write_off"

    CHOICES = [
        (ACTIVE, "Hoạt động"),
        (GROWING, "Đang nuôi trồng"),
        (HARVESTED, "Đã thu hoạch"),
        (SOLD, "Đã bán"),
        (DEAD, "Chết"),
        (WRITE_OFF, "Xóa sổ"),
    ]
