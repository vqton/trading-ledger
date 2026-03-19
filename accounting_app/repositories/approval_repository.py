from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Tuple

from core.database import db
from models.approval_workflow import ApprovalWorkflow, ApprovalStep, ApprovalRequest, ApprovalAction


class ApprovalRepository:
    """Repository for ApprovalWorkflow, ApprovalStep, ApprovalRequest, ApprovalAction."""

    @staticmethod
    def get_workflow_by_id(workflow_id: int) -> Optional[ApprovalWorkflow]:
        """Get workflow by ID."""
        return db.session.get(ApprovalWorkflow, workflow_id)

    @staticmethod
    def get_workflow_by_code(code: str) -> Optional[ApprovalWorkflow]:
        """Get workflow by code."""
        return ApprovalWorkflow.query.filter_by(code=code).first()

    @staticmethod
    def get_workflows(page: int = 1, per_page: int = 20, is_active: bool = None, entity_type: str = None) -> Tuple[List[ApprovalWorkflow], int]:
        """Get paginated workflows."""
        query = ApprovalWorkflow.query

        if is_active is not None:
            query = query.filter(ApprovalWorkflow.is_active == is_active)
        if entity_type:
            query = query.filter(ApprovalWorkflow.entity_type == entity_type)

        query = query.order_by(ApprovalWorkflow.code)
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        return pagination.items, pagination.total

    @staticmethod
    def create_workflow(code: str, name: str, entity_type: str, created_by: int, description: str = None, approval_levels: int = 1, auto_approve_below: Decimal = None) -> ApprovalWorkflow:
        """Create a new workflow."""
        workflow = ApprovalWorkflow(
            code=code,
            name=name,
            entity_type=entity_type,
            description=description,
            approval_levels=approval_levels,
            auto_approve_below=auto_approve_below,
            created_by=created_by,
        )
        db.session.add(workflow)
        db.session.commit()
        return workflow

    @staticmethod
    def add_workflow_step(workflow_id: int, sequence: int, name: str, approver_role_id: int = None, approver_user_id: int = None, approval_limit: Decimal = None, timeout_hours: int = None, is_required: bool = True, can_delegate: bool = False) -> ApprovalStep:
        """Add step to workflow."""
        step = ApprovalStep(
            workflow_id=workflow_id,
            sequence=sequence,
            name=name,
            approver_role_id=approver_role_id,
            approver_user_id=approver_user_id,
            approval_limit=approval_limit,
            timeout_hours=timeout_hours,
            is_required=is_required,
            can_delegate=can_delegate,
        )
        db.session.add(step)
        db.session.commit()
        return step

    @staticmethod
    def get_request_by_id(request_id: int) -> Optional[ApprovalRequest]:
        """Get request by ID."""
        return db.session.get(ApprovalRequest, request_id)

    @staticmethod
    def get_requests(page: int = 1, per_page: int = 20, status: str = None, requester_id: int = None) -> Tuple[List[ApprovalRequest], int]:
        """Get paginated requests."""
        query = ApprovalRequest.query

        if status:
            query = query.filter(ApprovalRequest.status == status)
        if requester_id:
            query = query.filter(ApprovalRequest.requester_id == requester_id)

        query = query.order_by(ApprovalRequest.requested_at.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        return pagination.items, pagination.total

    @staticmethod
    def get_pending_requests_for_user(user_id: int) -> List[ApprovalRequest]:
        """Get pending requests for a user."""
        return ApprovalRequest.query.filter(
            ApprovalRequest.status == "pending"
        ).order_by(ApprovalRequest.requested_at.desc()).all()

    @staticmethod
    def create_request(workflow_id: int, entity_type: str, entity_id: int, requester_id: int, amount: Decimal = None, description: str = None) -> ApprovalRequest:
        """Create a new approval request."""
        request_no = ApprovalRequest.generate_request_no(entity_type)
        request = ApprovalRequest(
            request_no=request_no,
            workflow_id=workflow_id,
            entity_type=entity_type,
            entity_id=entity_id,
            requester_id=requester_id,
            amount=amount,
            description=description,
        )
        db.session.add(request)
        db.session.commit()
        return request

    @staticmethod
    def approve_request(request_id: int, step_id: int, approver_id: int, comments: str = None) -> ApprovalAction:
        """Approve a request."""
        action = ApprovalAction(
            request_id=request_id,
            step_id=step_id,
            approver_id=approver_id,
            is_approved=True,
            comments=comments,
        )
        db.session.add(action)

        request = db.session.get(ApprovalRequest, request_id)
        request.advance_step()

        db.session.commit()
        return action

    @staticmethod
    def reject_request(request_id: int, step_id: int, approver_id: int, comments: str = None) -> ApprovalAction:
        """Reject a request."""
        action = ApprovalAction(
            request_id=request_id,
            step_id=step_id,
            approver_id=approver_id,
            is_approved=False,
            comments=comments,
        )
        db.session.add(action)

        request = db.session.get(ApprovalRequest, request_id)
        request.reject()

        db.session.commit()
        return action

    @staticmethod
    def get_request_actions(request_id: int) -> List[ApprovalAction]:
        """Get all actions for a request."""
        return ApprovalAction.query.filter_by(request_id=request_id).order_by(ApprovalAction.action_at).all()
