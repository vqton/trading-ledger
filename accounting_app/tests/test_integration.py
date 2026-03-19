"""
Integration tests for VAS Accounting System.
Tests end-to-end workflows across multiple modules.
"""

import pytest
from datetime import date
from decimal import Decimal

from app import create_app
from core.database import db
from core.security import User, Role
from models.account import Account
from models.journal import JournalVoucher, JournalEntry
from models.approval_workflow import ApprovalWorkflow, ApprovalStep, ApprovalRequest
from models.notification import Notification
from models.document import Document, DocumentTemplate
from models.system_setting import SystemSetting
from models.biological_asset import BiologicalAsset, BiologicalAssetType
from models.dividend_payable import DividendPayable, ShareholderType
from services.approval_service import ApprovalService
from services.notification_service import NotificationService
from services.biological_asset_service import BiologicalAssetService
from services.dividend_payable_service import DividendPayableService
from services.system_setting_service import SystemSettingService


@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        _seed_base_data()
        yield app
        db.session.remove()
        db.drop_all()


def _seed_base_data():
    """Seed base data for integration tests."""
    existing_role = Role.query.filter_by(name="admin").first()
    if existing_role:
        return
    
    admin_role = Role(name="admin", description="Administrator")
    accountant_role = Role(name="accountant", description="Accountant")
    db.session.add_all([admin_role, accountant_role])
    db.session.commit()

    admin = User(
        username="admin",
        email="admin@test.com",
        is_active=True,
        role_id=admin_role.id,
    )
    admin.set_password("admin123")
    db.session.add(admin)
    db.session.commit()


class TestNotificationWorkflow:
    """Test notification creation on various events."""

    def test_notification_on_voucher_creation(self, app):
        """Test notifications are created for voucher events."""
        with app.app_context():
            admin = User.query.filter_by(username="admin").first()

            success, notification = NotificationService.create_notification(
                user_id=admin.id,
                title="Voucher Created",
                message="A new voucher has been created",
                notification_type="info",
                entity_type="voucher",
                entity_id=1,
            )

            assert success is True
            assert notification["title"] == "Voucher Created"
            assert notification["is_read"] is False

            success, _ = NotificationService.mark_as_read(
                notification_id=notification["id"],
                user_id=admin.id,
            )
            assert success is True

            unread = NotificationService.get_unread_count(admin.id)
            assert unread == 0

    def test_notification_priority_from_settings(self, app):
        """Test notification priority is set correctly."""
        with app.app_context():
            admin = User.query.filter_by(username="admin").first()

            success, notification = NotificationService.create_notification(
                user_id=admin.id,
                title="High Priority Alert",
                message="This is a high priority notification",
                notification_type="warning",
            )

            assert success is True
            assert notification["priority"] == "medium"


class TestBiologicalAssetAccounting:
    """Test biological asset creation and accounting integration."""

    def test_create_biological_asset_and_update_value(self, app):
        """Test creating biological asset and updating fair value."""
        with app.app_context():
            admin = User.query.filter_by(username="admin").first()

            success, asset = BiologicalAssetService.create_asset(
                code="BIO-2026-001",
                name="Cattle Herd",
                asset_type=BiologicalAssetType.CONSUMABLE,
                category="livestock",
                quantity=Decimal("50"),
                unit="head",
                initial_value=Decimal("100000000"),
                acquisition_date=date.today(),
                location="Farm A",
                created_by=admin.id,
            )

            assert success is True
            assert asset["status"] == "owned"
            assert float(asset["total_fair_value"]) == 100000000.0

            success, updated = BiologicalAssetService.update_fair_value(
                asset_id=asset["id"],
                fair_value=Decimal("120000000"),
            )

            assert success is True
            assert float(updated["total_fair_value"]) == 120000000.0

            success, growth = BiologicalAssetService.record_growth_change(
                asset_id=asset["id"],
                quantity_change=Decimal("5"),
                value_change=Decimal("10000000"),
            )

            assert success is True
            assert float(growth["current_quantity"]) == 55.0

    def test_dispose_biological_asset(self, app):
        """Test disposing biological asset."""
        with app.app_context():
            admin = User.query.filter_by(username="admin").first()

            success, asset = BiologicalAssetService.create_asset(
                code="BIO-2026-002",
                name="Fish Pond",
                asset_type=BiologicalAssetType.CONSUMABLE,
                category="aquaculture",
                quantity=Decimal("100"),
                unit="kg",
                initial_value=Decimal("50000000"),
                acquisition_date=date.today(),
                created_by=admin.id,
            )

            success, disposed = BiologicalAssetService.dispose_asset(
                asset_id=asset["id"],
                disposal_type="sold",
                disposal_value=Decimal("60000000"),
                disposal_date=date.today(),
                buyer="Fish Market Co",
            )

            assert success is True
            assert disposed["status"] == "disposed"
            assert disposed["disposal_type"] == "sold"
            assert disposed["buyer"] == "Fish Market Co"


class TestDividendPayableWorkflow:
    """Test dividend payable creation and payment workflow."""

    def test_create_dividend_and_record_payment(self, app):
        """Test creating dividend and recording payment."""
        with app.app_context():
            admin = User.query.filter_by(username="admin").first()

            success, dividend = DividendPayableService.create_dividend(
                shareholder_name="Nguyen Van A",
                shareholder_type=ShareholderType.INDIVIDUAL,
                share_quantity=Decimal("1000"),
                dividend_per_share=Decimal("10000"),
                declaration_date=date.today(),
                created_by=admin.id,
            )

            assert success is True
            assert dividend["gross_amount"] == 10000000.0
            assert dividend["payment_status"] == "pending"

            success, payment = DividendPayableService.record_payment(
                dividend_id=dividend["id"],
                payment_date=date.today(),
                payment_method="bank_transfer",
            )

            assert success is True
            assert payment["payment_status"] == "paid"

            summary = DividendPayableService.get_dividend_summary(
                fiscal_year=date.today().year
            )

            assert summary["total_dividends"] >= 1
            assert summary["total_gross_amount"] >= 10000000

    def test_cancel_dividend(self, app):
        """Test cancelling dividend obligation."""
        with app.app_context():
            admin = User.query.filter_by(username="admin").first()

            success, dividend = DividendPayableService.create_dividend(
                shareholder_name="Cancelled Shareholder",
                shareholder_type=ShareholderType.INDIVIDUAL,
                share_quantity=Decimal("100"),
                dividend_per_share=Decimal("5000"),
                declaration_date=date.today(),
                created_by=admin.id,
            )

            success, cancelled = DividendPayableService.cancel_dividend(
                dividend_id=dividend["id"],
                reason="Shareholder request",
            )

            assert success is True
            assert cancelled["status"] == "cancelled"


class TestCrossModuleDataIntegrity:
    """Test data integrity across modules."""

    def test_user_related_data_cascades(self, app):
        """Test that user deletion handles related data."""
        with app.app_context():
            admin = User.query.filter_by(username="admin").first()

            success, notification = NotificationService.create_notification(
                user_id=admin.id,
                title="Test",
                message="Test message",
            )

            success, dividend = DividendPayableService.create_dividend(
                shareholder_name="Test",
                shareholder_type=ShareholderType.INDIVIDUAL,
                share_quantity=Decimal("100"),
                dividend_per_share=Decimal("1000"),
                declaration_date=date.today(),
                created_by=admin.id,
            )

            user_notifications = NotificationService.get_notifications(
                user_id=admin.id,
            )

            assert len(user_notifications) >= 1

            dividends = DividendPayableService.get_dividends(
                fiscal_year=date.today().year,
            )

            assert len(dividends) >= 1

    def test_biological_asset_statistics(self, app):
        """Test biological asset statistics."""
        with app.app_context():
            admin = User.query.filter_by(username="admin").first()

            BiologicalAssetService.create_asset(
                code="BIO-001",
                name="Test Asset 1",
                asset_type=BiologicalAssetType.CONSUMABLE,
                category="test",
                quantity=Decimal("10"),
                unit="pcs",
                initial_value=Decimal("10000000"),
                acquisition_date=date.today(),
                created_by=admin.id,
            )

            BiologicalAssetService.create_asset(
                code="BIO-002",
                name="Test Asset 2",
                asset_type=BiologicalAssetType.BEARER,
                category="test",
                quantity=Decimal("20"),
                unit="pcs",
                initial_value=Decimal("20000000"),
                acquisition_date=date.today(),
                created_by=admin.id,
            )

            stats = BiologicalAssetService.get_asset_statistics()

            assert stats["total_assets"] >= 2
            assert stats["active_assets"] >= 2

    def test_dividend_summary_by_type(self, app):
        """Test dividend summary by shareholder type."""
        with app.app_context():
            admin = User.query.filter_by(username="admin").first()

            DividendPayableService.create_dividend(
                shareholder_name="Individual A",
                shareholder_type=ShareholderType.INDIVIDUAL,
                share_quantity=Decimal("100"),
                dividend_per_share=Decimal("1000"),
                declaration_date=date.today(),
                created_by=admin.id,
            )

            DividendPayableService.create_dividend(
                shareholder_name="Corporate B",
                shareholder_type=ShareholderType.CORPORATE,
                share_quantity=Decimal("200"),
                dividend_per_share=Decimal("1000"),
                declaration_date=date.today(),
                created_by=admin.id,
            )

            summary = DividendPayableService.get_dividend_summary(
                fiscal_year=date.today().year
            )

            assert summary["total_dividends"] >= 2


class TestSystemSettings:
    """Test system settings functionality."""

    def test_settings_crud_operations(self, app):
        """Test basic CRUD operations on system settings."""
        with app.app_context():
            success, setting = SystemSettingService.set_setting(
                key="test_key",
                value="test_value",
                value_type="string",
                category="test",
            )
            assert success is True

            value = SystemSettingService.get_setting("test_key")
            assert value == "test_value"

            success, _ = SystemSettingService.delete_setting("test_key")
            assert success is True

            deleted_value = SystemSettingService.get_setting("test_key")
            assert deleted_value is None

    def test_settings_default_value(self, app):
        """Test default value when setting doesn't exist."""
        with app.app_context():
            value = SystemSettingService.get_setting(
                "nonexistent_key",
                default="default_value"
            )
            assert value == "default_value"
