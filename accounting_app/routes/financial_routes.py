"""
Financial Report Routes - Balance Sheet, Income Statement, Cash Flow.
Based on Circular 99/2025/TT-BTC for Vietnamese accounting standards.
"""

from datetime import date, datetime
from decimal import Decimal

from flask import Blueprint, flash, redirect, render_template, request, url_for, make_response, jsonify
from flask_login import current_user

from core.rbac import permission_required
from services.financial_report_service import FinancialReportService, BalanceSheetService, IncomeStatementService, CashFlowService
from services.tax_service import TaxService
from reports.excel_exporter import ExcelExporter
from reports.pdf_exporter import PDFExporter


financial_bp = Blueprint("financial", __name__, url_prefix="/financial")


@financial_bp.route("/")
@permission_required("report", "read")
def index():
    """Financial reports dashboard."""
    current_year = date.today().year
    current_quarter = (date.today().month - 1) // 3 + 1
    return redirect(url_for("financial.reports", year=current_year))


@financial_bp.route("/reports")
@permission_required("report", "read")
def reports():
    """Financial reports selection page."""
    year = request.args.get("year", date.today().year, type=int)
    return render_template(
        "accounting/financial/reports.html",
        year=year,
    )


@financial_bp.route("/balance-sheet")
@permission_required("report", "read")
def balance_sheet():
    """Balance Sheet (B01 - Báo cáo tình hình tài chính)."""
    end_date_str = request.args.get("end_date")
    if end_date_str:
        end_date = date.fromisoformat(end_date_str)
    else:
        end_date = date.today()

    report = BalanceSheetService.get_balance_sheet(end_date)
    
    return render_template(
        "accounting/financial/balance_sheet.html",
        report=report,
        end_date=end_date,
    )


@financial_bp.route("/balance-sheet/export")
@permission_required("report", "read")
def export_balance_sheet():
    """Export Balance Sheet to Excel/PDF."""
    end_date_str = request.args.get("end_date")
    if end_date_str:
        end_date = date.fromisoformat(end_date_str)
    else:
        end_date = date.today()

    export_format = request.args.get("format", "excel")
    report = BalanceSheetService.get_balance_sheet(end_date)

    data = {
        "title": "Báo cáo tình hình tài chính",
        "subtitle": f"Đến ngày {end_date.strftime('%d/%m/%Y')}",
        "end_date": end_date,
        "report": report,
    }

    if export_format == "pdf":
        content = PDFExporter.export_balance_sheet(data)
        response = make_response(content)
        response.headers["Content-Type"] = "application/pdf"
        response.headers["Content-Disposition"] = f'attachment; filename=B01_BalanceSheet_{end_date.strftime("%Y%m%d")}.pdf'
    else:
        content = ExcelExporter.export_balance_sheet(data)
        response = make_response(content)
        response.headers["Content-Type"] = "application/vnd.ms-excel"
        response.headers["Content-Disposition"] = f'attachment; filename=B01_BalanceSheet_{end_date.strftime("%Y%m%d")}.xlsx'

    return response


@financial_bp.route("/income-statement")
@permission_required("report", "read")
def income_statement():
    """Income Statement (B02 - Kết quả hoạt động kinh doanh)."""
    start_date_str = request.args.get("start_date")
    end_date_str = request.args.get("end_date")

    if start_date_str and end_date_str:
        start_date = date.fromisoformat(start_date_str)
        end_date = date.fromisoformat(end_date_str)
    else:
        year = request.args.get("year", date.today().year, type=int)
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)

    report = IncomeStatementService.get_income_statement(start_date, end_date)

    return render_template(
        "accounting/financial/income_statement.html",
        report=report,
        start_date=start_date,
        end_date=end_date,
    )


@financial_bp.route("/income-statement/export")
@permission_required("report", "read")
def export_income_statement():
    """Export Income Statement to Excel/PDF."""
    start_date_str = request.args.get("start_date")
    end_date_str = request.args.get("end_date")

    if start_date_str and end_date_str:
        start_date = date.fromisoformat(start_date_str)
        end_date = date.fromisoformat(end_date_str)
    else:
        year = date.today().year
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)

    export_format = request.args.get("format", "excel")
    report = IncomeStatementService.get_income_statement(start_date, end_date)

    data = {
        "title": "Báo cáo kết quả hoạt động kinh doanh",
        "subtitle": f"Từ {start_date.strftime('%d/%m/%Y')} đến {end_date.strftime('%d/%m/%Y')}",
        "start_date": start_date,
        "end_date": end_date,
        "report": report,
    }

    if export_format == "pdf":
        content = PDFExporter.export_income_statement(data)
        response = make_response(content)
        response.headers["Content-Type"] = "application/pdf"
        response.headers["Content-Disposition"] = f'attachment; filename=B02_IncomeStatement_{start_date.year}.pdf'
    else:
        content = ExcelExporter.export_income_statement(data)
        response = make_response(content)
        response.headers["Content-Type"] = "application/vnd.ms-excel"
        response.headers["Content-Disposition"] = f'attachment; filename=B02_IncomeStatement_{start_date.year}.xlsx'

    return response


@financial_bp.route("/cash-flow")
@permission_required("report", "read")
def cash_flow():
    """Cash Flow Statement (B03 - Lưu chuyển tiền tệ - Indirect Method)."""
    start_date_str = request.args.get("start_date")
    end_date_str = request.args.get("end_date")

    if start_date_str and end_date_str:
        start_date = date.fromisoformat(start_date_str)
        end_date = date.fromisoformat(end_date_str)
    else:
        year = request.args.get("year", date.today().year, type=int)
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)

    report = CashFlowService.get_cash_flow(start_date, end_date)

    return render_template(
        "accounting/financial/cash_flow.html",
        report=report,
        start_date=start_date,
        end_date=end_date,
    )


@financial_bp.route("/cash-flow/export")
@permission_required("report", "read")
def export_cash_flow():
    """Export Cash Flow Statement to Excel/PDF."""
    start_date_str = request.args.get("start_date")
    end_date_str = request.args.get("end_date")

    if start_date_str and end_date_str:
        start_date = date.fromisoformat(start_date_str)
        end_date = date.fromisoformat(end_date_str)
    else:
        year = date.today().year
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)

    export_format = request.args.get("format", "excel")
    report = CashFlowService.get_cash_flow(start_date, end_date)

    data = {
        "title": "Lưu chuyển tiền tệ",
        "subtitle": f"Từ {start_date.strftime('%d/%m/%Y')} đến {end_date.strftime('%d/%m/%Y')}",
        "start_date": start_date,
        "end_date": end_date,
        "report": report,
    }

    if export_format == "pdf":
        content = PDFExporter.export_cash_flow(data)
        response = make_response(content)
        response.headers["Content-Type"] = "application/pdf"
        response.headers["Content-Disposition"] = f'attachment; filename=B03_CashFlow_{start_date.year}.pdf'
    else:
        content = ExcelExporter.export_cash_flow(data)
        response = make_response(content)
        response.headers["Content-Type"] = "application/vnd.ms-excel"
        response.headers["Content-Disposition"] = f'attachment; filename=B03_CashFlow_{start_date.year}.xlsx'

    return response


@financial_bp.route("/trial-balance")
@permission_required("report", "read")
def trial_balance():
    """Trial Balance (Sổ cái tổng hợp)."""
    end_date_str = request.args.get("end_date")
    if end_date_str:
        end_date = date.fromisoformat(end_date_str)
    else:
        end_date = date.today()

    from repositories.ledger_repository import LedgerRepository
    trial_balance = LedgerRepository.get_trial_balance(end_date)

    return render_template(
        "accounting/financial/trial_balance.html",
        trial_balance=trial_balance,
        end_date=end_date,
    )


@financial_bp.route("/trial-balance/export")
@permission_required("report", "read")
def export_trial_balance():
    """Export Trial Balance to Excel/PDF."""
    end_date_str = request.args.get("end_date")
    if end_date_str:
        end_date = date.fromisoformat(end_date_str)
    else:
        end_date = date.today()

    export_format = request.args.get("format", "excel")

    from repositories.ledger_repository import LedgerRepository
    trial_balance = LedgerRepository.get_trial_balance(end_date)

    data = {
        "title": "Sổ cái tổng hợp",
        "subtitle": f"Đến ngày {end_date.strftime('%d/%m/%Y')}",
        "end_date": end_date,
        "trial_balance": trial_balance,
    }

    if export_format == "pdf":
        content = PDFExporter.export_trial_balance(data)
        response = make_response(content)
        response.headers["Content-Type"] = "application/pdf"
        response.headers["Content-Disposition"] = f'attachment; filename=TrialBalance_{end_date.strftime("%Y%m%d")}.pdf'
    else:
        content = ExcelExporter.export_trial_balance(data)
        response = make_response(content)
        response.headers["Content-Type"] = "application/vnd.ms-excel"
        response.headers["Content-Disposition"] = f'attachment; filename=TrialBalance_{end_date.strftime("%Y%m%d")}.xlsx'

    return response


@financial_bp.route("/notes")
@permission_required("report", "read")
def notes():
    """Notes to Financial Statements (B05 - Thuyết minh BCTC)."""
    year = request.args.get("year", date.today().year, type=int)
    start_date = date(year, 1, 1)
    end_date = date(year, 12, 31)

    balance_sheet = BalanceSheetService.get_balance_sheet(end_date)
    income_stmt = IncomeStatementService.get_income_statement(start_date, end_date)

    from repositories.financial_report_repository import FinancialReportRepository
    account_details = FinancialReportRepository.get_account_details(start_date, end_date)

    return render_template(
        "accounting/financial/notes.html",
        year=year,
        start_date=start_date,
        end_date=end_date,
        balance_sheet=balance_sheet,
        income_statement=income_stmt,
        account_details=account_details,
    )


@financial_bp.route("/api/balance-sheet")
@permission_required("report", "read")
def api_balance_sheet():
    """API: Get Balance Sheet data."""
    end_date_str = request.args.get("end_date")
    if end_date_str:
        end_date = date.fromisoformat(end_date_str)
    else:
        end_date = date.today()

    report = BalanceSheetService.get_balance_sheet(end_date)
    return jsonify({
        "status": "success",
        "data": report,
        "end_date": end_date.isoformat(),
    })


@financial_bp.route("/api/income-statement")
@permission_required("report", "read")
def api_income_statement():
    """API: Get Income Statement data."""
    start_date_str = request.args.get("start_date")
    end_date_str = request.args.get("end_date")

    if start_date_str and end_date_str:
        start_date = date.fromisoformat(start_date_str)
        end_date = date.fromisoformat(end_date_str)
    else:
        year = date.today().year
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)

    report = IncomeStatementService.get_income_statement(start_date, end_date)
    return jsonify({
        "status": "success",
        "data": report,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
    })


@financial_bp.route("/api/cash-flow")
@permission_required("report", "read")
def api_cash_flow():
    """API: Get Cash Flow data."""
    start_date_str = request.args.get("start_date")
    end_date_str = request.args.get("end_date")

    if start_date_str and end_date_str:
        start_date = date.fromisoformat(start_date_str)
        end_date = date.fromisoformat(end_date_str)
    else:
        year = date.today().year
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)

    report = CashFlowService.get_cash_flow(start_date, end_date)
    return jsonify({
        "status": "success",
        "data": report,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
    })
