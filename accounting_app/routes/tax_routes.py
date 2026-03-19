"""
Tax Routes - Tax reporting and VAT declaration endpoints.
Based on Circular 99/2025/TT-BTC for Vietnamese accounting standards.
"""

from datetime import date
from decimal import Decimal

from flask import Blueprint, flash, redirect, render_template, request, url_for, make_response
from flask_login import current_user

from core.rbac import permission_required
from services.tax_service import TaxService
from services.financial_report_service import FinancialReportService
from reports.excel_exporter import ExcelExporter
from reports.pdf_exporter import PDFExporter


tax_bp = Blueprint("tax", __name__, url_prefix="/tax")


@tax_bp.route("/")
@permission_required("report", "read")
def index():
    """Tax dashboard."""
    current_year = date.today().year
    return redirect(url_for("tax.summary", year=current_year))


@tax_bp.route("/summary/<int:year>")
@permission_required("report", "read")
def summary(year: int):
    """Tax summary for a year."""
    tax_summary = TaxService.get_tax_summary(year)
    vat_summary = TaxService.get_monthly_vat_summary(year)
    quarterly_vat = TaxService.get_quarterly_vat_summary(year)
    cit_estimate = TaxService.get_cit_estimate(year)

    return render_template(
        "accounting/tax/summary.html",
        year=year,
        tax_summary=tax_summary,
        vat_summary=vat_summary,
        quarterly_vat=quarterly_vat,
        cit_estimate=cit_estimate,
    )


@tax_bp.route("/vat/declaration/<int:year>/<int:month>")
@permission_required("report", "read")
def vat_declaration(year: int, month: int):
    """Monthly VAT declaration."""
    declaration = TaxService.get_vat_declaration(year, month)
    return render_template(
        "accounting/tax/vat_declaration.html",
        year=year,
        month=month,
        declaration=declaration,
    )


@tax_bp.route("/vat/declaration/<int:year>/<int:month>/export")
@permission_required("report", "read")
def export_vat_declaration(year: int, month: int):
    """Export VAT declaration to Excel."""
    declaration = TaxService.get_vat_declaration(year, month)

    export_format = request.args.get("format", "excel")

    data = {
        "title": f"Tờ khai thuế GTGT - Kỳ {year}/{month:02d}",
        "period": declaration.period,
        "vat_input": declaration.vat_input,
        "vat_output": declaration.vat_output,
        "vat_payable": declaration.vat_payable,
        "vat_refundable": declaration.vat_refundable,
        "transactions_input": declaration.transactions_input,
        "transactions_output": declaration.transactions_output,
    }

    if export_format == "pdf":
        pdf_exporter = PDFExporter()
        pdf_content = pdf_exporter.export_vat_declaration(data)
        response = make_response(pdf_content)
        response.headers["Content-Type"] = "application/pdf"
        response.headers["Content-Disposition"] = f'attachment; filename="VAT_{year}_{month:02d}.pdf"'
        return response

    excel_exporter = ExcelExporter()
    excel_content = excel_exporter.export_vat_declaration(data)
    response = make_response(excel_content)
    response.headers["Content-Type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    response.headers["Content-Disposition"] = f'attachment; filename="VAT_{year}_{month:02d}.xlsx"'
    return response


@tax_bp.route("/vat/monthly")
@permission_required("report", "read")
def vat_monthly():
    """Monthly VAT summary."""
    current_year = date.today().year
    year = request.args.get("year", current_year, type=int)
    vat_summary = TaxService.get_monthly_vat_summary(year)
    return render_template(
        "accounting/tax/vat_monthly.html",
        year=year,
        vat_summary=vat_summary,
    )


@tax_bp.route("/vat/quarterly")
@permission_required("report", "read")
def vat_quarterly():
    """Quarterly VAT summary."""
    current_year = date.today().year
    year = request.args.get("year", current_year, type=int)
    quarterly_vat = TaxService.get_quarterly_vat_summary(year)
    return render_template(
        "accounting/tax/vat_quarterly.html",
        year=year,
        quarterly_vat=quarterly_vat,
    )


@tax_bp.route("/cit/estimate/<int:year>")
@permission_required("report", "read")
def cit_estimate(year: int):
    """Annual CIT estimate."""
    cit_estimate = TaxService.get_cit_estimate(year)
    balance_sheet = FinancialReportService.get_balance_sheet(date(year, 12, 31))
    return render_template(
        "accounting/tax/cit_estimate.html",
        year=year,
        cit_estimate=cit_estimate,
        balance_sheet=balance_sheet,
    )


@tax_bp.route("/cit/estimate/<int:year>/quarter/<int:quarter>")
@permission_required("report", "read")
def cit_estimate_quarter(year: int, quarter: int):
    """Quarterly CIT estimate."""
    cit_estimate = TaxService.get_quarterly_cit_estimate(year, quarter)
    return render_template(
        "accounting/tax/cit_estimate.html",
        year=year,
        quarter=quarter,
        cit_estimate=cit_estimate,
    )


@tax_bp.route("/cit/estimate/<int:year>/export")
@permission_required("report", "read")
def export_cit_estimate(year: int):
    """Export CIT estimate to Excel."""
    cit_estimate = TaxService.get_cit_estimate(year)

    export_format = request.args.get("format", "excel")

    data = {
        "title": f"Tạm tính thuế TNDN - Năm {year}",
        "year": year,
        "cit_estimate": cit_estimate.to_dict(),
    }

    if export_format == "pdf":
        pdf_exporter = PDFExporter()
        pdf_content = pdf_exporter.export_cit_estimate(data)
        response = make_response(pdf_content)
        response.headers["Content-Type"] = "application/pdf"
        response.headers["Content-Disposition"] = f'attachment; filename="CIT_{year}.pdf"'
        return response

    excel_exporter = ExcelExporter()
    excel_content = excel_exporter.export_cit_estimate(data)
    response = make_response(excel_content)
    response.headers["Content-Type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    response.headers["Content-Disposition"] = f'attachment; filename="CIT_{year}.xlsx"'
    return response


@tax_bp.route("/policies")
@permission_required("tax_policy", "read")
def policies():
    """Tax policies list."""
    tax_type = request.args.get("type")
    policies_list = TaxService.get_tax_policies(tax_type)
    return render_template(
        "accounting/tax/policies.html",
        policies=policies_list,
        tax_type=tax_type,
    )


@tax_bp.route("/policies/create", methods=["GET", "POST"])
@permission_required("tax_policy", "create")
def create_policy():
    """Create new tax policy."""
    if request.method == "POST":
        try:
            tax_type = request.form.get("tax_type")
            year = int(request.form.get("year"))
            rate = Decimal(request.form.get("rate"))
            rate_name = request.form.get("rate_name")
            description = request.form.get("description", "")

            TaxService.create_tax_policy(
                tax_type=tax_type,
                year=year,
                rate=rate,
                rate_name=rate_name,
                description=description,
            )

            flash(f"Đã tạo chính sách thuế: {rate_name}", "success")
            return redirect(url_for("tax.policies"))

        except ValueError as e:
            flash(str(e), "danger")

    return render_template("accounting/tax/policy_form.html")


@tax_bp.route("/calculator")
@permission_required("report", "read")
def calculator():
    """VAT calculator tool."""
    amount = request.args.get("amount", type=Decimal, default=Decimal("0"))
    vat_rate = request.args.get("vat_rate", "10")
    inclusive = request.args.get("inclusive", "yes") == "yes"

    if amount > 0:
        if inclusive:
            result = TaxService.calculate_vat_from_amount(amount, vat_rate)
        else:
            result = TaxService.calculate_vat_exclusive(amount, vat_rate)
    else:
        result = None

    return render_template(
        "accounting/tax/calculator.html",
        amount=amount,
        vat_rate=vat_rate,
        inclusive=inclusive,
        result=result,
    )
