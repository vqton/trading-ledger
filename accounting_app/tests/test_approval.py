"""
Tests for Approval Service - Workflow creation and approval processing.
"""

import pytest
from datetime import date
from decimal import Decimal

from app import create_app
from core.database import db
from services.approval_service import ApprovalService
from models.approval_workflow import (
    ApprovalWorkflow,
    ApprovalStep,
    ApprovalRequest,
    ApprovalAction,
    WorkflowStatus,
    EntityType,
)


@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def workflow(app):
    """Create test workflow."""
    with app.app_context():
        wf = ApprovalWorkflow(
            code="WF-TEST",
            name="Test Workflow",
            entity_type=EntityType.VOUCHER,
            approval_levels=2,
            is_active=True,
            created_by=1,
        )
        db.session.add(wf)
        db.session.commit()

        step1 = ApprovalStep(
            workflow_id=wf.id,
            sequence=1,
            name="Manager Approval",
            is_required=True,
        )
        step2 = ApprovalStep(
            workflow_id=wf.id,
            sequence=2,
            name="Director Approval",
            is_required=True,
        )
        db.session.add_all([step1, step2])
        db.session.commit()

        return wf.id


class TestApprovalWorkflow:
    """Tests for approval workflow creation."""

    def test_create_workflow(self, app):
        """Test creating a new approval workflow."""
        with app.app_context():
            success, result = ApprovalService.create_workflow(
                code="WF-NEW",
                name="New Workflow",
                entity_type=EntityType.PAYMENT,
                description="Test workflow",
                approval_levels=1,
                created_by=1,
            )

            assert success is True
            assert result["code"] == "WF-NEW"
            assert result["name"] == "New Workflow"
            assert result["approval_levels"] == 1

    def test_create_workflow_with_auto_approve(self, app):
        """Test creating workflow with auto-approve threshold."""
        with app.app_context():
            success, result = ApprovalService.create_workflow(
                code="WF-AUTO",
                name="Auto Approve Workflow",
                entity_type=EntityType.VOUCHER,
                auto_approve_below=Decimal("10000000"),
                created_by=1,
            )

            assert success is True
            assert result["auto_approve_below"] == 10000000

    def test_add_workflow_step(self, app, workflow):
        """Test adding step to workflow."""
        with app.app_context():
            success, result = ApprovalService.add_workflow_step(
                workflow_id=workflow,
                sequence=3,
                name="Finance Approval",
                description="Finance team approval",
                approval_limit=Decimal("50000000"),
                timeout_hours=48,
                is_required=True,
            )

            assert success is True
            assert result["name"] == "Finance Approval"
            assert result["sequence"] == 3


class TestApprovalRequest:
    """Tests for approval request processing."""

    def test_create_approval_request(self, app, workflow):
        """Test creating approval request."""
        with app.app_context():
            success, result = ApprovalService.create_approval_request(
                workflow_id=workflow,
                entity_type=EntityType.VOUCHER,
                entity_id=1,
                amount=Decimal("20000000"),
                description="Test voucher",
                requester_id=1,
            )

            assert success is True
            assert result["entity_type"] == EntityType.VOUCHER
            assert result["amount"] == 20000000
            assert result["status"] == WorkflowStatus.PENDING

    def test_auto_approve_below_threshold(self, app, workflow):
        """Test auto-approve when below threshold."""
        with app.app_context():
            wf = db.session.get(ApprovalWorkflow, workflow)
            wf.auto_approve_below = Decimal("50000000")
            db.session.commit()

            success, result = ApprovalService.create_approval_request(
                workflow_id=workflow,
                entity_type=EntityType.VOUCHER,
                entity_id=1,
                amount=Decimal("10000000"),
                requester_id=1,
            )

            assert success is True
            assert result["status"] == WorkflowStatus.APPROVED

    def test_process_approval_approve(self, app, workflow):
        """Test approving a request."""
        with app.app_context():
            success, req = ApprovalService.create_approval_request(
                workflow_id=workflow,
                entity_type=EntityType.VOUCHER,
                entity_id=1,
                amount=Decimal("20000000"),
                requester_id=1,
            )

            success, result = ApprovalService.process_approval(
                request_id=req["id"],
                approver_id=1,
                is_approved=True,
                comments="Approved",
            )

            assert success is True

    def test_process_approval_reject(self, app, workflow):
        """Test rejecting a request."""
        with app.app_context():
            success, req = ApprovalService.create_approval_request(
                workflow_id=workflow,
                entity_type=EntityType.VOUCHER,
                entity_id=1,
                amount=Decimal("20000000"),
                requester_id=1,
            )

            success, result = ApprovalService.process_approval(
                request_id=req["id"],
                approver_id=1,
                is_approved=False,
                comments="Rejected - insufficient documentation",
            )

            assert success is True
            assert result["status"] == WorkflowStatus.REJECTED

    def test_cancel_request(self, app, workflow):
        """Test cancelling a request."""
        with app.app_context():
            success, req = ApprovalService.create_approval_request(
                workflow_id=workflow,
                entity_type=EntityType.VOUCHER,
                entity_id=1,
                amount=Decimal("20000000"),
                requester_id=1,
            )

            success, message = ApprovalService.cancel_request(req["id"])

            assert success is True
            assert "cancelled" in message.lower()


class TestApprovalWorkflowStats:
    """Tests for workflow statistics."""

    def test_get_workflow_statistics(self, app, workflow):
        """Test getting workflow statistics."""
        with app.app_context():
            stats = ApprovalService.get_workflow_statistics(workflow)

            assert "total" in stats
            assert "pending" in stats
            assert "approved" in stats
            assert "rejected" in stats
