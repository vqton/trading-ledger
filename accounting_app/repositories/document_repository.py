from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional, Tuple

from core.database import db
from models.document import Document, DocumentAttachment, DocumentTemplate, DocumentType


class DocumentRepository:
    """Repository for Document, DocumentAttachment, DocumentTemplate."""

    @staticmethod
    def get_document_by_id(document_id: int) -> Optional[Document]:
        """Get document by ID."""
        return db.session.get(Document, document_id)

    @staticmethod
    def get_document_by_no(document_no: str) -> Optional[Document]:
        """Get document by document number."""
        return Document.query.filter_by(document_no=document_no).first()

    @staticmethod
    def get_documents(page: int = 1, per_page: int = 20, document_type: str = None, status: str = None, start_date: date = None, end_date: date = None) -> Tuple[List[Document], int]:
        """Get paginated documents."""
        query = Document.query

        if document_type:
            query = query.filter(Document.document_type == document_type)
        if status:
            query = query.filter(Document.status == status)
        if start_date:
            query = query.filter(Document.document_date >= start_date)
        if end_date:
            query = query.filter(Document.document_date <= end_date)

        query = query.order_by(Document.document_date.desc(), Document.document_no.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        return pagination.items, pagination.total

    @staticmethod
    def create_document(document_no: str, document_type: str, document_date: date, created_by: int, reference_no: str = None, reference_date: date = None, entity_type: str = None, entity_id: int = None, voucher_id: int = None, amount: Decimal = None, currency: str = "VND", exchange_rate: Decimal = Decimal("1.0000"), description: str = None) -> Document:
        """Create a new document."""
        document = Document(
            document_no=document_no,
            document_type=document_type,
            document_date=document_date,
            reference_no=reference_no,
            reference_date=reference_date,
            entity_type=entity_type,
            entity_id=entity_id,
            voucher_id=voucher_id,
            amount=amount,
            currency=currency,
            exchange_rate=exchange_rate,
            description=description,
            created_by=created_by,
        )
        db.session.add(document)
        db.session.commit()
        return document

    @staticmethod
    def add_attachment(document_id: int, filename: str, original_filename: str, file_path: str, file_type: str = None, file_size: int = None, mime_type: str = None, uploaded_by: int = None) -> DocumentAttachment:
        """Add attachment to document."""
        attachment = DocumentAttachment(
            document_id=document_id,
            filename=filename,
            original_filename=original_filename,
            file_path=file_path,
            file_type=file_type,
            file_size=file_size,
            mime_type=mime_type,
            uploaded_by=uploaded_by,
        )
        db.session.add(attachment)

        document = db.session.get(Document, document_id)
        document.attachment_count += 1

        db.session.commit()
        return attachment

    @staticmethod
    def get_template_by_id(template_id: int) -> Optional[DocumentTemplate]:
        """Get template by ID."""
        return db.session.get(DocumentTemplate, template_id)

    @staticmethod
    def get_templates(page: int = 1, per_page: int = 20, document_type: str = None, is_active: bool = None) -> Tuple[List[DocumentTemplate], int]:
        """Get paginated templates."""
        query = DocumentTemplate.query

        if document_type:
            query = query.filter(DocumentTemplate.document_type == document_type)
        if is_active is not None:
            query = query.filter(DocumentTemplate.is_active == is_active)

        query = query.order_by(DocumentTemplate.code)
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        return pagination.items, pagination.total

    @staticmethod
    def create_template(code: str, name: str, document_type: str, created_by: int, description: str = None, template_content: str = None, required_fields: dict = None, optional_fields: dict = None, validation_rules: dict = None) -> DocumentTemplate:
        """Create a new document template."""
        template = DocumentTemplate(
            code=code,
            name=name,
            document_type=document_type,
            description=description,
            template_content=template_content,
            required_fields=required_fields,
            optional_fields=optional_fields,
            validation_rules=validation_rules,
            created_by=created_by,
        )
        db.session.add(template)
        db.session.commit()
        return template

    @staticmethod
    def get_document_attachments(document_id: int) -> List[DocumentAttachment]:
        """Get all attachments for a document."""
        return DocumentAttachment.query.filter_by(document_id=document_id).all()
