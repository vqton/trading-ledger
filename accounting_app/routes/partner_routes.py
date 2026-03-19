"""
Partner Routes - Customer, Vendor, and Employee management endpoints.
Based on Circular 99/2025/TT-BTC for Vietnamese accounting standards.
"""

from datetime import date
from decimal import Decimal

from flask import Blueprint, flash, redirect, render_template, request, url_for, jsonify, make_response
from flask_login import current_user

from core.rbac import permission_required
from core.database import db
from services.partner_service import PartnerService
from models.partner import Customer, Vendor, Employee, CustomerType, VendorType, EmployeeType


partner_bp = Blueprint("partner", __name__, url_prefix="/partner")


@partner_bp.route("/")
@permission_required("account", "read")
def index():
    """Partner dashboard."""
    summary = PartnerService.get_partner_summary()
    return render_template(
        "accounting/partner/index.html",
        summary=summary,
    )


@partner_bp.route("/customers")
@permission_required("account", "read")
def customers():
    """Customer list."""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)
    is_active = request.args.get("is_active", type=lambda x: x == "true" if x else None)
    customer_type = request.args.get("customer_type")
    search = request.args.get("search")

    customers, total = PartnerService.get_customers(
        is_active=is_active,
        customer_type=customer_type,
        search=search,
        page=page,
        per_page=per_page
    )

    customer_types = PartnerService.get_customer_types()

    return render_template(
        "accounting/partner/customers.html",
        customers=customers,
        total=total,
        page=page,
        per_page=per_page,
        customer_types=customer_types,
    )


@partner_bp.route("/customers/<int:customer_id>")
@permission_required("account", "read")
def customer_detail(customer_id: int):
    """Customer detail."""
    customer = PartnerService.get_customer(customer_id)
    if not customer:
        flash("Customer not found", "danger")
        return redirect(url_for("partner.customers"))

    ar_aging = PartnerService.get_customer_ar_aging(customer_id)

    return render_template(
        "accounting/partner/customer_detail.html",
        customer=customer,
        ar_aging=ar_aging,
    )


@partner_bp.route("/customers/new", methods=["GET", "POST"])
@permission_required("account", "create")
def customer_new():
    """Create new customer."""
    if request.method == "GET":
        customer_types = PartnerService.get_customer_types()
        return render_template(
            "accounting/partner/customer_form.html",
            customer=None,
            customer_types=customer_types,
        )

    data = {
        "name": request.form.get("name"),
        "tax_id": request.form.get("tax_id"),
        "email": request.form.get("email"),
        "phone": request.form.get("phone"),
        "address": request.form.get("address"),
        "city": request.form.get("city"),
        "country": request.form.get("country", "Vietnam"),
        "contact_person": request.form.get("contact_person"),
        "credit_limit": Decimal(request.form.get("credit_limit", "0")),
        "payment_terms": int(request.form.get("payment_terms", 30)),
        "customer_type": request.form.get("customer_type", "corporate"),
        "notes": request.form.get("notes"),
        "created_by": current_user.id,
    }

    success, result = PartnerService.create_customer(data)

    if success:
        flash("Customer created successfully", "success")
        return redirect(url_for("partner.customer_detail", customer_id=result["id"]))
    else:
        flash(result.get("error", "Failed to create customer"), "danger")
        customer_types = PartnerService.get_customer_types()
        return render_template(
            "accounting/partner/customer_form.html",
            customer=data,
            customer_types=customer_types,
        )


@partner_bp.route("/customers/<int:customer_id>/edit", methods=["GET", "POST"])
@permission_required("account", "update")
def customer_edit(customer_id: int):
    """Edit customer."""
    if request.method == "GET":
        customer = PartnerService.get_customer(customer_id)
        if not customer:
            flash("Customer not found", "danger")
            return redirect(url_for("partner.customers"))
        customer_types = PartnerService.get_customer_types()
        return render_template(
            "accounting/partner/customer_form.html",
            customer=customer,
            customer_types=customer_types,
        )

    data = {
        "name": request.form.get("name"),
        "tax_id": request.form.get("tax_id"),
        "email": request.form.get("email"),
        "phone": request.form.get("phone"),
        "address": request.form.get("address"),
        "city": request.form.get("city"),
        "country": request.form.get("country"),
        "contact_person": request.form.get("contact_person"),
        "credit_limit": Decimal(request.form.get("credit_limit", "0")),
        "payment_terms": int(request.form.get("payment_terms", 30)),
        "customer_type": request.form.get("customer_type"),
        "notes": request.form.get("notes"),
        "is_active": request.form.get("is_active") == "true",
    }

    success, result = PartnerService.update_customer(customer_id, data)

    if success:
        flash("Customer updated successfully", "success")
        return redirect(url_for("partner.customer_detail", customer_id=customer_id))
    else:
        flash(result.get("error", "Failed to update customer"), "danger")
        customer_types = PartnerService.get_customer_types()
        return render_template(
            "accounting/partner/customer_form.html",
            customer=data,
            customer_types=customer_types,
        )


@partner_bp.route("/customers/<int:customer_id>/delete", methods=["POST"])
@permission_required("account", "delete")
def customer_delete(customer_id: int):
    """Delete (deactivate) customer."""
    success, message = PartnerService.delete_customer(customer_id)
    if success:
        flash(message, "success")
    else:
        flash(message, "danger")
    return redirect(url_for("partner.customers"))


@partner_bp.route("/vendors")
@permission_required("account", "read")
def vendors():
    """Vendor list."""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)
    is_active = request.args.get("is_active", type=lambda x: x == "true" if x else None)
    vendor_type = request.args.get("vendor_type")
    search = request.args.get("search")

    vendors_list, total = PartnerService.get_vendors(
        is_active=is_active,
        vendor_type=vendor_type,
        search=search,
        page=page,
        per_page=per_page
    )

    vendor_types = PartnerService.get_vendor_types()

    return render_template(
        "accounting/partner/vendors.html",
        vendors=vendors_list,
        total=total,
        page=page,
        per_page=per_page,
        vendor_types=vendor_types,
    )


@partner_bp.route("/vendors/<int:vendor_id>")
@permission_required("account", "read")
def vendor_detail(vendor_id: int):
    """Vendor detail."""
    vendor = PartnerService.get_vendor(vendor_id)
    if not vendor:
        flash("Vendor not found", "danger")
        return redirect(url_for("partner.vendors"))

    ap_aging = PartnerService.get_vendor_ap_aging(vendor_id)

    return render_template(
        "accounting/partner/vendor_detail.html",
        vendor=vendor,
        ap_aging=ap_aging,
    )


@partner_bp.route("/vendors/new", methods=["GET", "POST"])
@permission_required("account", "create")
def vendor_new():
    """Create new vendor."""
    if request.method == "GET":
        vendor_types = PartnerService.get_vendor_types()
        return render_template(
            "accounting/partner/vendor_form.html",
            vendor=None,
            vendor_types=vendor_types,
        )

    data = {
        "name": request.form.get("name"),
        "tax_id": request.form.get("tax_id"),
        "email": request.form.get("email"),
        "phone": request.form.get("phone"),
        "address": request.form.get("address"),
        "city": request.form.get("city"),
        "country": request.form.get("country", "Vietnam"),
        "contact_person": request.form.get("contact_person"),
        "credit_limit": Decimal(request.form.get("credit_limit", "0")),
        "payment_terms": int(request.form.get("payment_terms", 30)),
        "vendor_type": request.form.get("vendor_type", "supplier"),
        "bank_account": request.form.get("bank_account"),
        "bank_name": request.form.get("bank_name"),
        "notes": request.form.get("notes"),
        "created_by": current_user.id,
    }

    success, result = PartnerService.create_vendor(data)

    if success:
        flash("Vendor created successfully", "success")
        return redirect(url_for("partner.vendor_detail", vendor_id=result["id"]))
    else:
        flash(result.get("error", "Failed to create vendor"), "danger")
        vendor_types = PartnerService.get_vendor_types()
        return render_template(
            "accounting/partner/vendor_form.html",
            vendor=data,
            vendor_types=vendor_types,
        )


@partner_bp.route("/vendors/<int:vendor_id>/edit", methods=["GET", "POST"])
@permission_required("account", "update")
def vendor_edit(vendor_id: int):
    """Edit vendor."""
    if request.method == "GET":
        vendor = PartnerService.get_vendor(vendor_id)
        if not vendor:
            flash("Vendor not found", "danger")
            return redirect(url_for("partner.vendors"))
        vendor_types = PartnerService.get_vendor_types()
        return render_template(
            "accounting/partner/vendor_form.html",
            vendor=vendor,
            vendor_types=vendor_types,
        )

    data = {
        "name": request.form.get("name"),
        "tax_id": request.form.get("tax_id"),
        "email": request.form.get("email"),
        "phone": request.form.get("phone"),
        "address": request.form.get("address"),
        "city": request.form.get("city"),
        "country": request.form.get("country"),
        "contact_person": request.form.get("contact_person"),
        "credit_limit": Decimal(request.form.get("credit_limit", "0")),
        "payment_terms": int(request.form.get("payment_terms", 30)),
        "vendor_type": request.form.get("vendor_type"),
        "bank_account": request.form.get("bank_account"),
        "bank_name": request.form.get("bank_name"),
        "notes": request.form.get("notes"),
        "is_active": request.form.get("is_active") == "true",
    }

    success, result = PartnerService.update_vendor(vendor_id, data)

    if success:
        flash("Vendor updated successfully", "success")
        return redirect(url_for("partner.vendor_detail", vendor_id=vendor_id))
    else:
        flash(result.get("error", "Failed to update vendor"), "danger")
        vendor_types = PartnerService.get_vendor_types()
        return render_template(
            "accounting/partner/vendor_form.html",
            vendor=data,
            vendor_types=vendor_types,
        )


@partner_bp.route("/vendors/<int:vendor_id>/delete", methods=["POST"])
@permission_required("account", "delete")
def vendor_delete(vendor_id: int):
    """Delete (deactivate) vendor."""
    success, message = PartnerService.delete_vendor(vendor_id)
    if success:
        flash(message, "success")
    else:
        flash(message, "danger")
    return redirect(url_for("partner.vendors"))


@partner_bp.route("/employees")
@permission_required("account", "read")
def employees():
    """Employee list."""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)
    is_active = request.args.get("is_active", type=lambda x: x == "true" if x else None)
    department = request.args.get("department")
    employee_type = request.args.get("employee_type")
    search = request.args.get("search")

    employees_list, total = PartnerService.get_employees(
        is_active=is_active,
        department=department,
        employee_type=employee_type,
        search=search,
        page=page,
        per_page=per_page
    )

    employee_types = PartnerService.get_employee_types()
    departments = PartnerService.get_departments()

    return render_template(
        "accounting/partner/employees.html",
        employees=employees_list,
        total=total,
        page=page,
        per_page=per_page,
        employee_types=employee_types,
        departments=departments,
    )


@partner_bp.route("/employees/<int:employee_id>")
@permission_required("account", "read")
def employee_detail(employee_id: int):
    """Employee detail."""
    employee = PartnerService.get_employee(employee_id)
    if not employee:
        flash("Employee not found", "danger")
        return redirect(url_for("partner.employees"))

    return render_template(
        "accounting/partner/employee_detail.html",
        employee=employee,
    )


@partner_bp.route("/employees/new", methods=["GET", "POST"])
@permission_required("account", "create")
def employee_new():
    """Create new employee."""
    if request.method == "GET":
        employee_types = PartnerService.get_employee_types()
        departments = PartnerService.get_departments()
        return render_template(
            "accounting/partner/employee_form.html",
            employee=None,
            employee_types=employee_types,
            departments=departments,
        )

    data = {
        "employee_id": request.form.get("employee_id"),
        "name": request.form.get("name"),
        "date_of_birth": request.form.get("date_of_birth"),
        "gender": request.form.get("gender"),
        "email": request.form.get("email"),
        "phone": request.form.get("phone"),
        "address": request.form.get("address"),
        "city": request.form.get("city"),
        "department": request.form.get("department"),
        "position": request.form.get("position"),
        "employee_type": request.form.get("employee_type", "fulltime"),
        "join_date": request.form.get("join_date"),
        "id_card": request.form.get("id_card"),
        "tax_id": request.form.get("tax_id"),
        "social_insurance_no": request.form.get("social_insurance_no"),
        "bank_account": request.form.get("bank_account"),
        "bank_name": request.form.get("bank_name"),
        "notes": request.form.get("notes"),
        "created_by": current_user.id,
    }

    success, result = PartnerService.create_employee(data)

    if success:
        flash("Employee created successfully", "success")
        return redirect(url_for("partner.employee_detail", employee_id=result["id"]))
    else:
        flash(result.get("error", "Failed to create employee"), "danger")
        employee_types = PartnerService.get_employee_types()
        departments = PartnerService.get_departments()
        return render_template(
            "accounting/partner/employee_form.html",
            employee=data,
            employee_types=employee_types,
            departments=departments,
        )


@partner_bp.route("/employees/<int:employee_id>/edit", methods=["GET", "POST"])
@permission_required("account", "update")
def employee_edit(employee_id: int):
    """Edit employee."""
    if request.method == "GET":
        employee = PartnerService.get_employee(employee_id)
        if not employee:
            flash("Employee not found", "danger")
            return redirect(url_for("partner.employees"))
        employee_types = PartnerService.get_employee_types()
        departments = PartnerService.get_departments()
        return render_template(
            "accounting/partner/employee_form.html",
            employee=employee,
            employee_types=employee_types,
            departments=departments,
        )

    data = {
        "employee_id": request.form.get("employee_id"),
        "name": request.form.get("name"),
        "date_of_birth": request.form.get("date_of_birth"),
        "gender": request.form.get("gender"),
        "email": request.form.get("email"),
        "phone": request.form.get("phone"),
        "address": request.form.get("address"),
        "city": request.form.get("city"),
        "department": request.form.get("department"),
        "position": request.form.get("position"),
        "employee_type": request.form.get("employee_type"),
        "join_date": request.form.get("join_date"),
        "leave_date": request.form.get("leave_date"),
        "id_card": request.form.get("id_card"),
        "tax_id": request.form.get("tax_id"),
        "social_insurance_no": request.form.get("social_insurance_no"),
        "bank_account": request.form.get("bank_account"),
        "bank_name": request.form.get("bank_name"),
        "notes": request.form.get("notes"),
        "is_active": request.form.get("is_active") == "true",
    }

    success, result = PartnerService.update_employee(employee_id, data)

    if success:
        flash("Employee updated successfully", "success")
        return redirect(url_for("partner.employee_detail", employee_id=employee_id))
    else:
        flash(result.get("error", "Failed to update employee"), "danger")
        employee_types = PartnerService.get_employee_types()
        departments = PartnerService.get_departments()
        return render_template(
            "accounting/partner/employee_form.html",
            employee=data,
            employee_types=employee_types,
            departments=departments,
        )


@partner_bp.route("/employees/<int:employee_id>/delete", methods=["POST"])
@permission_required("account", "delete")
def employee_delete(employee_id: int):
    """Delete (deactivate) employee."""
    success, message = PartnerService.delete_employee(employee_id)
    if success:
        flash(message, "success")
    else:
        flash(message, "danger")
    return redirect(url_for("partner.employees"))


@partner_bp.route("/ar-aging")
@permission_required("report", "read")
def ar_aging():
    """AR Aging report."""
    end_date = request.args.get("end_date")
    if end_date:
        end_date = date.fromisoformat(end_date)
    else:
        end_date = date.today()

    aging = PartnerService.get_customer_ar_aging(end_date=end_date)

    return render_template(
        "accounting/partner/ar_aging.html",
        aging=aging,
        end_date=end_date,
    )


@partner_bp.route("/ap-aging")
@permission_required("report", "read")
def ap_aging():
    """AP Aging report."""
    end_date = request.args.get("end_date")
    if end_date:
        end_date = date.fromisoformat(end_date)
    else:
        end_date = date.today()

    aging = PartnerService.get_vendor_ap_aging(end_date=end_date)

    return render_template(
        "accounting/partner/ap_aging.html",
        aging=aging,
        end_date=end_date,
    )


@partner_bp.route("/api/customers")
@permission_required("account", "read")
def api_customers():
    """API: List customers."""
    search = request.args.get("search", "")
    customers, _ = PartnerService.get_customers(search=search, per_page=100)
    return jsonify({
        "status": "success",
        "data": customers,
    })


@partner_bp.route("/api/vendors")
@permission_required("account", "read")
def api_vendors():
    """API: List vendors."""
    search = request.args.get("search", "")
    vendors, _ = PartnerService.get_vendors(search=search, per_page=100)
    return jsonify({
        "status": "success",
        "data": vendors,
    })


@partner_bp.route("/api/employees")
@permission_required("account", "read")
def api_employees():
    """API: List employees."""
    search = request.args.get("search", "")
    employees, _ = PartnerService.get_employees(search=search, per_page=100)
    return jsonify({
        "status": "success",
        "data": employees,
    })
