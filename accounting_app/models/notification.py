from datetime import datetime
from typing import Optional, List

from core.database import db
from core.utils import utc_now


class NotificationType:
    """Notification type constants."""

    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    APPROVAL = "approval"
    REMINDER = "reminder"
    SYSTEM = "system"

    CHOICES = [
        (INFO, "Thông tin"),
        (SUCCESS, "Thành công"),
        (WARNING, "Cảnh báo"),
        (ERROR, "Lỗi"),
        (APPROVAL, "Phê duyệt"),
        (REMINDER, "Nhắc nhở"),
        (SYSTEM, "Hệ thống"),
    ]


class NotificationPriority:
    """Notification priority constants."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

    CHOICES = [
        (LOW, "Thấp"),
        (MEDIUM, "Trung bình"),
        (HIGH, "Cao"),
        (URGENT, "Khẩn cấp"),
    ]


class Notification(db.Model):
    """Notification model for user notifications."""

    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(20), default=NotificationType.INFO, nullable=False)
    priority = db.Column(db.String(20), default=NotificationPriority.MEDIUM, nullable=False)
    entity_type = db.Column(db.String(50), nullable=True, index=True)
    entity_id = db.Column(db.Integer, nullable=True, index=True)
    action_url = db.Column(db.String(500), nullable=True)
    is_read = db.Column(db.Boolean, default=False, nullable=False, index=True)
    read_at = db.Column(db.DateTime, nullable=True)
    expires_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)

    user = db.relationship("User", backref="notifications")

    __table_args__ = (
        db.Index("ix_notification_user_read", "user_id", "is_read"),
        db.Index("ix_notification_expires", "expires_at"),
    )

    def __repr__(self) -> str:
        return f"<Notification {self.id} - {self.title}>"

    def mark_as_read(self) -> None:
        """Mark notification as read."""
        self.is_read = True
        self.read_at = utc_now()
        db.session.commit()

    def mark_as_unread(self) -> None:
        """Mark notification as unread."""
        self.is_read = False
        self.read_at = None
        db.session.commit()

    @property
    def is_expired(self) -> bool:
        """Check if notification is expired."""
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False

    @property
    def is_readable(self) -> bool:
        """Check if notification is still readable."""
        return not self.is_expired

    @classmethod
    def create_notification(
        cls,
        user_id: int,
        title: str,
        message: str,
        notification_type: str = NotificationType.INFO,
        priority: str = NotificationPriority.MEDIUM,
        entity_type: str = None,
        entity_id: int = None,
        action_url: str = None,
        expires_at=None,
    ) -> "Notification":
        """Create a new notification."""
        notification = cls(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            priority=priority,
            entity_type=entity_type,
            entity_id=entity_id,
            action_url=action_url,
            expires_at=expires_at,
        )
        db.session.add(notification)
        db.session.commit()
        return notification

    @classmethod
    def get_unread_count(cls, user_id: int) -> int:
        """Get unread notification count for user."""
        return cls.query.filter_by(
            user_id=user_id,
            is_read=False
        ).filter(
            db.or_(
                cls.expires_at.is_(None),
                cls.expires_at > datetime.utcnow()
            )
        ).count()

    @classmethod
    def mark_all_read(cls, user_id: int) -> int:
        """Mark all notifications as read for user."""
        count = cls.query.filter_by(
            user_id=user_id,
            is_read=False
        ).update({
            "is_read": True,
            "read_at": utc_now()
        })
        db.session.commit()
        return count

    def to_dict(self) -> dict:
        """Convert notification to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "message": self.message,
            "notification_type": self.notification_type,
            "priority": self.priority,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "action_url": self.action_url,
            "is_read": self.is_read,
            "read_at": self.read_at.isoformat() if self.read_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
