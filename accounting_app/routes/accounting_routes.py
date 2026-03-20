from flask import Blueprint, current_app, flash, jsonify, redirect, render_template, request, url_for, make_response
from flask_login import current_user
from flask_wtf.csrf import generate_csrf
import json

from core.rbac import permission_required
from core.logging import log_audit
from forms.account_forms import AccountForm
from forms.journal_forms import JournalVoucherForm, JournalSearchForm
from models.account import AccountType
from models.journal import VoucherStatus
from repositories.account_repository import AccountRepository
from services.account_service import AccountService
from services.journal_service import JournalService
from services.ledger_service import LedgerService
from services.financial_report_service import FinancialReportService
from reports.excel_exporter import ExcelExporter
from reports.pdf_exporter import PDFExporter

accounting_bp = Blueprint(
    "accounting", __name__, url_prefix="/accounting"
)


@accounting_bp.route("/accounts")
@permission_required("account", "read")
def accounts():
    """Chart of accounts page."""
    accounts_list = AccountService.get_all_accounts()
    return render_template("accounting/accounts.html", accounts=accounts_list)


@accounting_bp.route("/accounts/create", methods=["GET", "POST"])
@permission_required("account", "create")
def create_account():
    """Create new account."""
    form = AccountForm()

    parent_accounts = AccountRepository.get_parent_accounts()
    form.parent_id.choices = [(0, "-- Không có --")] + [
        (a.id, f"{a.code} - {a.name_vi}") for a in parent_accounts
    ]

    if request.method == "POST" and form.validate_on_submit():
        try:
            account_data = {
                "code": form.account_code.data,
                "name_vi": form.account_name.data,
                "account_type": form.account_type.data,
                "parent_id": form.parent_id.data if form.parent_id.data and form.parent_id.data != 0 else None,
                "normal_balance": form.normal_balance.data,
                "is_postable": form.is_detail.data,
                "is_active": form.is_active.data,
            }

            AccountService.create_account(
                account_data,
                user_id=current_user.id,
                ip_address=request.remote_addr,
            )
            
            log_audit(
                action="create",
                entity="account",
                new_value=json.dumps(account_data),
                user_id=current_user.id,
                request_obj=request,
            )

            flash(f"Đã tạo tài khoản {form.account_code.data}", "success")
            return redirect(url_for("accounting.accounts"))

        except ValueError as e:
            flash(str(e), "danger")

    return render_template(
        "accounting/account_form.html",
        form=form,
        title="Thêm tài khoản",
    )


@accounting_bp.route("/accounts/<int:account_id>/edit", methods=["GET", "POST"])
@permission_required("account", "update")
def edit_account(account_id: int):
    """Edit existing account."""
    account = AccountService.get_account(account_id)
    if not account:
        flash("Tài khoản không tồn tại", "danger")
        return redirect(url_for("accounting.accounts"))

    form = AccountForm(obj=account)

    parent_accounts = AccountRepository.get_parent_accounts()
    form.parent_id.choices = [(0, "-- Không có --")] + [
        (a.id, f"{a.code} - {a.name_vi}")
        for a in parent_accounts
        if a.id != account_id
    ]

    if request.method == "POST" and form.validate_on_submit():
        try:
            account_data = {
                "name_vi": form.account_name.data,
                "account_type": form.account_type.data,
                "parent_id": form.parent_id.data if form.parent_id.data and form.parent_id.data != 0 else None,
                "normal_balance": form.normal_balance.data,
                "is_postable": form.is_detail.data,
                "is_active": form.is_active.data,
            }

            AccountService.update_account(
                account_id,
                account_data,
                user_id=current_user.id,
                ip_address=request.remote_addr,
            )

            flash(f"Đã cập nhật tài khoản {account.code}", "success")
            return redirect(url_for("accounting.accounts"))

        except ValueError as e:
            flash(str(e), "danger")

    if form.parent_id.data is None:
        form.parent_id.data = 0

    return render_template(
        "accounting/account_form.html",
        form=form,
        account=account,
        title="Sửa tài khoản",
    )


@accounting_bp.route("/accounts/<int:account_id>/delete", methods=["POST"])
@permission_required("account", "delete")
def delete_account(account_id: int):
    """Delete account."""
    try:
        AccountService.delete_account(
            account_id,
            user_id=current_user.id,
            ip_address=request.remote_addr,
        )
        flash("Đã xóa tài khoản", "success")
    except ValueError as e:
        flash(str(e), "danger")

    return redirect(url_for("accounting.accounts"))


@accounting_bp.route("/accounts/tree")
@permission_required("account", "read")
def account_tree():
    """Get account tree structure."""
    tree = AccountService.get_account_tree()
    return render_template("accounting/account_tree.html", tree=tree)


@accounting_bp.route("/journal")
@permission_required("journal", "read")
def journal():
    """Journal vouchers list page."""
    search_form = JournalSearchForm(request.args)
    
    status = request.args.get("status", "")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    
    from datetime import datetime
    start = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else None
    end = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None
    
    vouchers = JournalService.get_all_vouchers(
        status=status or None,
        start_date=start,
        end_date=end,
    )
    
    return render_template(
        "accounting/journal.html",
        vouchers=vouchers,
        search_form=search_form,
    )


@accounting_bp.route("/journal/create", methods=["GET", "POST"])
@permission_required("journal", "create")
def create_voucher():
    """Create new journal voucher."""
    from datetime import date
    
    template_id = request.args.get("template", "")
    template = None
    if template_id:
        from services.voucher_template_service import get_template
        template = get_template(template_id)
    
    form = JournalVoucherForm()
    
    accounts = AccountService.get_all_active_for_journal()
    form.entries[0].account_id.choices = [(0, "-- Chọn tài khoản --")] + [
        (a.id, f"{a.code} - {a.name_vi}") for a in accounts
    ]
    form.entries[1].account_id.choices = form.entries[0].account_id.choices
    
    if template:
        form.voucher_type.data = template.voucher_type
    
    if request.method == "POST":
        form.voucher_date.data = date.today()
        
        if form.validate_on_submit():
            try:
                entries_data = []
                for idx, entry_form in enumerate(form.entries):
                    current_app.logger.debug(f"Entry {idx}: {entry_form}")
                    
                    if hasattr(entry_form, 'account_id') and hasattr(entry_form.account_id, 'data'):
                        account_id_val = entry_form.account_id.data
                        if account_id_val and account_id_val != 0:
                            entries_data.append({
                                "account_id": account_id_val,
                                "debit": float(entry_form.debit.data or 0),
                                "credit": float(entry_form.credit.data or 0),
                                "description": entry_form.description.data if hasattr(entry_form.description, 'data') else str(entry_form.description),
                                "reference": entry_form.reference.data if hasattr(entry_form.reference, 'data') else str(entry_form.reference),
                                "cost_center": entry_form.cost_center.data if hasattr(entry_form.cost_center, 'data') else str(entry_form.cost_center),
                            })
                
                if not entries_data:
                    flash("Vui lòng nhập ít nhất một dòng kết toán", "danger")
                    return render_template(
                        "accounting/voucher_form.html",
                        form=form,
                        title="Thêm chứng từ",
                    )
                
                voucher_data = {
                    "voucher_date": form.voucher_date.data,
                    "voucher_type": form.voucher_type.data,
                    "description": form.description.data,
                    "reference": form.reference.data,
                }
                
                JournalService.create_voucher(
                    voucher_data,
                    entries_data,
                    user_id=current_user.id,
                    ip_address=request.remote_addr,
                )
                
                log_audit(
                    action="create",
                    entity="journal",
                    new_value=json.dumps({**voucher_data, "entries": entries_data, "voucher_date": str(voucher_data["voucher_date"])}),
                    user_id=current_user.id,
                    request_obj=request,
                )
                
                flash("Đã tạo chứng từ thành công", "success")
                return redirect(url_for("accounting.journal"))
                
            except ValueError as e:
                flash(str(e), "danger")
        else:
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages.append(f"{field}: {error}")
            if error_messages:
                flash("Lỗi: " + "; ".join(error_messages), "danger")
                current_app.logger.warning(f"Form validation failed: {form.errors}")

    from services.voucher_template_service import get_all_templates
    templates = get_all_templates()
    
    return render_template(
        "accounting/voucher_form.html",
        form=form,
        title="Thêm chứng từ",
        templates=templates,
        selected_template=template,
    )


@accounting_bp.route("/journal/<int:voucher_id>", methods=["GET"])
@permission_required("journal", "read")
def view_voucher(voucher_id: int):
    """View voucher details."""
    voucher = JournalService.get_voucher(voucher_id)
    if not voucher:
        flash("Chứng từ không tồn tại", "danger")
        return redirect(url_for("accounting.journal"))
    
    return render_template(
        "accounting/voucher_view.html",
        voucher=voucher,
    )


@accounting_bp.route("/journal/<int:voucher_id>/edit", methods=["GET", "POST"])
@permission_required("journal", "update")
def edit_voucher(voucher_id: int):
    """Edit voucher (only draft)."""
    voucher = JournalService.get_voucher(voucher_id)
    if not voucher:
        flash("Chứng từ không tồn tại", "danger")
        return redirect(url_for("accounting.journal"))
    
    if voucher.status != VoucherStatus.DRAFT:
        flash("Chỉ có thể sửa chứng từ nháp", "danger")
        return redirect(url_for("accounting.view_voucher", voucher_id=voucher_id))
    
    from datetime import date
    form = JournalVoucherForm(obj=voucher)
    
    accounts = AccountService.get_all_active_for_journal()
    choices = [(a.id, f"{a.code} - {a.name_vi}") for a in accounts]
    
    if request.method == "POST":
        if form.validate_on_submit():
            try:
                entries_data = []
                for entry_form in form.entries:
                    if hasattr(entry_form, 'account_id') and hasattr(entry_form.account_id, 'data'):
                        account_id_val = entry_form.account_id.data
                        if account_id_val and account_id_val != 0:
                            entries_data.append({
                                "account_id": account_id_val,
                                "debit": float(entry_form.debit.data or 0),
                                "credit": float(entry_form.credit.data or 0),
                                "description": entry_form.description.data if hasattr(entry_form.description, 'data') else str(entry_form.description),
                                "reference": entry_form.reference.data if hasattr(entry_form.reference, 'data') else str(entry_form.reference),
                                "cost_center": entry_form.cost_center.data if hasattr(entry_form.cost_center, 'data') else str(entry_form.cost_center),
                            })
                
                voucher_data = {
                    "voucher_date": form.voucher_date.data,
                    "voucher_type": form.voucher_type.data,
                    "description": form.description.data,
                    "reference": form.reference.data,
                }
                
                JournalService.update_voucher(
                    voucher_id,
                    voucher_data,
                    entries_data,
                    user_id=current_user.id,
                    ip_address=request.remote_addr,
                )
                
                flash("Đã cập nhật chứng từ", "success")
                return redirect(url_for("accounting.view_voucher", voucher_id=voucher_id))
                
            except ValueError as e:
                flash(str(e), "danger")
    
    return render_template(
        "accounting/voucher_form.html",
        form=form,
        voucher=voucher,
        title="Sửa chứng từ",
    )


@accounting_bp.route("/journal/<int:voucher_id>/post", methods=["POST"])
@permission_required("journal", "update")
def post_voucher(voucher_id: int):
    """Post voucher to ledger."""
    try:
        JournalService.post_voucher(
            voucher_id,
            user_id=current_user.id,
            ip_address=request.remote_addr,
        )
        
        log_audit(
            action="post",
            entity="journal",
            entity_id=voucher_id,
            new_value=json.dumps({"status": "posted"}),
            user_id=current_user.id,
            request_obj=request,
        )
        
        flash("Đã ghi sổ chứng từ", "success")
    except ValueError as e:
        flash(str(e), "danger")
    
    return redirect(url_for("accounting.view_voucher", voucher_id=voucher_id))


@accounting_bp.route("/journal/<int:voucher_id>/unpost", methods=["POST"])
@permission_required("journal", "update")
def unpost_voucher(voucher_id: int):
    """Unpost voucher."""
    try:
        JournalService.unpost_voucher(
            voucher_id,
            user_id=current_user.id,
            ip_address=request.remote_addr,
        )
        
        log_audit(
            action="unpost",
            entity="journal",
            entity_id=voucher_id,
            old_value=json.dumps({"status": "posted"}),
            new_value=json.dumps({"status": "draft"}),
            user_id=current_user.id,
            request_obj=request,
        )
        
        flash("Đã bỏ ghi sổ chứng từ", "success")
    except ValueError as e:
        flash(str(e), "danger")
    
    return redirect(url_for("accounting.view_voucher", voucher_id=voucher_id))


@accounting_bp.route("/journal/<int:voucher_id>/delete", methods=["POST"])
@permission_required("journal", "delete")
def delete_voucher(voucher_id: int):
    """Delete voucher."""
    try:
        JournalService.delete_voucher(
            voucher_id,
            user_id=current_user.id,
            ip_address=request.remote_addr,
        )
        flash("Đã xóa chứng từ", "success")
    except ValueError as e:
        flash(str(e), "danger")
    
    return redirect(url_for("accounting.journal"))


@accounting_bp.route("/api/accounts")
@permission_required("journal", "read")
def api_accounts():
    """API endpoint for account list."""
    accounts = AccountService.get_all_active_for_journal()
    return jsonify([
        {"id": a.id, "code": a.code, "name": a.name_vi, "type": a.account_type}
        for a in accounts
    ])


@accounting_bp.route("/ledger")
@permission_required("journal", "read")
def ledger():
    """General ledger page with account selection."""
    account_id = request.args.get("account_id")
    if account_id:
        return redirect(url_for("accounting.ledger_account", account_id=account_id, 
                               start_date=request.args.get("start_date"),
                               end_date=request.args.get("end_date")))
    
    accounts = AccountService.get_all_active_for_journal()
    return render_template("accounting/ledger.html", accounts=accounts)


@accounting_bp.route("/ledger/account/<int:account_id>")
@permission_required("journal", "read")
def ledger_account(account_id: int):
    """View ledger for specific account."""
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    from datetime import datetime
    start = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else None
    end = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None

    try:
        ledger_data = LedgerService.get_ledger(account_id, start, end)
        return render_template("accounting/ledger_detail.html", **ledger_data)
    except ValueError as e:
        flash(str(e), "danger")
        return redirect(url_for("accounting.ledger"))


@accounting_bp.route("/ledger/trial-balance")
@permission_required("report", "read")
def trial_balance():
    """Trial balance report."""
    end_date = request.args.get("end_date")

    from datetime import datetime
    end = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else datetime.now().date()

    trial_balance_data = LedgerService.get_trial_balance(end)
    return render_template("accounting/trial_balance.html", **trial_balance_data)


@accounting_bp.route("/ledger/general")
@permission_required("report", "read")
def general_ledger():
    """General ledger report - all accounts."""
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    from datetime import datetime
    start = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else None
    end = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else datetime.now().date()

    ledger_data = LedgerService.get_general_ledger(start, end)
    return render_template("accounting/general_ledger.html", 
                           ledger_data=ledger_data, 
                           start_date=start, 
                           end_date=end)


from datetime import date, timedelta


@accounting_bp.route("/reports")
@permission_required("report", "read")
def reports():
    """Financial reports page."""
    today = date.today()
    first_day = today.replace(day=1)
    return render_template(
        "accounting/reports.html",
        current_date=today.strftime("%Y-%m-%d"),
        first_day_of_month=first_day.strftime("%Y-%m-%d"),
    )


@accounting_bp.route("/reports/tax")
@permission_required("report", "read")
def tax_report():
    """Tax reports page."""
    from datetime import datetime
    
    today = date.today()
    current_year = today.year
    current_month = today.month
    
    year = request.args.get("year", current_year, type=int)
    month = request.args.get("month", current_month, type=int)
    tab = request.args.get("tab", "vat")
    
    from services.tax_service import TaxService
    
    vat_declaration = TaxService.get_vat_declaration(year, month)
    tndn_estimate = TaxService.get_cit_estimate(year)
    tax_summaries = TaxService.get_tax_summary(year)
    cit_rate = TaxService.get_cit_rate(year)
    cit_policies = TaxService.get_tax_policies("cit")
    
    return render_template(
        "accounting/tax_report.html",
        current_year=current_year,
        current_month=current_month,
        year=year,
        month=month,
        tab=tab,
        vat_declaration=vat_declaration,
        tndn_estimate=tndn_estimate,
        tax_summaries=tax_summaries,
        cit_rate=cit_rate,
        cit_policies=cit_policies,
    )


@accounting_bp.route("/reports/balance-sheet")
@permission_required("report", "read")
def balance_sheet():
    """Balance Sheet report."""
    end_date = request.args.get("end_date")

    from datetime import datetime
    end = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else datetime.now().date()

    report_data = FinancialReportService.get_balance_sheet(end)
    return render_template("accounting/balance_sheet.html", **report_data)


@accounting_bp.route("/reports/income-statement")
@permission_required("report", "read")
def income_statement():
    """Income Statement report."""
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    from datetime import datetime
    start = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else datetime(datetime.now().year, 1, 1).date()
    end = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else datetime.now().date()

    report_data = FinancialReportService.get_income_statement(start, end)
    return render_template("accounting/income_statement.html", **report_data)


@accounting_bp.route("/reports/cash-flow")
@permission_required("report", "read")
def cash_flow():
    """Cash Flow Statement report."""
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    from datetime import datetime
    start = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else datetime(datetime.now().year, 1, 1).date()
    end = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else datetime.now().date()

    report_data = FinancialReportService.get_cash_flow(start, end)
    return render_template("accounting/cash_flow.html", **report_data)


@accounting_bp.route("/reports/trial-balance/export/excel")
@permission_required("report", "read")
def export_trial_balance_excel():
    """Export Trial Balance to Excel."""
    end_date = request.args.get("end_date")
    from datetime import datetime
    end = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else datetime.now().date()

    try:
        excel_data = ExcelExporter.export_trial_balance(end)
        response = make_response(excel_data)
        response.headers["Content-Disposition"] = f"attachment; filename=BCD_Tai_Khoan_{end.strftime('%Y%m%d')}.xlsx"
        response.headers["Content-Type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        return response
    except Exception as e:
        flash(f"Lỗi xuất Excel: {str(e)}", "danger")
        return redirect(url_for("accounting.trial_balance"))


@accounting_bp.route("/reports/trial-balance/export/pdf")
@permission_required("report", "read")
def export_trial_balance_pdf():
    """Export Trial Balance to PDF."""
    end_date = request.args.get("end_date")
    from datetime import datetime
    end = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else datetime.now().date()

    try:
        pdf_data = PDFExporter.export_trial_balance(end)
        response = make_response(pdf_data)
        response.headers["Content-Disposition"] = f"attachment; filename=BCD_Tai_Khoan_{end.strftime('%Y%m%d')}.pdf"
        response.headers["Content-Type"] = "application/pdf"
        return response
    except Exception as e:
        flash(f"Lỗi xuất PDF: {str(e)}", "danger")
        return redirect(url_for("accounting.trial_balance"))


@accounting_bp.route("/reports/balance-sheet/export/excel")
@permission_required("report", "read")
def export_balance_sheet_excel():
    """Export Balance Sheet to Excel."""
    end_date = request.args.get("end_date")
    from datetime import datetime
    end = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else datetime.now().date()

    try:
        excel_data = ExcelExporter.export_balance_sheet(end)
        response = make_response(excel_data)
        response.headers["Content-Disposition"] = f"attachment; filename=BC_Doi_So_Tai_Chinh_{end.strftime('%Y%m%d')}.xlsx"
        response.headers["Content-Type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        return response
    except Exception as e:
        flash(f"Lỗi xuất Excel: {str(e)}", "danger")
        return redirect(url_for("accounting.balance_sheet"))


@accounting_bp.route("/reports/balance-sheet/export/pdf")
@permission_required("report", "read")
def export_balance_sheet_pdf():
    """Export Balance Sheet to PDF."""
    end_date = request.args.get("end_date")
    from datetime import datetime
    end = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else datetime.now().date()

    try:
        pdf_data = PDFExporter.export_balance_sheet(end)
        response = make_response(pdf_data)
        response.headers["Content-Disposition"] = f"attachment; filename=BC_Doi_So_Tai_Chinh_{end.strftime('%Y%m%d')}.pdf"
        response.headers["Content-Type"] = "application/pdf"
        return response
    except Exception as e:
        flash(f"Lỗi xuất PDF: {str(e)}", "danger")
        return redirect(url_for("accounting.balance_sheet"))


@accounting_bp.route("/reports/income-statement/export/excel")
@permission_required("report", "read")
def export_income_statement_excel():
    """Export Income Statement to Excel."""
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    from datetime import datetime
    start = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else datetime(datetime.now().year, 1, 1).date()
    end = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else datetime.now().date()

    try:
        excel_data = ExcelExporter.export_income_statement(start, end)
        response = make_response(excel_data)
        response.headers["Content-Disposition"] = f"attachment; filename=BC_Ket_Qua_KD_{start.strftime('%Y%m%d')}_{end.strftime('%Y%m%d')}.xlsx"
        response.headers["Content-Type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        return response
    except Exception as e:
        flash(f"Lỗi xuất Excel: {str(e)}", "danger")
        return redirect(url_for("accounting.income_statement"))


@accounting_bp.route("/reports/income-statement/export/pdf")
@permission_required("report", "read")
def export_income_statement_pdf():
    """Export Income Statement to PDF."""
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    from datetime import datetime
    start = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else datetime(datetime.now().year, 1, 1).date()
    end = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else datetime.now().date()

    try:
        pdf_data = PDFExporter.export_income_statement(start, end)
        response = make_response(pdf_data)
        response.headers["Content-Disposition"] = f"attachment; filename=BC_Ket_Qua_KD_{start.strftime('%Y%m%d')}_{end.strftime('%Y%m%d')}.pdf"
        response.headers["Content-Type"] = "application/pdf"
        return response
    except Exception as e:
        flash(f"Lỗi xuất PDF: {str(e)}", "danger")
        return redirect(url_for("accounting.income_statement"))


@accounting_bp.route("/journal/<int:voucher_id>/export/excel")
@permission_required("journal", "read")
def export_voucher_excel(voucher_id: int):
    """Export voucher to Excel."""
    try:
        excel_data = ExcelExporter.export_journal_voucher(voucher_id)
        response = make_response(excel_data)
        response.headers["Content-Disposition"] = f"attachment; filename=Chung_Tu_{voucher_id}.xlsx"
        response.headers["Content-Type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        return response
    except Exception as e:
        flash(f"Lỗi xuất Excel: {str(e)}", "danger")
        return redirect(url_for("accounting.view_voucher", voucher_id=voucher_id))


@accounting_bp.route("/journal/<int:voucher_id>/export/pdf")
@permission_required("journal", "read")
def export_voucher_pdf(voucher_id: int):
    """Export voucher to PDF."""
    try:
        pdf_data = PDFExporter.export_journal_voucher(voucher_id)
        response = make_response(pdf_data)
        response.headers["Content-Disposition"] = f"attachment; filename=Chung_Tu_{voucher_id}.pdf"
        response.headers["Content-Type"] = "application/pdf"
        return response
    except Exception as e:
        flash(f"Lỗi xuất PDF: {str(e)}", "danger")
        return redirect(url_for("accounting.view_voucher", voucher_id=voucher_id))
