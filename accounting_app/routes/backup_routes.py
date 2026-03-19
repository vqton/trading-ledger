"""
Backup Routes - Database backup endpoints.
Handles backup creation, restoration, and scheduling.
"""

from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for, jsonify, send_file
from flask_login import current_user

from core.rbac import permission_required
from services.backup_service import BackupService


backup_bp = Blueprint("backup", __name__, url_prefix="/backup")


@backup_bp.route("/")
@permission_required("account", "read")
def index():
    """Backup dashboard."""
    stats = BackupService.get_backup_statistics()
    schedules = BackupService.get_schedules()
    return render_template(
        "accounting/backup/index.html",
        stats=stats,
        schedules=schedules,
    )


@backup_bp.route("/backups")
@permission_required("account", "read")
def backups():
    """List backups."""
    backup_type = request.args.get("backup_type")
    status = request.args.get("status")

    backups_list = BackupService.get_backups(
        backup_type=backup_type,
        status=status,
    )

    return render_template(
        "accounting/backup/backups.html",
        backups=backups_list,
    )


@backup_bp.route("/backups/create", methods=["POST"])
@permission_required("account", "create")
def create_backup():
    """Create new backup."""
    success, result = BackupService.create_backup(
        backup_type="manual",
        created_by=current_user.id if current_user.is_authenticated else 1,
    )

    if success:
        flash("Backup created successfully", "success")
    else:
        flash(result.get("error", "Failed to create backup"), "danger")

    return redirect(url_for("backup.backups"))


@backup_bp.route("/backups/<int:backup_id>/download")
@permission_required("account", "read")
def download_backup(backup_id: int):
    """Download backup file."""
    backup = BackupService.get_backup_by_id(backup_id)
    if not backup:
        flash("Backup not found", "danger")
        return redirect(url_for("backup.backups"))

    try:
        return send_file(
            backup["file_path"],
            as_attachment=True,
            download_name=f"accounting_{backup['backup_no']}.db",
        )
    except Exception as e:
        flash(f"Error downloading backup: {str(e)}", "danger")
        return redirect(url_for("backup.backups"))


@backup_bp.route("/backups/<int:backup_id>/restore", methods=["POST"])
@permission_required("account", "update")
def restore_backup(backup_id: int):
    """Restore from backup."""
    success, message = BackupService.restore_backup(backup_id)

    if success:
        flash(message, "success")
    else:
        flash(message, "danger")

    return redirect(url_for("backup.backups"))


@backup_bp.route("/backups/<int:backup_id>/delete", methods=["POST"])
@permission_required("account", "delete")
def delete_backup(backup_id: int):
    """Delete backup."""
    success, message = BackupService.delete_backup(backup_id)

    if success:
        flash(message, "success")
    else:
        flash(message, "danger")

    return redirect(url_for("backup.backups"))


@backup_bp.route("/schedules")
@permission_required("account", "read")
def schedules():
    """List backup schedules."""
    schedules_list = BackupService.get_schedules()
    return render_template(
        "accounting/backup/schedules.html",
        schedules=schedules_list,
    )


@backup_bp.route("/schedules/new", methods=["GET", "POST"])
@permission_required("account", "create")
def schedule_new():
    """Create new backup schedule."""
    if request.method == "GET":
        return render_template(
            "accounting/backup/schedule_form.html",
            schedule=None,
        )

    success, result = BackupService.create_schedule(
        name=request.form.get("name"),
        backup_type=request.form.get("backup_type", "auto"),
        frequency=request.form.get("frequency"),
        time_str=request.form.get("time", "00:00"),
        day_of_week=request.form.get("day_of_week", type=int),
        day_of_month=request.form.get("day_of_month", type=int),
        retention_days=request.form.get("retention_days", type=int, default=30),
        created_by=current_user.id if current_user.is_authenticated else 1,
    )

    if success:
        flash("Schedule created successfully", "success")
        return redirect(url_for("backup.schedules"))
    else:
        flash(result.get("error", "Failed to create schedule"), "danger")
        return render_template(
            "accounting/backup/schedule_form.html",
            schedule=request.form,
        )


@backup_bp.route("/schedules/<int:schedule_id>/toggle", methods=["POST"])
@permission_required("account", "update")
def toggle_schedule(schedule_id: int):
    """Toggle schedule active status."""
    from models.backup import BackupSchedule

    schedule = BackupSchedule.query.get(schedule_id)
    if not schedule:
        flash("Schedule not found", "danger")
        return redirect(url_for("backup.schedules"))

    schedule.is_active = not schedule.is_active

    from core.database import db
    db.session.commit()

    status = "activated" if schedule.is_active else "deactivated"
    flash(f"Schedule {status}", "success")
    return redirect(url_for("backup.schedules"))


@backup_bp.route("/schedules/<int:schedule_id>/delete", methods=["POST"])
@permission_required("account", "delete")
def delete_schedule(schedule_id: int):
    """Delete backup schedule."""
    success, message = BackupService.delete_schedule(schedule_id)

    if success:
        flash(message, "success")
    else:
        flash(message, "danger")

    return redirect(url_for("backup.schedules"))


@backup_bp.route("/api/stats")
@permission_required("account", "read")
def api_stats():
    """API: Get backup statistics."""
    stats = BackupService.get_backup_statistics()
    return jsonify({
        "status": "success",
        "data": stats,
    })


@backup_bp.route("/api/backups")
@permission_required("account", "read")
def api_backups():
    """API: List backups."""
    backups_list = BackupService.get_backups()
    return jsonify({
        "status": "success",
        "data": backups_list,
    })
