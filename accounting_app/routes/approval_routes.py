"""
Approval Routes - Approval workflow endpoints.
Handles workflow definitions and approval request processing.
"""

from datetime import date
from decimal import Decimal

from flask import Blueprint, flash, redirect, render_template, request, url_for, jsonify
from flask_login import current_user

from core.rbac import permission_required
from core.database import db
from services.approval_service import ApprovalService
from models.approval_workflow import ApprovalWorkflow, ApprovalRequest, WorkflowStatus, EntityType


approval_bp = Blueprint("approval", __name__, url_prefix="/approval")


@approval_bp.route("/")
@permission_required("report", "read")
def index():
    """Approval dashboard."""
    stats = ApprovalService.get_workflow_statistics()
    pending_count = ApprovalRequest.query.filter_by(status=WorkflowStatus.PENDING).count()
    return render_template(
        "accounting/approval/index.html",
        stats=stats,
        pending_count=pending_count,
    )


@approval_bp.route("/workflows")
@permission_required("report", "read")
def workflows():
    """List approval workflows."""
    workflows = ApprovalWorkflow.query.order_by(ApprovalWorkflow.code).all()
    return render_template(
        "accounting/approval/workflows.html",
        workflows=workflows,
    )


@approval_bp.route("/workflows/new", methods=["GET", "POST"])
@permission_required("account", "create")
def workflow_new():
    """Create new approval workflow."""
    if request.method == "GET":
        entity_types = EntityType.CHOICES
        return render_template(
            "accounting/approval/workflow_form.html",
            workflow=None,
            entity_types=entity_types,
        )

    code = request.form.get("code")
    name = request.form.get("name")
    entity_type = request.form.get("entity_type")
    description = request.form.get("description")
    approval_levels = int(request.form.get("approval_levels", 1))
    auto_approve_below = request.form.get("auto_approve_below")

    success, result = ApprovalService.create_workflow(
        code=code,
        name=name,
        entity_type=entity_type,
        description=description,
        approval_levels=approval_levels,
        auto_approve_below=Decimal(auto_approve_bellow) if auto_approve_below else None,
        created_by=current_user.id if current_user.is_authenticated else 1,
    )

    if success:
        flash("Workflow created successfully", "success")
        return redirect(url_for("approval.workflow_detail", workflow_id=result["id"]))
    else:
        flash(result.get("error", "Failed to create workflow"), "danger")
        entity_types = EntityType.CHOICES
        return render_template(
            "accounting/approval/workflow_form.html",
            workflow=request.form,
            entity_types=entity_types,
        )


@approval_bp.route("/workflows/<int:workflow_id>")
@permission_required("report", "read")
def workflow_detail(workflow_id: int):
    """Workflow detail with steps."""
    workflow = db.session.get(ApprovalWorkflow, workflow_id)
    if not workflow:
        flash("Workflow not found", "danger")
        return redirect(url_for("approval.workflows"))

    stats = ApprovalService.get_workflow_statistics(workflow_id)
    return render_template(
        "accounting/approval/workflow_detail.html",
        workflow=workflow,
        stats=stats,
    )


@approval_bp.route("/workflows/<int:workflow_id>/steps/new", methods=["POST"])
@permission_required("account", "create")
def workflow_add_step(workflow_id: int):
    """Add step to workflow."""
    workflow = db.session.get(ApprovalWorkflow, workflow_id)
    if not workflow:
        flash("Workflow not found", "danger")
        return redirect(url_for("approval.workflows"))

    sequence = int(request.form.get("sequence", 1))
    name = request.form.get("name")
    approver_role_id = request.form.get("approver_role_id", type=int)
    approval_limit = request.form.get("approval_limit")

    success, result = ApprovalService.add_workflow_step(
        workflow_id=workflow_id,
        sequence=sequence,
        name=name,
        description=request.form.get("description"),
        approver_role_id=approver_role_id,
        approval_limit=Decimal(approval_limit) if approval_limit else None,
        timeout_hours=request.form.get("timeout_hours", type=int),
        is_required=request.form.get("is_required") == "on",
        can_delegate=request.form.get("can_delegate") == "on",
    )

    if success:
        flash("Step added successfully", "success")
    else:
        flash(result.get("error", "Failed to add step"), "danger")

    return redirect(url_for("approval.workflow_detail", workflow_id=workflow_id))


@approval_bp.route("/requests")
@permission_required("report", "read")
def requests():
    """List approval requests."""
    status = request.args.get("status")
    entity_type = request.args.get("entity_type")

    query = ApprovalRequest.query
    if status:
        query = query.filter_by(status=status)
    if entity_type:
        query = query.filter_by(entity_type=entity_type)

    requests_list = query.order_by(ApprovalRequest.requested_at.desc()).all()
    statuses = WorkflowStatus.CHOICES
    entity_types = EntityType.CHOICES

    return render_template(
        "accounting/approval/requests.html",
        requests_list=requests_list,
        statuses=statuses,
        entity_types=entity_types,
    )


@approval_bp.route("/requests/pending")
@permission_required("report", "read")
def pending_requests():
    """List pending requests for current user."""
    role_ids = []
    if current_user.is_authenticated and hasattr(current_user, "role"):
        role_ids = [current_user.role_id]

    pending = ApprovalService.get_pending_requests_for_user(
        user_id=current_user.id if current_user.is_authenticated else 0,
        role_ids=role_ids,
    )

    return render_template(
        "accounting/approval/pending.html",
        pending=pending,
    )


@approval_bp.route("/requests/<int:request_id>")
@permission_required("report", "read")
def request_detail(request_id: int):
    """Request detail."""
    request_obj = db.session.get(ApprovalRequest, request_id)
    if not request_obj:
        flash("Request not found", "danger")
        return redirect(url_for("approval.requests"))

    return render_template(
        "accounting/approval/request_detail.html",
        request_obj=request_obj,
    )


@approval_bp.route("/requests/<int:request_id>/approve", methods=["POST"])
@permission_required("account", "update")
def approve_request(request_id: int):
    """Approve request."""
    comments = request.form.get("comments")

    success, result = ApprovalService.process_approval(
        request_id=request_id,
        approver_id=current_user.id if current_user.is_authenticated else 1,
        is_approved=True,
        comments=comments,
    )

    if success:
        flash("Request approved successfully", "success")
    else:
        flash(result.get("error", "Failed to approve"), "danger")

    return redirect(url_for("approval.request_detail", request_id=request_id))


@approval_bp.route("/requests/<int:request_id>/reject", methods=["POST"])
@permission_required("account", "update")
def reject_request(request_id: int):
    """Reject request."""
    comments = request.form.get("comments")

    success, result = ApprovalService.process_approval(
        request_id=request_id,
        approver_id=current_user.id if current_user.is_authenticated else 1,
        is_approved=False,
        comments=comments,
    )

    if success:
        flash("Request rejected", "warning")
    else:
        flash(result.get("error", "Failed to reject"), "danger")

    return redirect(url_for("approval.request_detail", request_id=request_id))


@approval_bp.route("/requests/<int:request_id>/cancel", methods=["POST"])
@permission_required("account", "delete")
def cancel_request(request_id: int):
    """Cancel request."""
    success, message = ApprovalService.cancel_request(request_id)

    if success:
        flash(message, "success")
    else:
        flash(message, "danger")

    return redirect(url_for("approval.requests"))


@approval_bp.route("/api/workflows")
@permission_required("report", "read")
def api_workflows():
    """API: List workflows."""
    workflows = ApprovalWorkflow.query.filter_by(is_active=True).all()
    return jsonify({
        "status": "success",
        "data": [w.to_dict() for w in workflows],
    })


@approval_bp.route("/api/requests")
@permission_required("report", "read")
def api_requests():
    """API: List requests."""
    requests_list = ApprovalRequest.query.order_by(
        ApprovalRequest.requested_at.desc()
    ).limit(100).all()
    return jsonify({
        "status": "success",
        "data": [r.to_dict() for r in requests_list],
    })


@approval_bp.route("/api/pending-count")
@permission_required("report", "read")
def api_pending_count():
    """API: Get pending count for current user."""
    count = ApprovalRequest.query.filter_by(status=WorkflowStatus.PENDING).count()
    return jsonify({
        "status": "success",
        "count": count,
    })
