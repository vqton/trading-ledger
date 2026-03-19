from datetime import datetime
from typing import List, Optional, Tuple

from core.database import db
from models.notification import Notification


class NotificationRepository:
    """Repository for Notification."""

    @staticmethod
    def get_notification_by_id(notification_id: int) -> Optional[Notification]:
        """Get notification by ID."""
        return db.session.get(Notification, notification_id)

    @staticmethod
    def get_notifications(page: int = 1, per_page: int = 20, user_id: int = None, is_read: bool = None, notification_type: str = None) -> Tuple[List[Notification], int]:
        """Get paginated notifications."""
        query = Notification.query

        if user_id:
            query = query.filter(Notification.user_id == user_id)
        if is_read is not None:
            query = query.filter(Notification.is_read == is_read)
        if notification_type:
            query = query.filter(Notification.notification_type == notification_type)

        query = query.order_by(Notification.created_at.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        return pagination.items, pagination.total

    @staticmethod
    def create_notification(user_id: int, title: str, message: str, notification_type: str = "info", priority: str = "medium", entity_type: str = None, entity_id: int = None, action_url: str = None, expires_at=None) -> Notification:
        """Create a new notification."""
        notification = Notification(
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

    @staticmethod
    def mark_as_read(notification_id: int) -> Optional[Notification]:
        """Mark notification as read."""
        notification = db.session.get(Notification, notification_id)
        if notification:
            notification.mark_as_read()
        return notification

    @staticmethod
    def mark_all_read(user_id: int) -> int:
        """Mark all notifications as read for user."""
        return Notification.mark_all_read(user_id)

    @staticmethod
    def get_unread_count(user_id: int) -> int:
        """Get unread notification count."""
        return Notification.get_unread_count(user_id)

    @staticmethod
    def delete_notification(notification_id: int) -> bool:
        """Delete a notification."""
        notification = db.session.get(Notification, notification_id)
        if notification:
            db.session.delete(notification)
            db.session.commit()
            return True
        return False

    @staticmethod
    def cleanup_expired() -> int:
        """Delete expired notifications."""
        count = Notification.query.filter(
            Notification.expires_at < datetime.utcnow(),
            Notification.is_read == True
        ).delete()
        db.session.commit()
        return count
