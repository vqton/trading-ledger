"""
Tests for Document Service - Document management.
"""

import pytest
from datetime import date
from decimal import Decimal

from app import create_app
from core.database import db
from services.document_service import DocumentService
from models.document import (
    Document,
    DocumentTemplate,
    DocumentType,
    DocumentStatus,
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


class TestDocument:
    """Tests for document management."""

    def test_create_document(self, app):
        """Test creating a new document."""
        with app.app_context():
            success, result = DocumentService.create_document(
                document_type=DocumentType.HOA_DON,
                document_date=date.today(),
                amount=Decimal("11000000"),
                description="Sales invoice",
                created_by=1,
            )

            assert success is True
            assert result["document_type"] == DocumentType.HOA_DON
            assert result["amount"] == 11000000
            assert result["status"] == DocumentStatus.DRAFT

    def test_generate_document_no(self, app):
        """Test document number generation."""
        with app.app_context():
            success1, result1 = DocumentService.create_document(
                document_type=DocumentType.PHIEU_THU,
                document_date=date.today(),
                created_by=1,
            )

            success2, result2 = DocumentService.create_document(
                document_type=DocumentType.PHIEU_THU,
                document_date=date.today(),
                created_by=1,
            )

            assert success1 is True
            assert success2 is True
            assert result1["document_no"] != result2["document_no"]

    def test_update_document_status(self, app):
        """Test updating document status."""
        with app.app_context():
            success, doc = DocumentService.create_document(
                document_type=DocumentType.HOA_DON,
                document_date=date.today(),
                created_by=1,
            )

            success, result = DocumentService.update_document_status(
                document_id=doc["id"],
                status=DocumentStatus.APPROVED,
            )

            assert success is True
            assert result["status"] == DocumentStatus.APPROVED

    def test_approve_document(self, app):
        """Test approving a document."""
        with app.app_context():
            success, doc = DocumentService.create_document(
                document_type=DocumentType.HOA_DON,
                document_date=date.today(),
                created_by=1,
            )

            success, result = DocumentService.approve_document(
                document_id=doc["id"],
                approver_id=1,
            )

            assert success is True

    def test_sign_document(self, app):
        """Test signing a document."""
        with app.app_context():
            success, doc = DocumentService.create_document(
                document_type=DocumentType.HOA_DON,
                document_date=date.today(),
                created_by=1,
            )

            success, result = DocumentService.sign_document(
                document_id=doc["id"],
                signer_id=1,
            )

            assert success is True
            assert result["status"] == DocumentStatus.SIGNED


class TestDocumentTemplate:
    """Tests for document templates."""

    def test_create_template(self, app):
        """Test creating a document template."""
        with app.app_context():
            success, result = DocumentService.create_template(
                code="TMP-HD-001",
                name="Sales Invoice Template",
                document_type=DocumentType.HOA_DON,
                description="Standard sales invoice template",
                required_fields=[
                    {"name": "customer_name", "type": "string", "required": True},
                    {"name": "amount", "type": "number", "required": True},
                ],
                created_by=1,
            )

            assert success is True
            assert result["code"] == "TMP-HD-001"
            assert result["document_type"] == DocumentType.HOA_DON

    def test_validate_document_data(self, app):
        """Test validating document data against template."""
        with app.app_context():
            success, template = DocumentService.create_template(
                code="TMP-TEST",
                name="Test Template",
                document_type=DocumentType.HOA_DON,
                required_fields=[
                    {"name": "customer_name", "type": "string"},
                ],
                created_by=1,
            )

            valid, errors, warnings = DocumentService.validate_document_data(
                template_id=template["id"],
                data={"customer_name": "Test Customer"},
            )

            assert valid is True
            assert len(errors) == 0


class TestDocumentStatistics:
    """Tests for document statistics."""

    def test_get_document_statistics(self, app):
        """Test getting document statistics."""
        with app.app_context():
            DocumentService.create_document(
                document_type=DocumentType.HOA_DON,
                document_date=date.today(),
                created_by=1,
            )
            DocumentService.create_document(
                document_type=DocumentType.PHIEU_THU,
                document_date=date.today(),
                created_by=1,
            )

            stats = DocumentService.get_document_statistics()

            assert stats["total"] >= 2
            assert "by_type" in stats
            assert "by_status" in stats
