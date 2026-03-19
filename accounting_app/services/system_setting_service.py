"""
System Setting Service - Business logic for system configuration.
Handles application settings and configuration management.
"""

import json
from typing import Optional, List, Dict, Any, Tuple

from core.database import db
from core.utils import utc_now


class SystemSettingService:
    """Service for managing system settings."""

    @staticmethod
    def get_setting(key: str, default: Any = None) -> Any:
        """
        Get a setting value.

        Args:
            key: Setting key
            default: Default value if not found

        Returns:
            Setting value or default
        """
        from models.system_setting import SystemSetting

        setting = SystemSetting.query.filter_by(key=key).first()
        if not setting:
            return default

        if setting.value_type == "int":
            return int(setting.value) if setting.value else default
        elif setting.value_type == "float":
            return float(setting.value) if setting.value else default
        elif setting.value_type == "bool":
            return setting.value == "true" if setting.value else default
        elif setting.value_type == "json":
            return json.loads(setting.value) if setting.value else default
        else:
            return setting.value if setting.value else default

    @staticmethod
    def set_setting(
        key: str,
        value: Any,
        value_type: str = "string",
        category: str = "general",
        description: str = None,
        is_encrypted: bool = False,
        modified_by: int = None,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Set a setting value.

        Args:
            key: Setting key
            value: Setting value
            value_type: Value type (string, int, float, bool, json)
            category: Setting category
            description: Setting description
            is_encrypted: Whether to encrypt the value
            updated_by: User updating the setting

        Returns:
            Tuple of (success, result)
        """
        try:
            from models.system_setting import SystemSetting

            setting = SystemSetting.query.filter_by(key=key).first()

            if value_type == "bool":
                str_value = "true" if value else "false"
            elif value_type == "json":
                str_value = json.dumps(value)
            else:
                str_value = str(value)

            if setting:
                setting.value = str_value
                setting.value_type = value_type
                setting.category = category
                setting.description = description or setting.description
                setting.is_encrypted = is_encrypted
                setting.modified_by = modified_by
                setting.modified_at = utc_now()
            else:
                setting = SystemSetting(
                    key=key,
                    value=str_value,
                    value_type=value_type,
                    category=category,
                    description=description,
                    is_encrypted=is_encrypted,
                    modified_by=modified_by,
                )
                db.session.add(setting)

            db.session.commit()
            return True, setting.to_dict()
        except Exception as e:
            db.session.rollback()
            return False, {"error": str(e)}

    @staticmethod
    def delete_setting(key: str) -> Tuple[bool, str]:
        """
        Delete a setting.

        Args:
            key: Setting key

        Returns:
            Tuple of (success, message)
        """
        try:
            from models.system_setting import SystemSetting

            setting = SystemSetting.query.filter_by(key=key).first()
            if not setting:
                return False, "Setting not found"

            if setting.is_system:
                return False, "Cannot delete system setting"

            db.session.delete(setting)
            db.session.commit()

            return True, "Setting deleted successfully"
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def get_settings_by_category(category: str) -> Dict[str, Any]:
        """
        Get all settings in a category.

        Args:
            category: Setting category

        Returns:
            Dictionary of settings
        """
        from models.system_setting import SystemSetting

        settings = SystemSetting.query.filter_by(category=category).all()
        result = {}
        for setting in settings:
            if setting.value_type == "int":
                result[setting.key] = int(setting.value) if setting.value else None
            elif setting.value_type == "float":
                result[setting.key] = float(setting.value) if setting.value else None
            elif setting.value_type == "bool":
                result[setting.key] = setting.value == "true" if setting.value else False
            elif setting.value_type == "json":
                result[setting.key] = json.loads(setting.value) if setting.value else None
            else:
                result[setting.key] = setting.value
        return result

    @staticmethod
    def get_all_settings() -> List[Dict[str, Any]]:
        """
        Get all settings.

        Returns:
            List of setting dictionaries
        """
        from models.system_setting import SystemSetting

        settings = SystemSetting.query.all()
        return [s.to_dict() for s in settings]

    @staticmethod
    def init_default_settings() -> None:
        """Initialize default system settings."""
        defaults = [
            ("company_name", "My Company", "string", "company"),
            ("company_tax_id", "", "string", "company", "Company Tax ID"),
            ("company_address", "", "string", "company"),
            ("company_phone", "", "string", "company"),
            ("company_email", "", "string", "company"),
            ("fiscal_year_start", 1, "int", "accounting", "Month number (1-12)"),
            ("currency_code", "VND", "string", "accounting"),
            ("decimal_places", 2, "int", "accounting"),
            ("voucher_prefix", "JV", "string", "accounting", "Journal voucher prefix"),
            ("auto_post_vouchers", "false", "bool", "accounting"),
            ("require_approval", "true", "bool", "approval"),
            ("approval_threshold", "50000000", "int", "approval", "Auto-approve below this amount"),
            ("session_timeout", 3600, "int", "security", "Session timeout in seconds"),
            ("max_login_attempts", 5, "int", "security"),
            ("password_min_length", 8, "int", "security"),
            ("backup_enabled", "true", "bool", "backup"),
            ("backup_retention_days", 30, "int", "backup"),
            ("auto_backup_frequency", "daily", "string", "backup"),
        ]

        for key, value, value_type, category, *desc in defaults:
            description = desc[0] if desc else None
            existing = SystemSettingService.get_setting(key)
            if existing is None:
                SystemSettingService.set_setting(
                    key=key,
                    value=value,
                    value_type=value_type,
                    category=category,
                    description=description,
                )

    @staticmethod
    def get_company_info() -> Dict[str, Any]:
        """Get company information settings."""
        return SystemSettingService.get_settings_by_category("company")

    @staticmethod
    def get_accounting_settings() -> Dict[str, Any]:
        """Get accounting settings."""
        return SystemSettingService.get_settings_by_category("accounting")

    @staticmethod
    def get_security_settings() -> Dict[str, Any]:
        """Get security settings."""
        return SystemSettingService.get_settings_by_category("security")
