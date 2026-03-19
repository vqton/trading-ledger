from datetime import date
from decimal import Decimal

from flask import Blueprint, flash, redirect, render_template, request, url_for, jsonify
from flask_login import current_user

from core.rbac import permission_required
from services.project_service import ProjectService
from services.cost_center_service import CostCenterService
from models.project import Project, ProjectStatus, ProjectType


project_bp = Blueprint("project", __name__, url_prefix="/projects")


@project_bp.route("/")
@permission_required("account", "read")
def index():
    """Project list page."""
    page = request.args.get("page", 1, type=int)
    per_page = 20
    is_active = request.args.get("is_active", type=lambda x: x == "true" if x else None)
    status = request.args.get("status")
    project_type = request.args.get("project_type")
    search = request.args.get("search")

    projects, total = ProjectService.get_projects(
        page=page,
        per_page=per_page,
        is_active=is_active,
        status=status,
        project_type=project_type,
        search=search,
    )

    return render_template(
        "accounting/project/index.html",
        projects=projects,
        total=total,
        page=page,
        per_page=per_page,
        status_choices=ProjectStatus.CHOICES,
        type_choices=ProjectType.CHOICES,
    )


@project_bp.route("/summary")
@permission_required("account", "read")
def summary():
    """Project summary dashboard."""
    summary = ProjectService.get_project_summary()
    return render_template(
        "accounting/project/summary.html",
        summary=summary,
    )


@project_bp.route("/create", methods=["GET", "POST"])
@permission_required("account", "create")
def create():
    """Create project."""
    if request.method == "GET":
        cost_centers = CostCenterService.get_active_cost_centers()
        return render_template(
            "accounting/project/create.html",
            cost_centers=cost_centers,
            status_choices=ProjectStatus.CHOICES,
            type_choices=ProjectType.CHOICES,
        )

    name = request.form.get("name")
    code = request.form.get("code")
    description = request.form.get("description")
    customer_id = request.form.get("customer_id", type=int)
    start_date = request.form.get("start_date")
    end_date = request.form.get("end_date")
    expected_completion = request.form.get("expected_completion_date")
    status = request.form.get("status", "planning")
    project_type = request.form.get("project_type", "service")
    total_contract_value = Decimal(request.form.get("total_contract_value", "0.00"))
    manager_id = request.form.get("manager_id", type=int)
    cost_center_id = request.form.get("cost_center_id", type=int)

    if start_date:
        start_date = date.fromisoformat(start_date)
    if end_date:
        end_date = date.fromisoformat(end_date)
    if expected_completion:
        expected_completion = date.fromisoformat(expected_completion)

    project, error = ProjectService.create_project(
        name=name,
        code=code if code else None,
        description=description,
        customer_id=customer_id if customer_id else None,
        start_date=start_date,
        end_date=end_date,
        expected_completion_date=expected_completion,
        status=status,
        project_type=project_type,
        total_contract_value=total_contract_value,
        manager_id=manager_id if manager_id else None,
        cost_center_id=cost_center_id if cost_center_id else None,
        created_by=current_user.id,
    )

    if error:
        flash(error, "danger")
        return redirect(url_for("project.create"))

    flash(f"Đã tạo dự án '{project.code}'", "success")
    return redirect(url_for("project.index"))


@project_bp.route("/<int:project_id>")
@permission_required("account", "read")
def view(project_id: int):
    """View project details."""
    proj = ProjectService.get_project(project_id)
    if not proj:
        flash("Dự án không tồn tại", "danger")
        return redirect(url_for("project.index"))

    return render_template(
        "accounting/project/view.html",
        project=proj,
    )


@project_bp.route("/<int:project_id>/edit", methods=["GET", "POST"])
@permission_required("account", "update")
def edit(project_id: int):
    """Edit project."""
    proj = ProjectService.get_project(project_id)
    if not proj:
        flash("Dự án không tồn tại", "danger")
        return redirect(url_for("project.index"))

    if request.method == "GET":
        cost_centers = CostCenterService.get_active_cost_centers()
        return render_template(
            "accounting/project/edit.html",
            project=proj,
            cost_centers=cost_centers,
            status_choices=ProjectStatus.CHOICES,
            type_choices=ProjectType.CHOICES,
        )

    name = request.form.get("name")
    description = request.form.get("description")
    customer_id = request.form.get("customer_id", type=int)
    start_date = request.form.get("start_date")
    end_date = request.form.get("end_date")
    expected_completion = request.form.get("expected_completion_date")
    status = request.form.get("status")
    project_type = request.form.get("project_type")
    total_contract_value = Decimal(request.form.get("total_contract_value", "0.00"))
    completion_percentage = Decimal(request.form.get("completion_percentage", "0.00"))
    manager_id = request.form.get("manager_id", type=int)
    cost_center_id = request.form.get("cost_center_id", type=int)
    is_active = request.form.get("is_active") == "on"

    if start_date:
        start_date = date.fromisoformat(start_date)
    if end_date:
        end_date = date.fromisoformat(end_date)
    if expected_completion:
        expected_completion = date.fromisoformat(expected_completion)

    updated, error = ProjectService.update_project(
        project_id=project_id,
        name=name,
        description=description,
        customer_id=customer_id if customer_id else None,
        start_date=start_date,
        end_date=end_date,
        expected_completion_date=expected_completion,
        status=status,
        project_type=project_type,
        total_contract_value=total_contract_value,
        completion_percentage=completion_percentage,
        manager_id=manager_id if manager_id else None,
        cost_center_id=cost_center_id if cost_center_id else None,
        is_active=is_active,
    )

    if error:
        flash(error, "danger")
        return redirect(url_for("project.edit", project_id=project_id))

    flash(f"Đã cập nhật dự án '{updated.code}'", "success")
    return redirect(url_for("project.index"))


@project_bp.route("/<int:project_id>/delete", methods=["POST"])
@permission_required("account", "delete")
def delete(project_id: int):
    """Delete project."""
    success, error = ProjectService.delete_project(project_id, current_user.id)

    if error:
        flash(error, "danger")
    else:
        flash("Đã xóa dự án", "success")

    return redirect(url_for("project.index"))


@project_bp.route("/<int:project_id>/complete", methods=["POST"])
@permission_required("account", "update")
def complete(project_id: int):
    """Mark project as completed."""
    updated, error = ProjectService.complete_project(project_id, current_user.id)

    if error:
        flash(error, "danger")
    else:
        flash(f"Đã đánh dấu dự án '{updated.code}' hoàn thành", "success")

    return redirect(url_for("project.index"))


@project_bp.route("/<int:project_id>/refresh", methods=["POST"])
@permission_required("account", "read")
def refresh(project_id: int):
    """Refresh project totals from journal entries."""
    proj = ProjectService.refresh_project_totals(project_id)

    if proj:
        flash(f"Đã cập nhật số liệu dự án '{proj.code}'", "success")
    else:
        flash("Dự án không tồn tại", "danger")

    return redirect(url_for("project.view", project_id=project_id))


@project_bp.route("/api/list")
@permission_required("account", "read")
def api_list():
    """API: Get active projects."""
    projects = ProjectService.get_active_projects()
    return jsonify({
        "status": "success",
        "data": [p.to_dict() for p in projects],
    })
