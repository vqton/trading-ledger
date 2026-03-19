from datetime import datetime
from typing import Optional, Any, List

from core.database import db
from core.utils import utc_now


class SystemSetting(db.Model):
    """System Setting model for application configuration."""

    __tablename__ = "system_settings"

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    value = db.Column(db.Text, nullable=True)
    value_type = db.Column(db.String(20), default="string")
    category = db.Column(db.String(50), nullable=True, index=True)
    description = db.Column(db.String(500), nullable=True)
    is_encrypted = db.Column(db.Boolean, default=False, nullable=False)
    is_system = db.Column(db.Boolean, default=False, nullable=False)
    modified_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    modified_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)

    modifier = db.relationship("User", backref="modified_settings")

    __table_args__ = (
        db.Index("ix_setting_category", "category"),
    )

    def __repr__(self) -> str:
        return f"<SystemSetting {self.key}>"

    def get_typed_value(self) -> Any:
        """Get value with proper type conversion."""
        if self.value is None:
            return None

        if self.value_type == "boolean":
            return self.value.lower() in ("true", "1", "yes")
        elif self.value_type == "integer":
            return int(self.value)
        elif self.value_type == "float":
            return float(self.value)
        elif self.value_type == "json":
            import json
            return json.loads(self.value)
        else:
            return self.value

    def set_typed_value(self, value: Any) -> None:
        """Set value with proper type conversion."""
        if value is None:
            self.value = None
            self.value_type = "string"
        elif isinstance(value, bool):
            self.value = str(value).lower()
            self.value_type = "boolean"
        elif isinstance(value, int):
            self.value = str(value)
            self.value_type = "integer"
        elif isinstance(value, float):
            self.value = str(value)
            self.value_type = "float"
        elif isinstance(value, dict) or isinstance(value, list):
            import json
            self.value = json.dumps(value)
            self.value_type = "json"
        else:
            self.value = str(value)
            self.value_type = "string"

    def update_value(self, new_value: Any, user_id: int = None) -> None:
        """Update setting value."""
        self.set_typed_value(new_value)
        self.modified_by = user_id
        self.modified_at = utc_now()
        db.session.commit()

    @classmethod
    def get_value(cls, key: str, default: Any = None) -> Any:
        """Get setting value by key."""
        setting = cls.query.filter_by(key=key).first()
        if setting:
            return setting.get_typed_value()
        return default

    @classmethod
    def set_value(cls, key: str, value: Any, category: str = None, description: str = None, user_id: int = None) -> "SystemSetting":
        """Set or create setting value."""
        setting = cls.query.filter_by(key=key).first()
        if not setting:
            setting = cls(
                key=key,
                category=category,
                description=description,
            )
            db.session.add(setting)
        setting.set_typed_value(value)
        setting.modified_by = user_id
        setting.modified_at = utc_now()
        db.session.commit()
        return setting

    @classmethod
    def get_by_category(cls, category: str) -> List["SystemSetting"]:
        """Get all settings in a category."""
        return cls.query.filter_by(category=category).order_by(cls.key).all()

    @classmethod
    def get_all_settings_dict(cls, include_system: bool = True) -> dict:
        """Get all settings as dictionary."""
        query = cls.query
        if not include_system:
            query = query.filter_by(is_system=False)
        settings = query.all()
        return {s.key: s.get_typed_value() for s in settings}

    def to_dict(self, include_value: bool = True) -> dict:
        """Convert setting to dictionary."""
        data = {
            "id": self.id,
            "key": self.key,
            "value": self.get_typed_value() if include_value and not self.is_encrypted else None,
            "value_type": self.value_type,
            "category": self.category,
            "description": self.description,
            "is_encrypted": self.is_encrypted,
            "is_system": self.is_system,
            "modified_by": self.modified_by,
            "modified_at": self.modified_at.isoformat() if self.modified_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if self.is_encrypted and include_value:
            data["value"] = "********"
        return data


class SettingCategory:
    """Setting category constants."""

    GENERAL = "general"
    ACCOUNTING = "accounting"
    TAX = "tax"
    EMAIL = "email"
    SECURITY = "security"
    INTEGRATION = "integration"
    REPORTING = "reporting"

    CHOICES = [
        (GENERAL, "Chung"),
        (ACCOUNTING, "Kế toán"),
        (TAX, "Thuế"),
        (EMAIL, "Email"),
        (SECURITY, "Bảo mật"),
        (INTEGRATION, "Tích hợp"),
        (REPORTING, "Báo cáo"),
    ]


class SettingKey:
    """Common setting keys."""

    COMPANY_NAME = "company_name"
    COMPANY_TAX_CODE = "company_tax_code"
    COMPANY_ADDRESS = "company_address"
    COMPANY_PHONE = "company_phone"
    COMPANY_EMAIL = "company_email"

    FISCAL_YEAR_START = "fiscal_year_start"
    CURRENCY_CODE = "currency_code"
    DECIMAL_PLACES = "decimal_places"

    VAT_DEFAULT_RATE = "vat_default_rate"
    CIT_RATE = "cit_rate"
    PIT_RATE = "pit_rate"

    AUTO_POST_VOUCHER = "auto_post_voucher"
    REQUIRE_APPROVAL = "require_approval"
    APPROVAL_AMOUNT_THRESHOLD = "approval_amount_threshold"

    EMAIL_SMTP_HOST = "email_smtp_host"
    EMAIL_SMTP_PORT = "email_smtp_port"
    EMAIL_FROM_ADDRESS = "email_from_address"

    SESSION_TIMEOUT_MINUTES = "session_timeout_minutes"
    PASSWORD_MIN_LENGTH = "password_min_length"
    MAX_LOGIN_ATTEMPTS = "max_login_attempts"

    DEFAULT_WAREHOUSE = "default_warehouse"
    DEFAULT_BANK_ACCOUNT = "default_bank_account"
