from datetime import date
from decimal import Decimal

from flask import Blueprint, flash, redirect, render_template, request, url_for, jsonify
from flask_login import current_user

from core.rbac import permission_required
from services.tax_payment_service import TaxPaymentService
from models.tax_payment import TaxPayment, TaxType, TaxPaymentStatus, TaxPaymentMethod


tax_payment_bp = Blueprint("tax_payment", __name__, url_prefix="/tax-payments")


@tax_payment_bp.route("/")
@permission_required("account", "read")
def index():
    """Tax payment list page."""
    page = request.args.get("page", 1, type=int)
    per_page = 20
    tax_type = request.args.get("tax_type")
    payment_status = request.args.get("payment_status")
    period_year = request.args.get("period_year", type=int, default=date.today().year)
    search = request.args.get("search")

    payments, total = TaxPaymentService.get_tax_payments(
        page=page,
        per_page=per_page,
        tax_type=tax_type,
        payment_status=payment_status,
        period_year=period_year,
        search=search,
    )

    return render_template(
        "accounting/tax_payment/index.html",
        payments=payments,
        total=total,
        page=page,
        per_page=per_page,
        tax_type_choices=TaxType.CHOICES,
        status_choices=TaxPaymentStatus.CHOICES,
        current_year=date.today().year,
    )


@tax_payment_bp.route("/pending")
@permission_required("account", "read")
def pending():
    """Pending tax payments."""
    year = request.args.get("year", date.today().year, type=int)
    payments = TaxPaymentService.get_pending_payments(year)
    overdue = TaxPaymentService.get_overdue_payments()

    return render_template(
        "accounting/tax_payment/pending.html",
        payments=payments,
        overdue=overdue,
        year=year,
    )


@tax_payment_bp.route("/summary")
@permission_required("account", "read")
def summary():
    """Tax payment summary."""
    year = request.args.get("year", date.today().year, type=int)
    summary_data, overdue_count = TaxPaymentService.get_tax_summary(year)

    return render_template(
        "accounting/tax_payment/summary.html",
        summary=summary_data,
        overdue_count=overdue_count,
        year=year,
        tax_type_choices=TaxType.CHOICES,
    )


@tax_payment_bp.route("/create", methods=["GET", "POST"])
@permission_required("account", "create")
def create():
    """Create tax payment."""
    if request.method == "GET":
        return render_template(
            "accounting/tax_payment/create.html",
            tax_type_choices=TaxType.CHOICES,
            status_choices=TaxPaymentStatus.CHOICES,
            payment_method_choices=TaxPaymentMethod.CHOICES,
        )

    payment_no = request.form.get("payment_no")
    tax_type = request.form.get("tax_type")
    period_year = request.form.get("period_year", type=int)
    declaration_no = request.form.get("declaration_no")
    declaration_date = request.form.get("declaration_date")
    period_month = request.form.get("period_month", type=int)
    period_quarter = request.form.get("period_quarter", type=int)
    taxable_amount = Decimal(request.form.get("taxable_amount", "0.00"))
    tax_rate = Decimal(request.form.get("tax_rate", "0.00"))
    tax_amount = Decimal(request.form.get("tax_amount", "0.00"))
    interest_amount = Decimal(request.form.get("interest_amount", "0.00"))
    penalty_amount = Decimal(request.form.get("penalty_amount", "0.00"))
    payment_date = request.form.get("payment_date")
    due_date = request.form.get("due_date")
    payment_status = request.form.get("payment_status", "pending")
    payment_method = request.form.get("payment_method")
    bank_transaction_no = request.form.get("bank_transaction_no")
    tax_authority = request.form.get("tax_authority")
    tax_office_code = request.form.get("tax_office_code")
    notes = request.form.get("notes")

    if declaration_date:
        declaration_date = date.fromisoformat(declaration_date)
    if payment_date:
        payment_date = date.fromisoformat(payment_date)
    if due_date:
        due_date = date.fromisoformat(due_date)

    payment, error = TaxPaymentService.create_tax_payment(
        payment_no=payment_no if payment_no else None,
        tax_type=tax_type,
        period_year=period_year,
        declaration_no=declaration_no,
        declaration_date=declaration_date,
        period_month=period_month if period_month else None,
        period_quarter=period_quarter if period_quarter else None,
        taxable_amount=taxable_amount,
        tax_rate=tax_rate,
        tax_amount=tax_amount,
        interest_amount=interest_amount,
        penalty_amount=penalty_amount,
        payment_date=payment_date,
        due_date=due_date,
        payment_status=payment_status,
        payment_method=payment_method,
        bank_transaction_no=bank_transaction_no,
        tax_authority=tax_authority,
        tax_office_code=tax_office_code,
        notes=notes,
        created_by=current_user.id,
    )

    if error:
        flash(error, "danger")
        return redirect(url_for("tax_payment.create"))

    flash(f"Đã tạo nộp thuế '{payment.payment_no}'", "success")
    return redirect(url_for("tax_payment.index"))


@tax_payment_bp.route("/<int:tax_payment_id>")
@permission_required("account", "read")
def view(tax_payment_id: int):
    """View tax payment details."""
    payment = TaxPaymentService.get_tax_payment(tax_payment_id)
    if not payment:
        flash("Nộp thuế không tồn tại", "danger")
        return redirect(url_for("tax_payment.index"))

    return render_template(
        "accounting/tax_payment/view.html",
        payment=payment,
    )


@tax_payment_bp.route("/<int:tax_payment_id>/edit", methods=["GET", "POST"])
@permission_required("account", "update")
def edit(tax_payment_id: int):
    """Edit tax payment."""
    payment = TaxPaymentService.get_tax_payment(tax_payment_id)
    if not payment:
        flash("Nộp thuế không tồn tại", "danger")
        return redirect(url_for("tax_payment.index"))

    if request.method == "GET":
        return render_template(
            "accounting/tax_payment/edit.html",
            payment=payment,
            tax_type_choices=TaxType.CHOICES,
            status_choices=TaxPaymentStatus.CHOICES,
            payment_method_choices=TaxPaymentMethod.CHOICES,
        )

    declaration_no = request.form.get("declaration_no")
    declaration_date = request.form.get("declaration_date")
    period_month = request.form.get("period_month", type=int)
    period_quarter = request.form.get("period_quarter", type=int)
    taxable_amount = Decimal(request.form.get("taxable_amount", "0.00"))
    tax_rate = Decimal(request.form.get("tax_rate", "0.00"))
    tax_amount = Decimal(request.form.get("tax_amount", "0.00"))
    interest_amount = Decimal(request.form.get("interest_amount", "0.00"))
    penalty_amount = Decimal(request.form.get("penalty_amount", "0.00"))
    payment_date = request.form.get("payment_date")
    due_date = request.form.get("due_date")
    payment_status = request.form.get("payment_status")
    payment_method = request.form.get("payment_method")
    bank_payment_date = request.form.get("bank_payment_date")
    bank_transaction_no = request.form.get("bank_transaction_no")
    tax_authority = request.form.get("tax_authority")
    tax_office_code = request.form.get("tax_office_code")
    notes = request.form.get("notes")

    if declaration_date:
        declaration_date = date.fromisoformat(declaration_date)
    if payment_date:
        payment_date = date.fromisoformat(payment_date)
    if due_date:
        due_date = date.fromisoformat(due_date)
    if bank_payment_date:
        bank_payment_date = date.fromisoformat(bank_payment_date)

    updated, error = TaxPaymentService.update_tax_payment(
        tax_payment_id=tax_payment_id,
        declaration_no=declaration_no,
        declaration_date=declaration_date,
        period_month=period_month if period_month else None,
        period_quarter=period_quarter if period_quarter else None,
        taxable_amount=taxable_amount,
        tax_rate=tax_rate,
        tax_amount=tax_amount,
        interest_amount=interest_amount,
        penalty_amount=penalty_amount,
        payment_date=payment_date,
        due_date=due_date,
        payment_status=payment_status,
        payment_method=payment_method,
        bank_payment_date=bank_payment_date,
        bank_transaction_no=bank_transaction_no,
        tax_authority=tax_authority,
        tax_office_code=tax_office_code,
        notes=notes,
    )

    if error:
        flash(error, "danger")
        return redirect(url_for("tax_payment.edit", tax_payment_id=tax_payment_id))

    flash(f"Đã cập nhật nộp thuế '{updated.payment_no}'", "success")
    return redirect(url_for("tax_payment.index"))


@tax_payment_bp.route("/<int:tax_payment_id>/delete", methods=["POST"])
@permission_required("account", "delete")
def delete(tax_payment_id: int):
    """Delete tax payment."""
    success, error = TaxPaymentService.delete_tax_payment(tax_payment_id, current_user.id)

    if error:
        flash(error, "danger")
    else:
        flash("Đã xóa nộp thuế", "success")

    return redirect(url_for("tax_payment.index"))


@tax_payment_bp.route("/<int:tax_payment_id>/mark-paid", methods=["GET", "POST"])
@permission_required("account", "update")
def mark_paid(tax_payment_id: int):
    """Mark tax payment as paid."""
    payment = TaxPaymentService.get_tax_payment(tax_payment_id)
    if not payment:
        flash("Nộp thuế không tồn tại", "danger")
        return redirect(url_for("tax_payment.index"))

    if request.method == "GET":
        return render_template(
            "accounting/tax_payment/mark_paid.html",
            payment=payment,
            payment_method_choices=TaxPaymentMethod.CHOICES,
        )

    payment_date = date.fromisoformat(request.form.get("payment_date"))
    payment_method = request.form.get("payment_method")
    bank_transaction_no = request.form.get("bank_transaction_no")

    updated, error = TaxPaymentService.mark_as_paid(
        tax_payment_id=tax_payment_id,
        payment_date=payment_date,
        payment_method=payment_method,
        bank_transaction_no=bank_transaction_no,
    )

    if error:
        flash(error, "danger")
        return redirect(url_for("tax_payment.mark_paid", tax_payment_id=tax_payment_id))

    flash(f"Đã đánh dấu nộp thuế '{updated.payment_no}' là đã nộp", "success")
    return redirect(url_for("tax_payment.index"))


@tax_payment_bp.route("/api/summary")
@permission_required("account", "read")
def api_summary():
    """API: Get tax summary."""
    year = request.args.get("year", date.today().year, type=int)
    summary_data, overdue_count = TaxPaymentService.get_tax_summary(year)
    return jsonify({
        "status": "success",
        "year": year,
        "summary": summary_data,
        "overdue_count": overdue_count,
    })
