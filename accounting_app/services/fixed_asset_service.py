"""Fixed Asset Service - Acquisition, depreciation, disposal."""

from datetime import date, datetime
from decimal import Decimal
from typing import Dict, List, Optional

from core.database import db
from models.fixed_asset import (
    AssetStatus,
    DepreciationEntry,
    DepreciationMethod,
    FixedAsset,
    FixedAssetCategory,
)
from models.journal import JournalRepository, JournalVoucher, VoucherType


class FixedAssetService:
    """Service for fixed asset operations."""

    @staticmethod
    def get_all_assets() -> List[FixedAsset]:
        """Get all fixed assets."""
        return FixedAsset.query.filter_by(is_active=True).all()

    @staticmethod
    def get_asset(asset_id: int) -> Optional[FixedAsset]:
        """Get fixed asset by ID."""
        return db.session.get(FixedAsset, asset_id)

    @staticmethod
    def get_asset_by_code(code: str) -> Optional[FixedAsset]:
        """Get fixed asset by code."""
        return FixedAsset.query.filter_by(code=code).first()

    @staticmethod
    def get_all_categories() -> List[FixedAssetCategory]:
        """Get all asset categories."""
        return FixedAssetCategory.query.filter_by(is_active=True).all()

    @staticmethod
    def create_asset(asset_data: Dict, user_id: int) -> FixedAsset:
        """Create new fixed asset."""
        existing = FixedAsset.query.filter_by(code=asset_data["code"]).first()
        if existing:
            raise ValueError(f"Mã tài sản {asset_data['code']} đã tồn tại")

        asset = FixedAsset(
            code=asset_data["code"],
            name=asset_data["name"],
            category_id=asset_data["category_id"],
            purchase_date=asset_data["purchase_date"],
            useful_life_years=asset_data["useful_life_years"],
            original_cost=asset_data["original_cost"],
            residual_value=asset_data.get("residual_value", Decimal("0")),
            depreciation_method=asset_data.get("depreciation_method", DepreciationMethod.STRAIGHT_LINE),
            depreciation_rate=asset_data.get("depreciation_rate", Decimal("0")),
            location=asset_data.get("location"),
            serial_number=asset_data.get("serial_number"),
            description=asset_data.get("description"),
            account_asset_id=asset_data.get("account_asset_id"),
            account_depreciation_id=asset_data.get("account_depreciation_id"),
            status=AssetStatus.IN_USE,
            created_by=user_id,
        )
        
        asset.net_book_value = asset.original_cost - asset.accumulated_depreciation
        
        db.session.add(asset)
        db.session.commit()
        return asset

    @staticmethod
    def update_asset(asset_id: int, asset_data: Dict) -> FixedAsset:
        """Update fixed asset."""
        asset = db.session.get(FixedAsset, asset_id)
        if not asset:
            raise ValueError(f"Asset {asset_id} not found")

        for key, value in asset_data.items():
            if hasattr(asset, key):
                setattr(asset, key, value)

        asset.update_net_book_value()
        db.session.commit()
        return asset

    @staticmethod
    def calculate_depreciation(asset_id: int, period_date: date) -> Decimal:
        """Calculate depreciation for a specific period."""
        asset = db.session.get(FixedAsset, asset_id)
        if not asset:
            raise ValueError(f"Asset {asset_id} not found")

        if asset.status != AssetStatus.IN_USE:
            return Decimal("0")

        return asset.calculate_depreciation()

    @staticmethod
    def calculate_monthly_depreciation(asset_id: int) -> Decimal:
        """Calculate monthly depreciation."""
        annual_depr = FixedAssetService.calculate_depreciation(asset_id, date.today())
        return annual_depr / 12

    @staticmethod
    def calculate_accumulated_depreciation(
        asset_id: int,
        year: int,
        month: int,
    ) -> Decimal:
        """Calculate accumulated depreciation up to a period."""
        entries = DepreciationEntry.query.filter(
            DepreciationEntry.asset_id == asset_id,
            (DepreciationEntry.period_year < year) | (
                (DepreciationEntry.period_year == year) &
                (DepreciationEntry.period_month <= month)
            ),
        ).all()
        
        return sum(e.depreciation_amount for e in entries)

    @staticmethod
    def record_depreciation(
        asset_id: int,
        period_year: int,
        period_month: int,
        user_id: int,
    ) -> DepreciationEntry:
        """Record depreciation for a period."""
        asset = db.session.get(FixedAsset, asset_id)
        if not asset:
            raise ValueError(f"Asset {asset_id} not found")

        existing = DepreciationEntry.query.filter_by(
            asset_id=asset_id,
            period_year=period_year,
            period_month=period_month,
        ).first()
        
        if existing:
            raise ValueError(
                f"Khấu hao kỳ {period_month}/{period_year} đã được ghi nhận"
            )

        depreciation = asset.calculate_depreciation() / 12
        
        entry = DepreciationEntry(
            asset_id=asset_id,
            period_year=period_year,
            period_month=period_month,
            depreciation_amount=depreciation,
            accumulated_before=asset.accumulated_depreciation,
            accumulated_after=asset.accumulated_depreciation + depreciation,
            created_by=user_id,
        )

        asset.accumulated_depreciation += depreciation
        asset.update_net_book_value()

        db.session.add(entry)
        db.session.commit()
        return entry

    @staticmethod
    def record_depreciation_batch(
        asset_ids: List[int],
        period_year: int,
        period_month: int,
        user_id: int,
    ) -> List[DepreciationEntry]:
        """Record depreciation for multiple assets."""
        entries = []
        for asset_id in asset_ids:
            try:
                entry = FixedAssetService.record_depreciation(
                    asset_id, period_year, period_month, user_id
                )
                entries.append(entry)
            except ValueError:
                pass
        
        return entries

    @staticmethod
    def dispose_asset(
        asset_id: int,
        disposal_date: date,
        disposal_proceeds: Decimal,
        disposal_cost: Decimal,
        user_id: int,
    ) -> Dict:
        """Dispose fixed asset."""
        asset = db.session.get(FixedAsset, asset_id)
        if not asset:
            raise ValueError(f"Asset {asset_id} not found")

        if asset.status == AssetStatus.DISPOSED:
            raise ValueError("Tài sản đã được thanh lý")

        gain_loss = disposal_proceeds - disposal_cost - asset.net_book_value

        asset.status = AssetStatus.DISPOSED
        asset.accumulated_depreciation = asset.original_cost
        asset.net_book_value = Decimal("0")

        db.session.commit()

        return {
            "asset_id": asset_id,
            "disposal_date": disposal_date,
            "original_cost": asset.original_cost,
            "accumulated_depreciation": asset.accumulated_depreciation,
            "net_book_value": asset.net_book_value,
            "disposal_proceeds": disposal_proceeds,
            "disposal_cost": disposal_cost,
            "gain_loss": gain_loss,
        }

    @staticmethod
    def get_depreciation_schedule(asset_id: int) -> List[Dict]:
        """Get depreciation schedule for an asset."""
        asset = db.session.get(FixedAsset, asset_id)
        if not asset:
            return []

        schedule = []
        current_date = asset.purchase_date
        accumulated = Decimal("0")

        for year in range(asset.useful_life_years):
            annual_depr = asset.calculate_depreciation()
            
            for month in range(1, 13):
                if current_date.year > datetime.now().year or (
                    current_date.year == datetime.now().year and 
                    current_date.month > datetime.now().month
                ):
                    break
                    
                month_depr = annual_depr / 12
                accumulated += month_depr
                
                schedule.append({
                    "year": current_date.year,
                    "month": current_date.month,
                    "depreciation": month_depr,
                    "accumulated": accumulated,
                    "book_value": asset.original_cost - accumulated,
                })
                
                current_date = current_date.replace(month=current_date.month + 1)
                if current_date.month > 12:
                    current_date = current_date.replace(year=current_date.year + 1, month=1)

        return schedule

    @staticmethod
    def get_fixed_asset_report(as_of_date: date) -> List[Dict]:
        """Generate fixed asset report."""
        assets = FixedAsset.query.filter_by(is_active=True).all()
        
        report = []
        for asset in assets:
            report.append({
                "code": asset.code,
                "name": asset.name,
                "category": asset.category.name if asset.category else "",
                "purchase_date": asset.purchase_date,
                "original_cost": asset.original_cost,
                "accumulated_depreciation": asset.accumulated_depreciation,
                "net_book_value": asset.net_book_value,
                "status": asset.status,
                "useful_life": asset.useful_life_years,
            })
        
        return report
