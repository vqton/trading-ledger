"""
Biological Asset Service - Business logic for TK 215 biological assets.
Circular 99/2025/TT-BTC compliant biological asset management.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any, Tuple

from core.database import db
from core.utils import utc_now


class BiologicalAssetService:
    """Service for managing biological assets (TK 215)."""

    @staticmethod
    def create_asset(
        code: str,
        name: str,
        asset_type: str,
        category: str,
        quantity: Decimal,
        unit: str,
        initial_value: Decimal,
        acquisition_date: date,
        location: str = None,
        description: str = None,
        created_by: int = None,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Create a new biological asset.

        Args:
            code: Asset code
            name: Asset name
            asset_type: Asset type
            category: Asset category
            quantity: Quantity
            unit: Unit of measurement
            initial_value: Initial value
            acquisition_date: Acquisition date
            location: Asset location
            description: Description
            created_by: Creator user ID

        Returns:
            Tuple of (success, result)
        """
        try:
            from models.biological_asset import BiologicalAsset

            if isinstance(acquisition_date, str):
                acquisition_date = datetime.strptime(acquisition_date, "%Y-%m-%d").date()

            asset = BiologicalAsset(
                code=code,
                name=name,
                asset_type=asset_type,
                category=category,
                initial_quantity=quantity,
                current_quantity=quantity,
                unit=unit,
                fair_value_per_unit=initial_value / quantity if quantity else Decimal("0"),
                total_fair_value=initial_value,
                costs_to_sell=Decimal("0"),
                net_value=initial_value,
                acquisition_date=acquisition_date,
                location=location,
                description=description,
                status="owned",
                created_by=created_by or 1,
            )
            db.session.add(asset)
            db.session.commit()
            return True, asset.to_dict()
        except Exception as e:
            db.session.rollback()
            return False, {"error": str(e)}

    @staticmethod
    def update_asset(
        asset_id: int,
        **kwargs,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Update biological asset.

        Args:
            asset_id: Asset ID
            **kwargs: Fields to update

        Returns:
            Tuple of (success, result)
        """
        try:
            from models.biological_asset import BiologicalAsset

            asset = db.session.get(BiologicalAsset, asset_id)
            if not asset:
                return False, {"error": "Asset not found"}

            for key, value in kwargs.items():
                if hasattr(asset, key) and key not in ["id", "code", "created_at"]:
                    setattr(asset, key, value)

            asset.updated_at = utc_now()
            db.session.commit()
            return True, asset.to_dict()
        except Exception as e:
            db.session.rollback()
            return False, {"error": str(e)}

    @staticmethod
    def update_fair_value(
        asset_id: int,
        fair_value: Decimal,
        valuation_date: date = None,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Update fair value of biological asset.

        Args:
            asset_id: Asset ID
            fair_value: New fair value
            valuation_date: Valuation date

        Returns:
            Tuple of (success, result)
        """
        try:
            from models.biological_asset import BiologicalAsset

            asset = db.session.get(BiologicalAsset, asset_id)
            if not asset:
                return False, {"error": "Asset not found"}

            old_fair_value = asset.total_fair_value
            asset.total_fair_value = fair_value
            asset.fair_value_per_unit = fair_value / asset.current_quantity if asset.current_quantity else Decimal("0")
            asset.net_value = fair_value - asset.costs_to_sell
            asset.updated_at = utc_now()

            db.session.commit()
            return True, asset.to_dict()
        except Exception as e:
            db.session.rollback()
            return False, {"error": str(e)}

    @staticmethod
    def record_growth_change(
        asset_id: int,
        quantity_change: Decimal,
        value_change: Decimal,
        description: str = None,
        change_date: date = None,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Record growth or decline change.

        Args:
            asset_id: Asset ID
            quantity_change: Change in quantity
            value_change: Change in value
            description: Change description
            change_date: Change date

        Returns:
            Tuple of (success, result)
        """
        try:
            from models.biological_asset import BiologicalAsset

            asset = db.session.get(BiologicalAsset, asset_id)
            if not asset:
                return False, {"error": "Asset not found"}

            asset.current_quantity = asset.current_quantity + quantity_change
            asset.total_fair_value = asset.total_fair_value + value_change
            asset.fair_value_per_unit = asset.total_fair_value / asset.current_quantity if asset.current_quantity else Decimal("0")
            asset.net_value = asset.total_fair_value - asset.costs_to_sell
            asset.updated_at = utc_now()

            db.session.commit()
            return True, asset.to_dict()
        except Exception as e:
            db.session.rollback()
            return False, {"error": str(e)}

    @staticmethod
    def dispose_asset(
        asset_id: int,
        disposal_type: str,
        disposal_value: Decimal = None,
        disposal_date: date = None,
        buyer: str = None,
        notes: str = None,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Dispose biological asset.

        Args:
            asset_id: Asset ID
            disposal_type: Type (sold, harvested, died, other)
            disposal_value: Disposal value
            disposal_date: Disposal date
            buyer: Buyer name
            notes: Notes

        Returns:
            Tuple of (success, result)
        """
        try:
            from models.biological_asset import BiologicalAsset

            asset = db.session.get(BiologicalAsset, asset_id)
            if not asset:
                return False, {"error": "Asset not found"}

            asset.status = "disposed"
            asset.disposal_type = disposal_type
            asset.disposal_value = disposal_value or Decimal("0")
            asset.disposal_date = disposal_date or date.today()
            asset.buyer = buyer
            asset.notes = notes

            db.session.commit()
            return True, asset.to_dict()
        except Exception as e:
            db.session.rollback()
            return False, {"error": str(e)}

    @staticmethod
    def get_assets(
        status: str = None,
        asset_type: str = None,
        category: str = None,
        is_active: bool = None,
    ) -> List[Dict[str, Any]]:
        """
        Get biological assets with filters.

        Args:
            status: Filter by status
            asset_type: Filter by type
            category: Filter by category
            is_active: Filter by active status

        Returns:
            List of assets
        """
        from models.biological_asset import BiologicalAsset

        query = BiologicalAsset.query

        if status:
            query = query.filter_by(status=status)
        if asset_type:
            query = query.filter_by(asset_type=asset_type)
        if category:
            query = query.filter_by(category=category)
        if is_active is not None:
            active_status = "owned" if is_active else "disposed"
            query = query.filter_by(status=active_status)

        assets = query.order_by(BiologicalAsset.code).all()
        return [a.to_dict() for a in assets]

    @staticmethod
    def get_asset_by_id(asset_id: int) -> Optional[Dict[str, Any]]:
        """Get asset by ID."""
        from models.biological_asset import BiologicalAsset

        asset = db.session.get(BiologicalAsset, asset_id)
        return asset.to_dict() if asset else None

    @staticmethod
    def get_total_value() -> Dict[str, Decimal]:
        """
        Get total value of all biological assets.

        Returns:
            Dictionary with total values
        """
        from models.biological_asset import BiologicalAsset

        assets = BiologicalAsset.query.filter_by(status="owned").all()

        total_initial = sum(a.total_fair_value or Decimal("0") for a in assets)
        total_current = sum(a.total_fair_value or Decimal("0") for a in assets)
        total_fair = sum(a.total_fair_value or Decimal("0") for a in assets)

        return {
            "total_initial_value": total_initial,
            "total_current_value": total_current,
            "total_fair_value": total_fair,
            "asset_count": len(assets),
        }

    @staticmethod
    def get_asset_statistics() -> Dict[str, Any]:
        """
        Get asset statistics.

        Returns:
            Dictionary of statistics
        """
        from models.biological_asset import BiologicalAsset

        total = BiologicalAsset.query.count()
        active = BiologicalAsset.query.filter_by(status="owned").count()
        disposed = BiologicalAsset.query.filter_by(status="disposed").count()

        by_type = {}
        for asset_type in ["consumable", "bearer", "standing_timber"]:
            count = BiologicalAsset.query.filter_by(
                asset_type=asset_type,
                status="owned"
            ).count()
            by_type[asset_type] = count

        return {
            "total_assets": total,
            "active_assets": active,
            "disposed_assets": disposed,
            "by_type": by_type,
        }
