"""
Tests for Biological Asset Service - TK 215 biological assets.
Circular 99/2025/TT-BTC compliant tests.
"""

import pytest
from datetime import date
from decimal import Decimal

from app import create_app
from core.database import db
from services.biological_asset_service import BiologicalAssetService
from models.biological_asset import (
    BiologicalAsset,
    BiologicalAssetType,
    BiologicalAssetStatus,
)


@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


class TestBiologicalAsset:
    """Tests for biological asset management."""

    def test_create_asset(self, app):
        """Test creating a biological asset."""
        with app.app_context():
            success, result = BiologicalAssetService.create_asset(
                code="BA-001",
                name="Cattle Herd A",
                asset_type=BiologicalAssetType.CONSUMABLE,
                category="livestock",
                quantity=Decimal("50"),
                unit="head",
                initial_value=Decimal("50000000"),
                acquisition_date=date.today(),
                location="Farm A",
                created_by=1,
            )

            assert success is True
            assert result["code"] == "BA-001"
            assert result["current_quantity"] == 50.0
            assert result["status"] == "owned"

    def test_update_fair_value(self, app):
        """Test updating fair value."""
        with app.app_context():
            success, asset = BiologicalAssetService.create_asset(
                code="BA-002",
                name="Tree Plantation B",
                asset_type=BiologicalAssetType.BEARER,
                category="forestry",
                quantity=Decimal("100"),
                unit="tree",
                initial_value=Decimal("100000000"),
                acquisition_date=date.today(),
                created_by=1,
            )

            new_fair_value = Decimal("120000000")
            success, result = BiologicalAssetService.update_fair_value(
                asset_id=asset["id"],
                fair_value=new_fair_value,
            )

            assert success is True
            assert result["total_fair_value"] == 120000000
            assert result["total_fair_value"] == 120000000

    def test_record_growth_change(self, app):
        """Test recording growth change."""
        with app.app_context():
            success, asset = BiologicalAssetService.create_asset(
                code="BA-003",
                name="Fish Pond C",
                asset_type=BiologicalAssetType.CONSUMABLE,
                category="aquaculture",
                quantity=Decimal("1000"),
                unit="kg",
                initial_value=Decimal("20000000"),
                acquisition_date=date.today(),
                created_by=1,
            )

            success, result = BiologicalAssetService.record_growth_change(
                asset_id=asset["id"],
                quantity_change=Decimal("200"),
                value_change=Decimal("4000000"),
            )

            assert success is True
            assert result["current_quantity"] == 1200.0

    def test_dispose_asset(self, app):
        """Test disposing biological asset."""
        with app.app_context():
            success, asset = BiologicalAssetService.create_asset(
                code="BA-004",
                name="Disposed Herd",
                asset_type=BiologicalAssetType.CONSUMABLE,
                category="livestock",
                quantity=Decimal("20"),
                unit="head",
                initial_value=Decimal("20000000"),
                acquisition_date=date.today(),
                created_by=1,
            )

            success, result = BiologicalAssetService.dispose_asset(
                asset_id=asset["id"],
                disposal_type="sold",
                disposal_value=Decimal("25000000"),
                disposal_date=date.today(),
                buyer="Meat Company",
            )

            assert success is True
            assert result["status"] == "disposed"
            assert result["disposal_type"] == "sold"


class TestBiologicalAssetQueries:
    """Tests for biological asset queries."""

    def test_get_assets_by_type(self, app):
        """Test getting assets by type."""
        with app.app_context():
            BiologicalAssetService.create_asset(
                code="BA-T1",
                name="Type 1 Asset",
                asset_type=BiologicalAssetType.CONSUMABLE,
                category="test",
                quantity=Decimal("10"),
                unit="unit",
                initial_value=Decimal("100000"),
                acquisition_date=date.today(),
                created_by=1,
            )

            assets = BiologicalAssetService.get_assets(asset_type=BiologicalAssetType.CONSUMABLE)

            assert len(assets) >= 1
            for asset in assets:
                assert asset["asset_type"] == BiologicalAssetType.CONSUMABLE

    def test_get_total_value(self, app):
        """Test getting total asset value."""
        with app.app_context():
            BiologicalAssetService.create_asset(
                code="BA-TV1",
                name="Total Value 1",
                asset_type=BiologicalAssetType.BEARER,
                category="test",
                quantity=Decimal("5"),
                unit="unit",
                initial_value=Decimal("10000000"),
                acquisition_date=date.today(),
                created_by=1,
            )

            totals = BiologicalAssetService.get_total_value()

            assert "total_initial_value" in totals
            assert "total_current_value" in totals
            assert "total_fair_value" in totals
            assert totals["total_initial_value"] == 10000000


class TestBiologicalAssetStatistics:
    """Tests for biological asset statistics."""

    def test_get_asset_statistics(self, app):
        """Test getting asset statistics."""
        with app.app_context():
            BiologicalAssetService.create_asset(
                code="BA-ST1",
                name="Statistics Test 1",
                asset_type=BiologicalAssetType.CONSUMABLE,
                category="test",
                quantity=Decimal("5"),
                unit="unit",
                initial_value=Decimal("5000000"),
                acquisition_date=date.today(),
                created_by=1,
            )

            stats = BiologicalAssetService.get_asset_statistics()

            assert "total_assets" in stats
            assert "active_assets" in stats
            assert "by_type" in stats
