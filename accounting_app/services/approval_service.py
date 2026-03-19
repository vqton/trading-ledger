"""
Approval Service - Business logic for approval workflows.
Handles workflow creation, approval requests, and step processing.
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, List, Dict, Any, Tuple

from core.database import db
from core.utils import utc_now
from models.approval_workflow import (
    ApprovalWorkflow,
    ApprovalStep,
    ApprovalRequest,
    ApprovalAction,
    WorkflowStatus,
    EntityType,
)
from repositories.approval_repository import ApprovalRepository


class ApprovalService:
    """Service for managing approval workflows."""

    @staticmethod
    def create_workflow(
        code: str,
        name: str,
        entity_type: str,
        description: str = None,
        approval_levels: int = 1,
        auto_approve_below: Decimal = None,
        created_by: int = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Create a new approval workflow.

        Args:
            code: Workflow code
            name: Workflow name
            entity_type: Entity type to approve
            description: Workflow description
            approval_levels: Number of approval levels
            auto_approve_below: Auto-approve threshold
            created_by: Creator user ID

        Returns:
            Tuple of (success, result)
        """
        try:
            workflow = ApprovalWorkflow(
                code=code,
                name=name,
                description=description,
                entity_type=entity_type,
                approval_levels=approval_levels,
                auto_approve_below=auto_approve_below,
                created_by=created_by or 1,
            )
            db.session.add(workflow)
            db.session.commit()
            return True, workflow.to_dict()
        except Exception as e:
            db.session.rollback()
            return False, {"error": str(e)}

    @staticmethod
    def add_workflow_step(
        workflow_id: int,
        sequence: int,
        name: str,
        description: str = None,
        approver_role_id: int = None,
        approver_user_id: int = None,
        approval_limit: Decimal = None,
        timeout_hours: int = None,
        is_required: bool = True,
        can_delegate: bool = False,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Add a step to a workflow.

        Args:
            workflow_id: Parent workflow ID
            sequence: Step sequence number
            name: Step name
            description: Step description
            approver_role_id: Role that can approve
            approver_user_id: Specific user that can approve
            approval_limit: Amount limit for this step
            timeout_hours: Hours before step expires
            is_required: Whether step is required
            can_delegate: Whether approver can delegate

        Returns:
            Tuple of (success, result)
        """
        try:
            workflow = db.session.get(ApprovalWorkflow, workflow_id)
            if not workflow:
                return False, {"error": "Workflow not found"}

            step = ApprovalStep(
                workflow_id=workflow_id,
                sequence=sequence,
                name=name,
                description=description,
                approver_role_id=approver_role_id,
                approver_user_id=approver_user_id,
                approval_limit=approval_limit,
                timeout_hours=timeout_hours,
                is_required=is_required,
                can_delegate=can_delegate,
            )
            db.session.add(step)
            db.session.commit()
            return True, step.to_dict()
        except Exception as e:
            db.session.rollback()
            return False, {"error": str(e)}

    @staticmethod
    def create_approval_request(
        workflow_id: int,
        entity_type: str,
        entity_id: int,
        amount: Decimal = None,
        description: str = None,
        requester_id: int = None,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Create an approval request for an entity.

        Args:
            workflow_id: Workflow to use
            entity_type: Type of entity
            entity_id: ID of entity
            amount: Transaction amount
            description: Request description
            requester_id: User making request

        Returns:
            Tuple of (success, result)
        """
        try:
            workflow = db.session.get(ApprovalWorkflow, workflow_id)
            if not workflow:
                return False, {"error": "Workflow not found"}

            if not workflow.is_active:
                return False, {"error": "Workflow is not active"}

            if workflow.auto_approve_below and amount and amount < workflow.auto_approve_below:
                request_no = ApprovalRequest.generate_request_no(entity_type)
                request = ApprovalRequest(
                    request_no=request_no,
                    workflow_id=workflow_id,
                    entity_type=entity_type,
                    entity_id=entity_id,
                    amount=amount,
                    description=description,
                    requester_id=requester_id or 1,
                    status=WorkflowStatus.APPROVED,
                    completed_at=utc_now(),
                )
            else:
                request_no = ApprovalRequest.generate_request_no(entity_type)
                request = ApprovalRequest(
                    request_no=request_no,
                    workflow_id=workflow_id,
                    entity_type=entity_type,
                    entity_id=entity_id,
                    amount=amount,
                    description=description,
                    requester_id=requester_id or 1,
                    status=WorkflowStatus.PENDING,
                    current_step_sequence=1,
                )

            db.session.add(request)
            db.session.commit()
            return True, request.to_dict()
        except Exception as e:
            db.session.rollback()
            return False, {"error": str(e)}

    @staticmethod
    def process_approval(
        request_id: int,
        approver_id: int,
        is_approved: bool,
        comments: str = None,
        delegated_from_id: int = None,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Process an approval decision.

        Args:
            request_id: Approval request ID
            approver_id: User approving/rejecting
            is_approved: True if approved, False if rejected
            comments: Approver comments
            delegated_from_id: Original approver if delegated

        Returns:
            Tuple of (success, result)
        """
        try:
            request = db.session.get(ApprovalRequest, request_id)
            if not request:
                return False, {"error": "Request not found"}

            if request.status != WorkflowStatus.PENDING:
                return False, {"error": "Request is not pending"}

            current_step = request.get_current_step()
            if not current_step:
                return False, {"error": "No current step found"}

            action = ApprovalAction(
                request_id=request_id,
                step_id=current_step.id,
                approver_id=approver_id,
                is_approved=is_approved,
                comments=comments,
                delegated_from_id=delegated_from_id,
            )
            db.session.add(action)

            if is_approved:
                if request.advance_step():
                    pass
                else:
                    request.status = WorkflowStatus.APPROVED
                    request.completed_at = utc_now()
            else:
                request.status = WorkflowStatus.REJECTED
                request.completed_at = utc_now()

            db.session.commit()
            return True, request.to_dict()
        except Exception as e:
            db.session.rollback()
            return False, {"error": str(e)}

    @staticmethod
    def cancel_request(request_id: int) -> Tuple[bool, str]:
        """
        Cancel an approval request.

        Args:
            request_id: Request to cancel

        Returns:
            Tuple of (success, message)
        """
        try:
            request = db.session.get(ApprovalRequest, request_id)
            if not request:
                return False, "Request not found"

            if request.status == WorkflowStatus.APPROVED:
                return False, "Cannot cancel approved request"

            request.status = WorkflowStatus.CANCELLED
            request.completed_at = utc_now()
            db.session.commit()
            return True, "Request cancelled successfully"
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def get_workflow_by_entity(entity_type: str) -> Optional[ApprovalWorkflow]:
        """Get active workflow for entity type."""
        return ApprovalWorkflow.query.filter_by(
            entity_type=entity_type,
            is_active=True
        ).first()

    @staticmethod
    def get_pending_requests_for_user(user_id: int, role_ids: List[int] = None) -> List[ApprovalRequest]:
        """
        Get pending approval requests for a user.

        Args:
            user_id: User ID
            role_ids: List of role IDs for user

        Returns:
            List of pending requests
        """
        requests = ApprovalRequest.query.filter_by(
            status=WorkflowStatus.PENDING
        ).all()

        pending = []
        for request in requests:
            current_step = request.get_current_step()
            if current_step:
                if current_step.approver_user_id == user_id:
                    pending.append(request)
                elif role_ids and current_step.approver_role_id in role_ids:
                    pending.append(request)

        return pending

    @staticmethod
    def get_request_history(
        entity_type: str = None,
        entity_id: int = None,
        requester_id: int = None,
        status: str = None,
    ) -> List[ApprovalRequest]:
        """
        Get approval request history with filters.

        Args:
            entity_type: Filter by entity type
            entity_id: Filter by entity ID
            requester_id: Filter by requester
            status: Filter by status

        Returns:
            List of requests
        """
        query = ApprovalRequest.query

        if entity_type:
            query = query.filter_by(entity_type=entity_type)
        if entity_id:
            query = query.filter_by(entity_id=entity_id)
        if requester_id:
            query = query.filter_by(requester_id=requester_id)
        if status:
            query = query.filter_by(status=status)

        return query.order_by(ApprovalRequest.requested_at.desc()).all()

    @staticmethod
    def get_workflow_statistics(workflow_id: int = None) -> Dict[str, Any]:
        """
        Get statistics for workflow(s).

        Args:
            workflow_id: Specific workflow or None for all

        Returns:
            Dictionary of statistics
        """
        query = ApprovalRequest.query
        if workflow_id:
            query = query.filter_by(workflow_id=workflow_id)

        total = query.count()
        pending = query.filter_by(status=WorkflowStatus.PENDING).count()
        approved = query.filter_by(status=WorkflowStatus.APPROVED).count()
        rejected = query.filter_by(status=WorkflowStatus.REJECTED).count()
        cancelled = query.filter_by(status=WorkflowStatus.CANCELLED).count()

        return {
            "total": total,
            "pending": pending,
            "approved": approved,
            "rejected": rejected,
            "cancelled": cancelled,
            "approval_rate": (approved / total * 100) if total > 0 else 0,
        }
