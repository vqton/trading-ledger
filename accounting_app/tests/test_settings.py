"""
Tests for System Setting Service - Configuration management.
"""

import pytest

from app import create_app
from core.database import db
from services.system_setting_service import SystemSettingService
from models.system_setting import SystemSetting


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


class TestSystemSetting:
    """Tests for system settings."""

    def test_set_and_get_string_setting(self, app):
        """Test setting and getting string value."""
        with app.app_context():
            SystemSettingService.set_setting(
                key="test_string",
                value="Hello World",
                value_type="string",
                category="test",
            )

            value = SystemSettingService.get_setting("test_string")
            assert value == "Hello World"

    def test_set_and_get_int_setting(self, app):
        """Test setting and getting integer value."""
        with app.app_context():
            SystemSettingService.set_setting(
                key="test_int",
                value=42,
                value_type="int",
                category="test",
            )

            value = SystemSettingService.get_setting("test_int")
            assert value == 42

    def test_set_and_get_bool_setting(self, app):
        """Test setting and getting boolean value."""
        with app.app_context():
            SystemSettingService.set_setting(
                key="test_bool",
                value=True,
                value_type="bool",
                category="test",
            )

            value = SystemSettingService.get_setting("test_bool")
            assert value is True

    def test_get_default_value(self, app):
        """Test getting default value for non-existent setting."""
        with app.app_context():
            value = SystemSettingService.get_setting("nonexistent", default="default")
            assert value == "default"

    def test_delete_setting(self, app):
        """Test deleting a setting."""
        with app.app_context():
            SystemSettingService.set_setting(
                key="to_delete",
                value="test",
                category="test",
            )

            success, message = SystemSettingService.delete_setting("to_delete")
            assert success is True

    def test_get_settings_by_category(self, app):
        """Test getting settings by category."""
        with app.app_context():
            SystemSettingService.set_setting("cat_key1", "value1", "string", "my_category")
            SystemSettingService.set_setting("cat_key2", "value2", "string", "my_category")

            settings = SystemSettingService.get_settings_by_category("my_category")

            assert "cat_key1" in settings
            assert "cat_key2" in settings


class TestDefaultSettings:
    """Tests for default settings initialization."""

    def test_init_default_settings(self, app):
        """Test initializing default settings."""
        with app.app_context():
            SystemSettingService.init_default_settings()

            company_name = SystemSettingService.get_setting("company_name")
            assert company_name == "My Company"

            currency = SystemSettingService.get_setting("currency_code")
            assert currency == "VND"

    def test_get_company_info(self, app):
        """Test getting company information."""
        with app.app_context():
            SystemSettingService.set_setting("company_name", "Test Corp", "string", "company")
            SystemSettingService.set_setting("company_tax_id", "0123456789", "string", "company")

            company = SystemSettingService.get_company_info()

            assert company["company_name"] == "Test Corp"
            assert company["company_tax_id"] == "0123456789"

    def test_get_accounting_settings(self, app):
        """Test getting accounting settings."""
        with app.app_context():
            SystemSettingService.init_default_settings()

            settings = SystemSettingService.get_accounting_settings()

            assert "fiscal_year_start" in settings
            assert "currency_code" in settings
