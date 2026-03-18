from datetime import datetime
from typing import Optional

from core.database import db
from core.utils import utc_now


class AuditLog(db.Model):
    """Audit Log model for tracking all system actions."""

    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    action = db.Column(db.String(50), nullable=False, index=True)
    entity = db.Column(db.String(50), nullable=False, index=True)
    entity_id = db.Column(db.Integer, nullable=True, index=True)
    old_value = db.Column(db.Text, nullable=True)
    new_value = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    timestamp = db.Column(db.DateTime, default=utc_now, nullable=False, index=True)

    user = db.relationship("User", backref="audit_logs")

    __table_args__ = (
        db.Index("ix_audit_entity", "entity", "entity_id"),
        db.Index("ix_audit_user_action", "user_id", "action"),
    )

    def __repr__(self) -> str:
        return f"<AuditLog {self.action} on {self.entity}:{self.entity_id}>"

    @classmethod
    def log(
        cls,
        action: str,
        entity: str,
        entity_id: Optional[int] = None,
        user_id: Optional[int] = None,
        old_value: Optional[dict] = None,
        new_value: Optional[dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> "AuditLog":
        """Create an audit log entry."""
        import json

        entry = cls(
            user_id=user_id,
            action=action,
            entity=entity,
            entity_id=entity_id,
            old_value=json.dumps(old_value) if old_value else None,
            new_value=json.dumps(new_value) if new_value else None,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        db.session.add(entry)
        db.session.commit()
        return entry


class AuditAction:
    """Audit action constants."""

    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    POST = "post"
    UNPOST = "unpost"
    LOCK = "lock"
    UNLOCK = "unlock"
    CANCEL = "cancel"


class AuditEntity:
    """Audit entity constants."""

    USER = "user"
    ROLE = "role"
    ACCOUNT = "account"
    JOURNAL_VOUCHER = "journal_voucher"
    JOURNAL_ENTRY = "journal_entry"
    INVENTORY_ITEM = "inventory_item"
    SETTINGS = "settings"
