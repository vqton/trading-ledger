"""
Dividend Routes - TK 332 dividend payable endpoints.
Circular 99/2025/TT-BTC compliant dividend management.
"""

from datetime import date
from decimal import Decimal

from flask import Blueprint, flash, redirect, render_template, request, url_for, jsonify
from flask_login import current_user

from core.rbac import permission_required
from core.database import db
from services.dividend_payable_service import DividendPayableService
from models.dividend_payable import DividendPayable, ShareholderType, DividendPaymentStatus


dividend_bp = Blueprint("dividend", __name__, url_prefix="/dividends")


@dividend_bp.route("/")
@permission_required("report", "read")
def index():
    """Dividend dashboard."""
    outstanding = DividendPayableService.get_outstanding_dividends()
    return render_template(
        "accounting/dividends/index.html",
        outstanding=outstanding,
    )


@dividend_bp.route("/dividends")
@permission_required("report", "read")
def dividends():
    """List dividend obligations."""
    status = request.args.get("status")
    shareholder_type = request.args.get("shareholder_type")

    dividends_list = DividendPayableService.get_dividends(
        status=status,
        shareholder_type=shareholder_type,
    )

    statuses = DividendPaymentStatus.CHOICES
    shareholder_types = ShareholderType.CHOICES

    return render_template(
        "accounting/dividends/dividends.html",
        dividends=dividends_list,
        statuses=statuses,
        shareholder_types=shareholder_types,
    )


@dividend_bp.route("/dividends/new", methods=["GET", "POST"])
@permission_required("account", "create")
def dividend_new():
    """Create new dividend obligation."""
    if request.method == "GET":
        shareholder_types = ShareholderType.CHOICES
        return render_template(
            "accounting/dividends/dividend_form.html",
            dividend=None,
            shareholder_types=shareholder_types,
        )

    declaration_date_str = request.form.get("declaration_date")
    declaration_date = date.fromisoformat(declaration_date_str) if declaration_date_str else date.today()

    due_date_str = request.form.get("due_date")
    due_date = date.fromisoformat(due_date_str) if due_date_str else None

    success, result = DividendPayableService.create_dividend(
        shareholder_name=request.form.get("shareholder_name"),
        shareholder_type=request.form.get("shareholder_type"),
        share_quantity=Decimal(request.form.get("share_quantity", "0")),
        dividend_per_share=Decimal(request.form.get("dividend_per_share", "0")),
        declaration_date=declaration_date,
        due_date=due_date,
        notes=request.form.get("notes"),
        created_by=current_user.id if current_user.is_authenticated else 1,
    )

    if success:
        flash("Dividend created successfully", "success")
        return redirect(url_for("dividend.dividend_detail", dividend_id=result["id"]))
    else:
        flash(result.get("error", "Failed to create dividend"), "danger")
        shareholder_types = ShareholderType.CHOICES
        return render_template(
            "accounting/dividends/dividend_form.html",
            dividend=request.form,
            shareholder_types=shareholder_types,
        )


@dividend_bp.route("/dividends/<int:dividend_id>")
@permission_required("report", "read")
def dividend_detail(dividend_id: int):
    """Dividend detail."""
    dividend = DividendPayableService.get_dividend_by_id(dividend_id)
    if not dividend:
        flash("Dividend not found", "danger")
        return redirect(url_for("dividend.dividends"))

    return render_template(
        "accounting/dividends/dividend_detail.html",
        dividend=dividend,
    )


@dividend_bp.route("/dividends/<int:dividend_id>/pay", methods=["GET", "POST"])
@permission_required("account", "update")
def pay_dividend(dividend_id: int):
    """Record dividend payment."""
    if request.method == "GET":
        dividend = DividendPayableService.get_dividend_by_id(dividend_id)
        return render_template(
            "accounting/dividends/pay_dividend.html",
            dividend=dividend,
        )

    payment_date_str = request.form.get("payment_date")
    payment_date = date.fromisoformat(payment_date_str) if payment_date_str else date.today()

    success, result = DividendPayableService.record_payment(
        dividend_id=dividend_id,
        payment_date=payment_date,
        payment_method=request.form.get("payment_method"),
        bank_account=request.form.get("bank_account"),
        notes=request.form.get("notes"),
    )

    if success:
        flash("Dividend payment recorded", "success")
    else:
        flash(result.get("error", "Failed to record payment"), "danger")

    return redirect(url_for("dividend.dividend_detail", dividend_id=dividend_id))


@dividend_bp.route("/dividends/<int:dividend_id>/cancel", methods=["POST"])
@permission_required("account", "delete")
def cancel_dividend(dividend_id: int):
    """Cancel dividend obligation."""
    success, result = DividendPayableService.cancel_dividend(
        dividend_id=dividend_id,
        reason=request.form.get("reason"),
    )

    if success:
        flash("Dividend cancelled", "success")
    else:
        flash(result.get("error", "Failed to cancel"), "danger")

    return redirect(url_for("dividend.dividends"))


@dividend_bp.route("/summary")
@permission_required("report", "read")
def summary():
    """Dividend summary by fiscal year."""
    fiscal_year = request.args.get("year", date.today().year, type=int)
    summary_data = DividendPayableService.get_dividend_summary(fiscal_year)
    return render_template(
        "accounting/dividends/summary.html",
        summary=summary_data,
        fiscal_year=fiscal_year,
    )


@dividend_bp.route("/api/dividends")
@permission_required("report", "read")
def api_dividends():
    """API: List dividends."""
    dividends_list = DividendPayableService.get_dividends()
    return jsonify({
        "status": "success",
        "data": dividends_list,
    })


@dividend_bp.route("/api/outstanding")
@permission_required("report", "read")
def api_outstanding():
    """API: Get outstanding dividends."""
    outstanding = DividendPayableService.get_outstanding_dividends()
    return jsonify({
        "status": "success",
        "data": outstanding,
    })
