"""
Tests for Notification Service - User notifications.
"""

import pytest

from app import create_app
from core.database import db
from services.notification_service import NotificationService
from models.notification import Notification


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


class TestNotification:
    """Tests for notification management."""

    def test_create_notification(self, app):
        """Test creating a notification."""
        with app.app_context():
            success, result = NotificationService.create_notification(
                user_id=1,
                title="Test Notification",
                message="This is a test notification",
                notification_type="info",
                entity_type="voucher",
                entity_id=1,
            )

            assert success is True
            assert result["title"] == "Test Notification"
            assert result["is_read"] is False

    def test_mark_as_read(self, app):
        """Test marking notification as read."""
        with app.app_context():
            success, notif = NotificationService.create_notification(
                user_id=1,
                title="Test",
                message="Test message",
            )

            success, message = NotificationService.mark_as_read(
                notification_id=notif["id"],
                user_id=1,
            )

            assert success is True

    def test_mark_all_as_read(self, app):
        """Test marking all notifications as read."""
        with app.app_context():
            NotificationService.create_notification(user_id=1, title="Test 1", message="Msg 1")
            NotificationService.create_notification(user_id=1, title="Test 2", message="Msg 2")

            success, message = NotificationService.mark_all_as_read(user_id=1)

            assert success is True

    def test_delete_notification(self, app):
        """Test deleting a notification."""
        with app.app_context():
            success, notif = NotificationService.create_notification(
                user_id=1,
                title="Test",
                message="Test message",
            )

            success, message = NotificationService.delete_notification(
                notification_id=notif["id"],
                user_id=1,
            )

            assert success is True

    def test_get_unread_count(self, app):
        """Test getting unread notification count."""
        with app.app_context():
            NotificationService.create_notification(user_id=1, title="Test 1", message="Msg 1")
            NotificationService.create_notification(user_id=1, title="Test 2", message="Msg 2")

            count = NotificationService.get_unread_count(user_id=1)

            assert count >= 2

    def test_get_notifications(self, app):
        """Test getting notifications."""
        with app.app_context():
            NotificationService.create_notification(user_id=1, title="Test 1", message="Msg 1")
            NotificationService.create_notification(user_id=1, title="Test 2", message="Msg 2")

            notifications = NotificationService.get_notifications(user_id=1)

            assert len(notifications) >= 2


class TestNotificationHelpers:
    """Tests for notification helper methods."""

    def test_notify_voucher_created(self, app):
        """Test voucher created notification."""
        with app.app_context():
            success, result = NotificationService.notify_voucher_created(
                user_id=1,
                voucher_no="JV-2026-00001",
            )

            assert success is True
            assert "JV-2026-00001" in result["message"]

    def test_notify_approval_result(self, app):
        """Test approval result notification."""
        with app.app_context():
            success, result = NotificationService.notify_approval_result(
                requester_id=1,
                request_no="AR-001",
                is_approved=True,
            )

            assert success is True

    def test_notify_tax_due_soon(self, app):
        """Test tax due notification."""
        with app.app_context():
            success, result = NotificationService.notify_tax_due_soon(
                user_id=1,
                tax_type="vat",
                due_date="2026-04-20",
            )

            assert success is True
