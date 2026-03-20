"""
System Setting Routes - System configuration endpoints.
Handles application settings management.
"""

from flask import Blueprint, flash, redirect, render_template, request, url_for, jsonify
from flask_login import current_user

from core.rbac import permission_required
from services.system_setting_service import SystemSettingService


settings_bp = Blueprint("settings", __name__, url_prefix="/settings")


@settings_bp.route("/")
@permission_required("account", "read")
def index():
    """Settings dashboard."""
    categories = [
        ("company", "Company Information"),
        ("accounting", "Accounting Settings"),
        ("approval", "Approval Settings"),
        ("backup", "Backup Settings"),
        ("all", "All Settings"),
    ]
    return render_template(
        "accounting/settings/index.html",
        categories=categories,
    )


@settings_bp.route("/company", methods=["GET", "POST"])
@permission_required("account", "update")
def company():
    """Company information settings."""
    if request.method == "POST":
        company_name = request.form.get("company_name")
        company_tax_id = request.form.get("company_tax_id")
        company_address = request.form.get("company_address")
        company_phone = request.form.get("company_phone")
        company_email = request.form.get("company_email")

        SystemSettingService.set_setting("company_name", company_name, "string", "company")
        SystemSettingService.set_setting("company_tax_id", company_tax_id, "string", "company")
        SystemSettingService.set_setting("company_address", company_address, "string", "company")
        SystemSettingService.set_setting("company_phone", company_phone, "string", "company")
        SystemSettingService.set_setting("company_email", company_email, "string", "company")

        flash("Company information updated", "success")
        return redirect(url_for("settings.company"))

    company_info = SystemSettingService.get_company_info()
    return render_template(
        "accounting/settings/company.html",
        company=company_info,
    )


@settings_bp.route("/accounting", methods=["GET", "POST"])
@permission_required("account", "update")
def accounting():
    """Accounting settings."""
    if request.method == "POST":
        fiscal_year_start = request.form.get("fiscal_year_start", type=int)
        currency_code = request.form.get("currency_code")
        decimal_places = request.form.get("decimal_places", type=int)
        voucher_prefix = request.form.get("voucher_prefix")
        auto_post = request.form.get("auto_post_vouchers") == "on"

        SystemSettingService.set_setting("fiscal_year_start", fiscal_year_start, "int", "accounting")
        SystemSettingService.set_setting("currency_code", currency_code, "string", "accounting")
        SystemSettingService.set_setting("decimal_places", decimal_places, "int", "accounting")
        SystemSettingService.set_setting("voucher_prefix", voucher_prefix, "string", "accounting")
        SystemSettingService.set_setting("auto_post_vouchers", auto_post, "bool", "accounting")

        flash("Accounting settings updated", "success")
        return redirect(url_for("settings.accounting"))

    settings = SystemSettingService.get_accounting_settings()
    return render_template(
        "accounting/settings/accounting.html",
        settings=settings,
    )


@settings_bp.route("/approval", methods=["GET", "POST"])
@permission_required("account", "update")
def approval():
    """Approval settings."""
    if request.method == "POST":
        require_approval = request.form.get("require_approval") == "on"
        threshold = request.form.get("approval_threshold", type=lambda x: int(x) if x else 0)

        SystemSettingService.set_setting("require_approval", require_approval, "bool", "approval")
        SystemSettingService.set_setting("approval_threshold", threshold, "int", "approval")

        flash("Approval settings updated", "success")
        return redirect(url_for("settings.approval"))

    settings = SystemSettingService.get_settings_by_category("approval")
    return render_template(
        "accounting/settings/approval.html",
        settings=settings,
    )


@settings_bp.route("/backup", methods=["GET", "POST"])
@permission_required("account", "update")
def backup_settings():
    """Backup settings."""
    if request.method == "POST":
        enabled = request.form.get("backup_enabled") == "on"
        retention = request.form.get("backup_retention_days", type=int)
        frequency = request.form.get("auto_backup_frequency")

        SystemSettingService.set_setting("backup_enabled", enabled, "bool", "backup")
        SystemSettingService.set_setting("backup_retention_days", retention, "int", "backup")
        SystemSettingService.set_setting("auto_backup_frequency", frequency, "string", "backup")

        flash("Backup settings updated", "success")
        return redirect(url_for("settings.backup_settings"))

    settings = SystemSettingService.get_settings_by_category("backup")
    return render_template(
        "accounting/settings/backup.html",
        settings=settings,
    )


@settings_bp.route("/all")
@permission_required("account", "read")
def all_settings():
    """View all settings."""
    all_settings_list = SystemSettingService.get_all_settings()
    return render_template(
        "accounting/settings/all.html",
        settings_list=all_settings_list,
    )


@settings_bp.route("/api/setting/<key>", methods=["GET"])
@permission_required("account", "read")
def api_get_setting(key: str):
    """API: Get setting value."""
    value = SystemSettingService.get_setting(key)
    return jsonify({
        "status": "success",
        "key": key,
        "value": value,
    })


@settings_bp.route("/api/settings", methods=["GET"])
@permission_required("account", "read")
def api_get_settings():
    """API: Get all settings."""
    settings = SystemSettingService.get_all_settings()
    return jsonify({
        "status": "success",
        "data": settings,
    })


@settings_bp.route("/api/setting/<key>", methods=["POST"])
@permission_required("account", "update")
def api_set_setting(key: str):
    """API: Set setting value."""
    data = request.get_json()
    value = data.get("value")
    value_type = data.get("value_type", "string")

    success, result = SystemSettingService.set_setting(
        key=key,
        value=value,
        value_type=value_type,
        updated_by=current_user.id if current_user.is_authenticated else None,
    )

    return jsonify({
        "status": "success" if success else "error",
        "result": result,
    })
