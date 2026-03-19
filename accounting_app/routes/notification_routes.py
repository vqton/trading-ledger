"""
Notification Routes - User notification endpoints.
Handles notification viewing and management.
"""

from flask import Blueprint, flash, redirect, render_template, request, url_for, jsonify
from flask_login import current_user

from core.rbac import permission_required
from services.notification_service import NotificationService


notification_bp = Blueprint("notification", __name__, url_prefix="/notifications")


@notification_bp.route("/")
@permission_required("report", "read")
def index():
    """Notification list."""
    page = request.args.get("page", 1, type=int)
    per_page = 20
    is_read = request.args.get("is_read")

    if not current_user.is_authenticated:
        flash("Please login to view notifications", "warning")
        return redirect(url_for("auth.login"))

    is_read_filter = None
    if is_read == "true":
        is_read_filter = True
    elif is_read == "false":
        is_read_filter = False

    notifications = NotificationService.get_notifications(
        user_id=current_user.id,
        is_read=is_read_filter,
        limit=per_page,
    )

    unread_count = NotificationService.get_unread_count(current_user.id)

    return render_template(
        "accounting/notifications/index.html",
        notifications=notifications,
        unread_count=unread_count,
    )


@notification_bp.route("/<int:notification_id>/read", methods=["POST"])
@permission_required("report", "read")
def mark_read(notification_id: int):
    """Mark notification as read."""
    if not current_user.is_authenticated:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401

    success, message = NotificationService.mark_as_read(
        notification_id=notification_id,
        user_id=current_user.id,
    )

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"status": "success" if success else "error", "message": message})

    if success:
        flash(message, "success")
    return redirect(url_for("notification.index"))


@notification_bp.route("/mark-all-read", methods=["POST"])
@permission_required("report", "read")
def mark_all_read():
    """Mark all notifications as read."""
    if not current_user.is_authenticated:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401

    success, message = NotificationService.mark_all_as_read(user_id=current_user.id)

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"status": "success" if success else "error", "message": message})

    if success:
        flash(message, "success")
    return redirect(url_for("notification.index"))


@notification_bp.route("/<int:notification_id>/delete", methods=["POST"])
@permission_required("account", "delete")
def delete(notification_id: int):
    """Delete notification."""
    if not current_user.is_authenticated:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401

    success, message = NotificationService.delete_notification(
        notification_id=notification_id,
        user_id=current_user.id,
    )

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"status": "success" if success else "error", "message": message})

    if success:
        flash(message, "success")
    else:
        flash(message, "danger")
    return redirect(url_for("notification.index"))


@notification_bp.route("/api/unread-count")
@permission_required("report", "read")
def api_unread_count():
    """API: Get unread count."""
    if not current_user.is_authenticated:
        return jsonify({"status": "error", "count": 0}), 401

    count = NotificationService.get_unread_count(user_id=current_user.id)
    return jsonify({
        "status": "success",
        "count": count,
    })


@notification_bp.route("/api/notifications")
@permission_required("report", "read")
def api_notifications():
    """API: Get recent notifications."""
    if not current_user.is_authenticated:
        return jsonify({"status": "error", "notifications": []}), 401

    limit = request.args.get("limit", 10, type=int)
    notifications = NotificationService.get_notifications(
        user_id=current_user.id,
        limit=limit,
    )
    return jsonify({
        "status": "success",
        "notifications": notifications,
    })
