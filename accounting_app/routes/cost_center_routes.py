from datetime import date
from decimal import Decimal

from flask import Blueprint, flash, redirect, render_template, request, url_for, jsonify
from flask_login import current_user

from core.rbac import permission_required
from services.cost_center_service import CostCenterService
from models.cost_center import CostCenter


cost_center_bp = Blueprint("cost_center", __name__, url_prefix="/cost-centers")


@cost_center_bp.route("/")
@permission_required("account", "read")
def index():
    """Cost center list page."""
    page = request.args.get("page", 1, type=int)
    per_page = 20
    is_active = request.args.get("is_active", type=lambda x: x == "true" if x else None)
    department = request.args.get("department")
    search = request.args.get("search")

    cost_centers, total = CostCenterService.get_cost_centers(
        page=page,
        per_page=per_page,
        is_active=is_active,
        department=department,
        search=search,
    )

    departments = CostCenterService.get_departments()

    return render_template(
        "accounting/cost_center/index.html",
        cost_centers=cost_centers,
        total=total,
        page=page,
        per_page=per_page,
        departments=departments,
    )


@cost_center_bp.route("/tree")
@permission_required("account", "read")
def tree():
    """Cost center tree view."""
    tree = CostCenterService.get_cost_center_tree()
    return render_template(
        "accounting/cost_center/tree.html",
        tree=tree,
    )


@cost_center_bp.route("/budget-report")
@permission_required("account", "read")
def budget_report():
    """Budget utilization report."""
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    if start_date:
        start_date = date.fromisoformat(start_date)
    if end_date:
        end_date = date.fromisoformat(end_date)

    report = CostCenterService.get_budget_report(start_date, end_date)
    return render_template(
        "accounting/cost_center/budget_report.html",
        report=report,
        start_date=start_date,
        end_date=end_date,
    )


@cost_center_bp.route("/create", methods=["GET", "POST"])
@permission_required("account", "create")
def create():
    """Create cost center."""
    if request.method == "GET":
        departments = CostCenterService.get_departments()
        parent_id = request.args.get("parent_id", type=int)
        parent = None
        if parent_id:
            parent = CostCenterService.get_cost_center(parent_id)
        return render_template(
            "accounting/cost_center/create.html",
            departments=departments,
            parent=parent,
        )

    name = request.form.get("name")
    code = request.form.get("code")
    description = request.form.get("description")
    parent_id = request.form.get("parent_id", type=int)
    department = request.form.get("department")
    budget_allocated = Decimal(request.form.get("budget_allocated", "0.00"))

    cost_center, error = CostCenterService.create_cost_center(
        name=name,
        code=code if code else None,
        description=description,
        parent_id=parent_id if parent_id else None,
        department=department,
        budget_allocated=budget_allocated,
        created_by=current_user.id,
    )

    if error:
        flash(error, "danger")
        return redirect(url_for("cost_center.create"))

    flash(f"Đã tạo trung tâm chi phí '{cost_center.code}'", "success")
    return redirect(url_for("cost_center.index"))


@cost_center_bp.route("/<int:cost_center_id>")
@permission_required("account", "read")
def view(cost_center_id: int):
    """View cost center details."""
    cost_center = CostCenterService.get_cost_center(cost_center_id)
    if not cost_center:
        flash("Trung tâm chi phí không tồn tại", "danger")
        return redirect(url_for("cost_center.index"))

    budget_summary = cost_center.get_budget_used()
    budget_remaining = cost_center.get_budget_remaining()

    return render_template(
        "accounting/cost_center/view.html",
        cost_center=cost_center,
        budget_used=budget_summary,
        budget_remaining=budget_remaining,
    )


@cost_center_bp.route("/<int:cost_center_id>/edit", methods=["GET", "POST"])
@permission_required("account", "update")
def edit(cost_center_id: int):
    """Edit cost center."""
    cost_center = CostCenterService.get_cost_center(cost_center_id)
    if not cost_center:
        flash("Trung tâm chi phí không tồn tại", "danger")
        return redirect(url_for("cost_center.index"))

    if request.method == "GET":
        departments = CostCenterService.get_departments()
        parent_cost_centers = CostCenterService.get_active_cost_centers()
        return render_template(
            "accounting/cost_center/edit.html",
            cost_center=cost_center,
            departments=departments,
            parent_cost_centers=parent_cost_centers,
        )

    name = request.form.get("name")
    description = request.form.get("description")
    parent_id = request.form.get("parent_id", type=int)
    department = request.form.get("department")
    budget_allocated = Decimal(request.form.get("budget_allocated", "0.00"))
    is_active = request.form.get("is_active") == "on"

    updated, error = CostCenterService.update_cost_center(
        cost_center_id=cost_center_id,
        name=name,
        description=description,
        parent_id=parent_id if parent_id else None,
        department=department,
        budget_allocated=budget_allocated,
        is_active=is_active,
    )

    if error:
        flash(error, "danger")
        return redirect(url_for("cost_center.edit", cost_center_id=cost_center_id))

    flash(f"Đã cập nhật trung tâm chi phí '{updated.code}'", "success")
    return redirect(url_for("cost_center.index"))


@cost_center_bp.route("/<int:cost_center_id>/delete", methods=["POST"])
@permission_required("account", "delete")
def delete(cost_center_id: int):
    """Delete cost center."""
    success, error = CostCenterService.delete_cost_center(cost_center_id, current_user.id)

    if error:
        flash(error, "danger")
    else:
        flash("Đã xóa trung tâm chi phí", "success")

    return redirect(url_for("cost_center.index"))


@cost_center_bp.route("/api/list")
@permission_required("account", "read")
def api_list():
    """API: Get active cost centers."""
    cost_centers = CostCenterService.get_active_cost_centers()
    return jsonify({
        "status": "success",
        "data": [cc.to_dict() for cc in cost_centers],
    })
