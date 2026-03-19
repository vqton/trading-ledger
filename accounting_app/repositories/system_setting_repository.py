from typing import List, Optional, Tuple, Any

from core.database import db
from core.utils import utc_now
from models.system_setting import SystemSetting, SettingCategory, SettingKey


class SystemSettingRepository:
    """Repository for SystemSetting."""

    @staticmethod
    def get_setting_by_id(setting_id: int) -> Optional[SystemSetting]:
        """Get setting by ID."""
        return db.session.get(SystemSetting, setting_id)

    @staticmethod
    def get_setting_by_key(key: str) -> Optional[SystemSetting]:
        """Get setting by key."""
        return SystemSetting.query.filter_by(key=key).first()

    @staticmethod
    def get_settings(page: int = 1, per_page: int = 20, category: str = None, is_system: bool = None) -> Tuple[List[SystemSetting], int]:
        """Get paginated settings."""
        query = SystemSetting.query

        if category:
            query = query.filter(SystemSetting.category == category)
        if is_system is not None:
            query = query.filter(SystemSetting.is_system == is_system)

        query = query.order_by(SystemSetting.category, SystemSetting.key)
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        return pagination.items, pagination.total

    @staticmethod
    def create_or_update_setting(key: str, value: Any, category: str = None, description: str = None, user_id: int = None, is_encrypted: bool = False, is_system: bool = False) -> SystemSetting:
        """Create or update a setting."""
        setting = SystemSetting.query.filter_by(key=key).first()
        if not setting:
            setting = SystemSetting(
                key=key,
                category=category,
                description=description,
                is_encrypted=is_encrypted,
                is_system=is_system,
            )
            db.session.add(setting)

        setting.set_typed_value(value)
        setting.modified_by = user_id
        setting.modified_at = utc_now()
        db.session.commit()
        return setting

    @staticmethod
    def delete_setting(key: str) -> bool:
        """Delete a setting."""
        setting = SystemSetting.query.filter_by(key=key).first()
        if setting and not setting.is_system:
            db.session.delete(setting)
            db.session.commit()
            return True
        return False

    @staticmethod
    def get_by_category(category: str) -> List[SystemSetting]:
        """Get all settings in a category."""
        return SystemSetting.get_by_category(category)

    @staticmethod
    def get_all_settings_dict(include_system: bool = True) -> dict:
        """Get all settings as dictionary."""
        return SystemSetting.get_all_settings_dict(include_system)

    @staticmethod
    def initialize_default_settings(user_id: int = None) -> None:
        """Initialize default system settings."""
        defaults = [
            (SettingKey.FISCAL_YEAR_START, 1, SettingCategory.ACCOUNTING, "Tháng bắt đầu năm tài chính"),
            (SettingKey.CURRENCY_CODE, "VND", SettingCategory.ACCOUNTING, "Mã tiền tệ mặc định"),
            (SettingKey.DECIMAL_PLACES, 2, SettingCategory.ACCOUNTING, "Số thập phân"),
            (SettingKey.VAT_DEFAULT_RATE, 0.10, SettingCategory.TAX, "Thuế suất VAT mặc định"),
            (SettingKey.CIT_RATE, 0.20, SettingCategory.TAX, "Thuế suất TNDN mặc định"),
            (SettingKey.PIT_RATE, 0.10, SettingCategory.TAX, "Thuế suất TNCN mặc định"),
            (SettingKey.SESSION_TIMEOUT_MINUTES, 60, SettingCategory.SECURITY, "Thời gian hết phiên (phút)"),
            (SettingKey.PASSWORD_MIN_LENGTH, 8, SettingCategory.SECURITY, "Độ dài mật khẩu tối thiểu"),
            (SettingKey.MAX_LOGIN_ATTEMPTS, 5, SettingCategory.SECURITY, "Số lần đăng nhập tối đa"),
            (SettingKey.REQUIRE_APPROVAL, True, SettingCategory.GENERAL, "Yêu cầu phê duyệt"),
            (SettingKey.APPROVAL_AMOUNT_THRESHOLD, 10000000, SettingCategory.GENERAL, "Ngưỡng phê duyệt"),
        ]

        for key, value, category, description in defaults:
            SystemSettingRepository.create_or_update_setting(
                key=key,
                value=value,
                category=category,
                description=description,
                user_id=user_id,
            )
