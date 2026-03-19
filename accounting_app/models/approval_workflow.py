from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List

from core.database import db
from core.utils import utc_now


class ApprovalWorkflow(db.Model):
    """Approval Workflow model for internal control (Điều 3 TT99).

    Defines approval workflows for various document types per Vietnamese
    accounting regulations.
    """

    __tablename__ = "approval_workflows"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    entity_type = db.Column(db.String(50), nullable=False, index=True)
    approval_levels = db.Column(db.Integer, default=1)
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    auto_approve_below = db.Column(db.Numeric(18, 2), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    creator = db.relationship("User", backref="approval_workflows")
    steps = db.relationship("ApprovalStep", backref="workflow", lazy="selectin", order_by="ApprovalStep.sequence")
    requests = db.relationship("ApprovalRequest", backref="workflow", lazy="dynamic")

    __table_args__ = (
        db.Index("ix_workflow_entity_active", "entity_type", "is_active"),
    )

    def __repr__(self) -> str:
        return f"<ApprovalWorkflow {self.code} - {self.name}>"

    def get_current_step(self) -> Optional["ApprovalStep"]:
        """Get current active step in workflow."""
        for step in self.steps:
            if not step.is_completed:
                return step
        return None

    def is_complete(self) -> bool:
        """Check if all workflow steps are complete."""
        return all(step.is_completed for step in self.steps)

    def get_max_approval_limit(self) -> Decimal:
        """Get maximum approval limit across all steps."""
        if not self.steps:
            return Decimal("0.00")
        return max(step.approval_limit or Decimal("0.00") for step in self.steps)

    @classmethod
    def generate_code(cls, entity_type: str) -> str:
        """Generate workflow code."""
        year = datetime.now().year
        prefix_map = {
            "voucher": "WF-V",
            "payment": "WF-P",
            "expense": "WF-E",
            "purchase": "WF-B",
            "journal": "WF-J",
            "general": "WF-G",
        }
        prefix = prefix_map.get(entity_type, "WF")

        last_wf = cls.query.filter(
            cls.code.like(f"{prefix}-{year}%")
        ).order_by(cls.code.desc()).first()

        if last_wf:
            last_num = int(last_wf.code.split("-")[-1])
            new_num = last_num + 1
        else:
            new_num = 1

        return f"{prefix}-{year}-{new_num:04d}"

    def to_dict(self) -> dict:
        """Convert workflow to dictionary."""
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "description": self.description,
            "entity_type": self.entity_type,
            "approval_levels": self.approval_levels,
            "is_active": self.is_active,
            "auto_approve_below": float(self.auto_approve_below) if self.auto_approve_below else None,
            "steps": [step.to_dict() for step in self.steps],
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ApprovalStep(db.Model):
    """Approval Step model for workflow definitions."""

    __tablename__ = "approval_steps"

    id = db.Column(db.Integer, primary_key=True)
    workflow_id = db.Column(db.Integer, db.ForeignKey("approval_workflows.id"), nullable=False)
    sequence = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    approver_role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=True)
    approver_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    approval_limit = db.Column(db.Numeric(18, 2), nullable=True)
    timeout_hours = db.Column(db.Integer, nullable=True)
    is_required = db.Column(db.Boolean, default=True, nullable=False)
    can_delegate = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)

    approver_role = db.relationship("Role", backref="approval_steps")
    approver_user = db.relationship("User", backref="approval_steps")
    approvals = db.relationship("ApprovalAction", backref="step", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<ApprovalStep {self.sequence} - {self.name}>"

    @property
    def is_completed(self) -> bool:
        """Check if step has at least one approval."""
        return self.approvals.filter_by(is_approved=True).count() > 0

    @property
    def is_rejected(self) -> bool:
        """Check if step has a rejection."""
        return self.approvals.filter_by(is_approved=False).count() > 0

    def get_approver(self) -> Optional["User"]:
        """Get the assigned approver."""
        if self.approver_user:
            return self.approver_user
        return None

    def to_dict(self) -> dict:
        """Convert step to dictionary."""
        return {
            "id": self.id,
            "workflow_id": self.workflow_id,
            "sequence": self.sequence,
            "name": self.name,
            "description": self.description,
            "approver_role_id": self.approver_role_id,
            "approver_user_id": self.approver_user_id,
            "approval_limit": float(self.approval_limit) if self.approval_limit else None,
            "timeout_hours": self.timeout_hours,
            "is_required": self.is_required,
            "can_delegate": self.can_delegate,
            "is_completed": self.is_completed,
            "is_rejected": self.is_rejected,
        }


class ApprovalRequest(db.Model):
    """Approval Request model for tracking individual approval requests."""

    __tablename__ = "approval_requests"

    id = db.Column(db.Integer, primary_key=True)
    request_no = db.Column(db.String(50), unique=True, nullable=False, index=True)
    workflow_id = db.Column(db.Integer, db.ForeignKey("approval_workflows.id"), nullable=False)
    entity_type = db.Column(db.String(50), nullable=False, index=True)
    entity_id = db.Column(db.Integer, nullable=False, index=True)
    amount = db.Column(db.Numeric(18, 2), nullable=True)
    description = db.Column(db.String(500), nullable=True)
    requester_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    current_step_sequence = db.Column(db.Integer, default=1)
    status = db.Column(db.String(20), default="pending", nullable=False, index=True)
    requested_at = db.Column(db.DateTime, default=utc_now, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    comments = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    requester = db.relationship("User", backref="approval_requests", foreign_keys=[requester_id])

    __table_args__ = (
        db.Index("ix_request_entity", "entity_type", "entity_id"),
        db.Index("ix_request_status_date", "status", "requested_at"),
    )

    def __repr__(self) -> str:
        return f"<ApprovalRequest {self.request_no} - {self.status}>"

    @property
    def is_approved(self) -> bool:
        """Check if request is fully approved."""
        return self.status == "approved"

    @property
    def is_rejected(self) -> bool:
        """Check if request is rejected."""
        return self.status == "rejected"

    @property
    def is_pending(self) -> bool:
        """Check if request is pending."""
        return self.status == "pending"

    def get_current_step(self) -> Optional[ApprovalStep]:
        """Get current step in workflow."""
        from models.approval_workflow import ApprovalWorkflow
        workflow = db.session.get(ApprovalWorkflow, self.workflow_id)
        if workflow:
            for step in workflow.steps:
                if step.sequence == self.current_step_sequence:
                    return step
        return None

    def advance_step(self) -> None:
        """Advance to next workflow step."""
        self.current_step_sequence += 1
        if self.current_step_sequence > self.workflow.approval_levels:
            self.status = "approved"
            self.completed_at = utc_now()
        db.session.commit()

    def reject(self) -> None:
        """Reject the request."""
        self.status = "rejected"
        self.completed_at = utc_now()
        db.session.commit()

    @classmethod
    def generate_request_no(cls, entity_type: str) -> str:
        """Generate request number."""
        year = datetime.now().year
        month = datetime.now().month
        prefix_map = {
            "voucher": "AR-V",
            "payment": "AR-P",
            "expense": "AR-E",
            "purchase": "AR-B",
            "journal": "AR-J",
        }
        prefix = prefix_map.get(entity_type, "AR")

        last_req = cls.query.filter(
            cls.request_no.like(f"{prefix}-{year}%")
        ).order_by(cls.request_no.desc()).first()

        if last_req:
            last_num = int(last_req.request_no.split("-")[-1])
            new_num = last_num + 1
        else:
            new_num = 1

        return f"{prefix}-{year}{month:02d}-{new_num:05d}"

    def to_dict(self) -> dict:
        """Convert request to dictionary."""
        return {
            "id": self.id,
            "request_no": self.request_no,
            "workflow_id": self.workflow_id,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "amount": float(self.amount) if self.amount else None,
            "description": self.description,
            "requester_id": self.requester_id,
            "current_step_sequence": self.current_step_sequence,
            "status": self.status,
            "requested_at": self.requested_at.isoformat() if self.requested_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "comments": self.comments,
        }


class ApprovalAction(db.Model):
    """Approval Action model for tracking individual approvals/rejections."""

    __tablename__ = "approval_actions"

    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey("approval_requests.id"), nullable=False)
    step_id = db.Column(db.Integer, db.ForeignKey("approval_steps.id"), nullable=False)
    approver_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    is_approved = db.Column(db.Boolean, nullable=False)
    comments = db.Column(db.Text, nullable=True)
    delegated_from_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    action_at = db.Column(db.DateTime, default=utc_now, nullable=False)

    approver = db.relationship("User", backref="approval_actions", foreign_keys=[approver_id])
    delegated_from = db.relationship("User", backref="delegated_actions", foreign_keys=[delegated_from_id])

    def __repr__(self) -> str:
        action = "Approved" if self.is_approved else "Rejected"
        return f"<ApprovalAction {self.id} - {action}>"

    def to_dict(self) -> dict:
        """Convert action to dictionary."""
        return {
            "id": self.id,
            "request_id": self.request_id,
            "step_id": self.step_id,
            "approver_id": self.approver_id,
            "is_approved": self.is_approved,
            "comments": self.comments,
            "delegated_from_id": self.delegated_from_id,
            "action_at": self.action_at.isoformat() if self.action_at else None,
        }


class WorkflowStatus:
    """Workflow status constants."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

    CHOICES = [
        (PENDING, "Chờ duyệt"),
        (APPROVED, "Đã duyệt"),
        (REJECTED, "Từ chối"),
        (CANCELLED, "Hủy bỏ"),
        (EXPIRED, "Hết hạn"),
    ]


class EntityType:
    """Entity types requiring approval."""

    VOUCHER = "voucher"
    PAYMENT = "payment"
    EXPENSE = "expense"
    PURCHASE = "purchase"
    JOURNAL = "journal"
    GENERAL = "general"

    CHOICES = [
        (VOUCHER, "Chứng từ"),
        (PAYMENT, "Thanh toán"),
        (EXPENSE, "Chi phí"),
        (PURCHASE, "Mua hàng"),
        (JOURNAL, "Sổ kế toán"),
        (GENERAL, "Tổng quát"),
    ]
