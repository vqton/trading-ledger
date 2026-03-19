"""
Document Service - Business logic for document management.
Handles document creation, attachments, and templates.
"""

import os
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any, Tuple

from core.database import db
from core.utils import utc_now
from models.document import (
    Document,
    DocumentAttachment,
    DocumentTemplate,
    DocumentType,
    DocumentStatus,
    ApprovalStatus,
)


class DocumentService:
    """Service for managing documents."""

    @staticmethod
    def create_document(
        document_type: str,
        document_date: datetime,
        entity_type: str = None,
        entity_id: int = None,
        voucher_id: int = None,
        reference_no: str = None,
        reference_date: datetime = None,
        amount: Decimal = None,
        currency: str = "VND",
        exchange_rate: Decimal = None,
        description: str = None,
        status: str = DocumentStatus.DRAFT,
        created_by: int = None,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Create a new document.

        Args:
            document_type: Type of document
            document_date: Document date
            entity_type: Related entity type
            entity_id: Related entity ID
            voucher_id: Related voucher ID
            reference_no: Reference number
            reference_date: Reference date
            amount: Document amount
            currency: Currency code
            exchange_rate: Exchange rate
            description: Document description
            status: Document status
            created_by: Creator user ID

        Returns:
            Tuple of (success, result)
        """
        try:
            document_no = Document.generate_document_no(document_type)

            document = Document(
                document_no=document_no,
                document_type=document_type,
                document_date=document_date,
                entity_type=entity_type,
                entity_id=entity_id,
                voucher_id=voucher_id,
                reference_no=reference_no,
                reference_date=reference_date,
                amount=amount or Decimal("0"),
                currency=currency,
                exchange_rate=exchange_rate or Decimal("1"),
                description=description,
                status=status,
                approval_status=ApprovalStatus.PENDING,
                created_by=created_by or 1,
            )
            db.session.add(document)
            db.session.commit()
            return True, document.to_dict()
        except Exception as e:
            db.session.rollback()
            return False, {"error": str(e)}

    @staticmethod
    def add_attachment(
        document_id: int,
        filename: str,
        file_data: bytes,
        file_type: str = None,
        mime_type: str = None,
        file_size: int = None,
        description: str = None,
        uploaded_by: int = None,
        upload_path: str = None,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Add attachment to document.

        Args:
            document_id: Parent document ID
            filename: Original filename
            file_data: File content
            file_type: File type/category
            mime_type: MIME type
            file_size: File size in bytes
            description: File description
            uploaded_by: Uploader user ID
            upload_path: Directory to save file

        Returns:
            Tuple of (success, result)
        """
        try:
            document = db.session.get(Document, document_id)
            if not document:
                return False, {"error": "Document not found"}

            ext = os.path.splitext(filename)[1]
            stored_filename = f"{uuid.uuid4()}{ext}"

            if upload_path:
                os.makedirs(upload_path, exist_ok=True)
                file_path = os.path.join(upload_path, stored_filename)
                with open(file_path, "wb") as f:
                    f.write(file_data)
            else:
                file_path = stored_filename

            attachment = DocumentAttachment(
                document_id=document_id,
                filename=stored_filename,
                original_filename=filename,
                file_path=file_path,
                file_type=file_type,
                mime_type=mime_type,
                file_size=file_size or len(file_data),
                description=description,
                uploaded_by=uploaded_by or 1,
            )
            db.session.add(attachment)

            document.attachment_count += 1
            db.session.commit()

            return True, attachment.to_dict()
        except Exception as e:
            db.session.rollback()
            return False, {"error": str(e)}

    @staticmethod
    def delete_attachment(attachment_id: int) -> Tuple[bool, str]:
        """
        Delete attachment from document.

        Args:
            attachment_id: Attachment ID

        Returns:
            Tuple of (success, message)
        """
        try:
            attachment = db.session.get(DocumentAttachment, attachment_id)
            if not attachment:
                return False, "Attachment not found"

            document = attachment.document
            if os.path.exists(attachment.file_path):
                os.remove(attachment.file_path)

            document.attachment_count = max(0, document.attachment_count - 1)

            db.session.delete(attachment)
            db.session.commit()

            return True, "Attachment deleted successfully"
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def update_document_status(
        document_id: int,
        status: str,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Update document status.

        Args:
            document_id: Document ID
            status: New status

        Returns:
            Tuple of (success, result)
        """
        try:
            document = db.session.get(Document, document_id)
            if not document:
                return False, {"error": "Document not found"}

            document.status = status
            db.session.commit()
            return True, document.to_dict()
        except Exception as e:
            db.session.rollback()
            return False, {"error": str(e)}

    @staticmethod
    def approve_document(
        document_id: int,
        approver_id: int,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Approve document.

        Args:
            document_id: Document ID
            approver_id: Approver user ID

        Returns:
            Tuple of (success, result)
        """
        try:
            document = db.session.get(Document, document_id)
            if not document:
                return False, {"error": "Document not found"}

            document.approval_status = ApprovalStatus.APPROVED
            document.signed_by = approver_id
            document.signed_at = utc_now()
            db.session.commit()

            return True, document.to_dict()
        except Exception as e:
            db.session.rollback()
            return False, {"error": str(e)}

    @staticmethod
    def sign_document(
        document_id: int,
        signer_id: int,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Sign document.

        Args:
            document_id: Document ID
            signer_id: Signer user ID

        Returns:
            Tuple of (success, result)
        """
        try:
            document = db.session.get(Document, document_id)
            if not document:
                return False, {"error": "Document not found"}

            document.status = DocumentStatus.SIGNED
            document.signed_by = signer_id
            document.signed_at = utc_now()
            db.session.commit()

            return True, document.to_dict()
        except Exception as e:
            db.session.rollback()
            return False, {"error": str(e)}

    @staticmethod
    def create_template(
        code: str,
        name: str,
        document_type: str,
        description: str = None,
        template_content: str = None,
        required_fields: List[Dict] = None,
        optional_fields: List[Dict] = None,
        validation_rules: List[Dict] = None,
        created_by: int = None,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Create document template.

        Args:
            code: Template code
            name: Template name
            document_type: Document type
            description: Template description
            template_content: HTML template content
            required_fields: List of required fields
            optional_fields: List of optional fields
            validation_rules: Validation rules
            created_by: Creator user ID

        Returns:
            Tuple of (success, result)
        """
        try:
            template = DocumentTemplate(
                code=code,
                name=name,
                document_type=document_type,
                description=description,
                template_content=template_content,
                required_fields=required_fields,
                optional_fields=optional_fields,
                validation_rules=validation_rules,
                created_by=created_by or 1,
            )
            db.session.add(template)
            db.session.commit()
            return True, template.to_dict()
        except Exception as e:
            db.session.rollback()
            return False, {"error": str(e)}

    @staticmethod
    def validate_document_data(
        template_id: int,
        data: Dict[str, Any],
    ) -> Tuple[bool, List[str], List[str]]:
        """
        Validate document data against template.

        Args:
            template_id: Template ID
            data: Data to validate

        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        try:
            template = db.session.get(DocumentTemplate, template_id)
            if not template:
                return False, ["Template not found"], []

            errors, warnings = template.validate_data(data)
            return len(errors) == 0, errors, warnings
        except Exception as e:
            return False, [str(e)], []

    @staticmethod
    def get_documents_by_type(
        document_type: str,
        status: str = None,
        start_date: datetime = None,
        end_date: datetime = None,
    ) -> List[Document]:
        """
        Get documents by type with filters.

        Args:
            document_type: Document type
            status: Filter by status
            start_date: Filter start date
            end_date: Filter end date

        Returns:
            List of documents
        """
        query = Document.query.filter_by(document_type=document_type)

        if status:
            query = query.filter_by(status=status)
        if start_date:
            query = query.filter(Document.document_date >= start_date)
        if end_date:
            query = query.filter(Document.document_date <= end_date)

        return query.order_by(Document.document_date.desc()).all()

    @staticmethod
    def get_document_statistics() -> Dict[str, Any]:
        """
        Get document statistics.

        Returns:
            Dictionary of statistics
        """
        total = Document.query.count()
        by_status = {}
        for status_choice in DocumentStatus.CHOICES:
            status_value = status_choice[0]
            count = Document.query.filter_by(status=status_value).count()
            by_status[status_value] = count

        by_type = {}
        for doc_type in DocumentType.CHOICES:
            type_value = doc_type[0]
            count = Document.query.filter_by(document_type=type_value).count()
            by_type[type_value] = count

        return {
            "total": total,
            "by_status": by_status,
            "by_type": by_type,
        }
