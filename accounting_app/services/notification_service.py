"""
Notification Service - Business logic for user notifications.
Handles notification creation, delivery, and management.
"""

from typing import Optional, List, Dict, Any, Tuple

from core.database import db
from core.utils import utc_now


class NotificationService:
    """Service for managing notifications."""

    @staticmethod
    def create_notification(
        user_id: int,
        title: str,
        message: str,
        notification_type: str = "info",
        entity_type: str = None,
        entity_id: int = None,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Create a notification for a user.

        Args:
            user_id: Recipient user ID
            title: Notification title
            message: Notification message
            notification_type: Type (info, success, warning, error)
            entity_type: Related entity type
            entity_id: Related entity ID

        Returns:
            Tuple of (success, result)
        """
        try:
            from models.notification import Notification

            notification = Notification(
                user_id=user_id,
                title=title,
                message=message,
                notification_type=notification_type,
                entity_type=entity_type,
                entity_id=entity_id,
            )
            db.session.add(notification)
            db.session.commit()
            return True, notification.to_dict()
        except Exception as e:
            db.session.rollback()
            return False, {"error": str(e)}

    @staticmethod
    def mark_as_read(notification_id: int, user_id: int) -> Tuple[bool, str]:
        """
        Mark notification as read.

        Args:
            notification_id: Notification ID
            user_id: User ID (for authorization)

        Returns:
            Tuple of (success, message)
        """
        try:
            from models.notification import Notification

            notification = db.session.get(Notification, notification_id)
            if not notification:
                return False, "Notification not found"

            if notification.user_id != user_id:
                return False, "Unauthorized"

            notification.is_read = True
            notification.read_at = utc_now()
            db.session.commit()

            return True, "Notification marked as read"
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def mark_all_as_read(user_id: int) -> Tuple[bool, str]:
        """
        Mark all notifications as read for a user.

        Args:
            user_id: User ID

        Returns:
            Tuple of (success, message)
        """
        try:
            from models.notification import Notification

            Notification.query.filter_by(
                user_id=user_id,
                is_read=False
            ).update({
                "is_read": True,
                "read_at": utc_now()
            })
            db.session.commit()

            return True, "All notifications marked as read"
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def delete_notification(notification_id: int, user_id: int) -> Tuple[bool, str]:
        """
        Delete a notification.

        Args:
            notification_id: Notification ID
            user_id: User ID (for authorization)

        Returns:
            Tuple of (success, message)
        """
        try:
            from models.notification import Notification

            notification = db.session.get(Notification, notification_id)
            if not notification:
                return False, "Notification not found"

            if notification.user_id != user_id:
                return False, "Unauthorized"

            db.session.delete(notification)
            db.session.commit()

            return True, "Notification deleted"
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def get_unread_count(user_id: int) -> int:
        """
        Get count of unread notifications for user.

        Args:
            user_id: User ID

        Returns:
            Count of unread notifications
        """
        from models.notification import Notification
        return Notification.query.filter_by(
            user_id=user_id,
            is_read=False
        ).count()

    @staticmethod
    def get_notifications(
        user_id: int,
        is_read: bool = None,
        notification_type: str = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        Get notifications for a user.

        Args:
            user_id: User ID
            is_read: Filter by read status
            notification_type: Filter by type
            limit: Maximum notifications to return

        Returns:
            List of notifications
        """
        from models.notification import Notification

        query = Notification.query.filter_by(user_id=user_id)

        if is_read is not None:
            query = query.filter_by(is_read=is_read)
        if notification_type:
            query = query.filter_by(notification_type=notification_type)

        notifications = query.order_by(
            Notification.created_at.desc()
        ).limit(limit).all()

        return [n.to_dict() for n in notifications]

    @staticmethod
    def notify_voucher_created(user_id: int, voucher_no: str) -> Tuple[bool, Dict]:
        """Notify user that voucher was created."""
        return NotificationService.create_notification(
            user_id=user_id,
            title="Voucher Created",
            message=f"Voucher {voucher_no} has been created successfully.",
            notification_type="success",
            entity_type="voucher",
        )

    @staticmethod
    def notify_voucher_posted(user_id: int, voucher_no: str) -> Tuple[bool, Dict]:
        """Notify user that voucher was posted."""
        return NotificationService.create_notification(
            user_id=user_id,
            title="Voucher Posted",
            message=f"Voucher {voucher_no} has been posted to the ledger.",
            notification_type="success",
            entity_type="voucher",
        )

    @staticmethod
    def notify_approval_required(
        approver_ids: List[int],
        request_no: str,
        entity_type: str,
        entity_id: int,
    ) -> List[Tuple[bool, Dict]]:
        """Notify approvers that approval is required."""
        results = []
        for user_id in approver_ids:
            result = NotificationService.create_notification(
                user_id=user_id,
                title="Approval Required",
                message=f"New approval request {request_no} requires your attention.",
                notification_type="warning",
                entity_type=entity_type,
                entity_id=entity_id,
            )
            results.append(result)
        return results

    @staticmethod
    def notify_approval_result(
        requester_id: int,
        request_no: str,
        is_approved: bool,
        comments: str = None,
    ) -> Tuple[bool, Dict]:
        """Notify requester of approval result."""
        status = "approved" if is_approved else "rejected"
        title = f"Request {status.title()}"
        message = f"Your request {request_no} has been {status}."
        if comments:
            message += f" Comment: {comments}"

        return NotificationService.create_notification(
            user_id=requester_id,
            title=title,
            message=message,
            notification_type="success" if is_approved else "error",
            entity_type="approval_request",
        )

    @staticmethod
    def notify_tax_due_soon(user_id: int, tax_type: str, due_date: str) -> Tuple[bool, Dict]:
        """Notify user of upcoming tax deadline."""
        return NotificationService.create_notification(
            user_id=user_id,
            title=f"{tax_type.upper()} Due Soon",
            message=f"Your {tax_type} payment is due on {due_date}.",
            notification_type="warning",
            entity_type="tax_payment",
        )

    @staticmethod
    def notify_tax_overdue(user_id: int, tax_type: str, payment_no: str) -> Tuple[bool, Dict]:
        """Notify user of overdue tax payment."""
        return NotificationService.create_notification(
            user_id=user_id,
            title=f"{tax_type.upper()} Overdue",
            message=f"Tax payment {payment_no} is overdue. Please pay immediately.",
            notification_type="error",
            entity_type="tax_payment",
        )

    @staticmethod
    def notify_backup_complete(user_id: int, backup_no: str) -> Tuple[bool, Dict]:
        """Notify user of successful backup."""
        return NotificationService.create_notification(
            user_id=user_id,
            title="Backup Complete",
            message=f"Backup {backup_no} completed successfully.",
            notification_type="info",
            entity_type="backup",
        )

    @staticmethod
    def notify_backup_failed(user_id: int, error: str) -> Tuple[bool, Dict]:
        """Notify user of backup failure."""
        return NotificationService.create_notification(
            user_id=user_id,
            title="Backup Failed",
            message=f"Backup failed: {error}",
            notification_type="error",
            entity_type="backup",
        )
