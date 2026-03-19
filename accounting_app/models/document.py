from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List

from core.database import db
from core.utils import utc_now


class DocumentType:
    """Document type constants per Phụ lục I TT99."""

    PHIEU_THU = "pt"
    PHIEU_CHI = "pc"
    PHIEU_NHAP_KHO = "pnk"
    PHIEU_XUAT_KHO = "pxk"
    HOA_DON = "hd"
    BIEN_BAN = "bb"
    GIAY_BAO_NO = "gbn"
    GIAY_BAO_CO = "gbc"
    GIAY_BAO_NHAN = "gbh"
    UNG_TRUOC = "ut"
    PHAI_TRA = "ptra"
    CHUNG_TU_KHAC = "ctk"

    CHOICES = [
        (PHIEU_THU, "Phiếu thu"),
        (PHIEU_CHI, "Phiếu chi"),
        (PHIEU_NHAP_KHO, "Phiếu nhập kho"),
        (PHIEU_XUAT_KHO, "Phiếu xuất kho"),
        (HOA_DON, "Hóa đơn"),
        (BIEN_BAN, "Biên bản"),
        (GIAY_BAO_NO, "Giấy báo Nợ"),
        (GIAY_BAO_CO, "Giấy báo Có"),
        (GIAY_BAO_NHAN, "Giấy báo Nhận"),
        (UNG_TRUOC, "Ủng trước"),
        (PHAI_TRA, "Phải trả"),
        (CHUNG_TU_KHAC, "Chứng từ khác"),
    ]

    PREFIXES = {
        PHIEU_THU: "PT",
        PHIEU_CHI: "PC",
        PHIEU_NHAP_KHO: "PNK",
        PHIEU_XUAT_KHO: "PXK",
        HOA_DON: "HD",
        BIEN_BAN: "BB",
        GIAY_BAO_NO: "GBN",
        GIAY_BAO_CO: "GBC",
        GIAY_BAO_NHAN: "GBH",
        UNG_TRUOC: "UT",
        PHAI_TRA: "PTRA",
        CHUNG_TU_KHAC: "CTK",
    }


class Document(db.Model):
    """Document model for accounting documents per Phụ lục I TT99.

    Tracks various document types used in Vietnamese accounting.
    """

    __tablename__ = "documents"

    id = db.Column(db.Integer, primary_key=True)
    document_no = db.Column(db.String(50), unique=True, nullable=False, index=True)
    document_type = db.Column(db.String(10), nullable=False, index=True)
    document_date = db.Column(db.Date, nullable=False, index=True)
    reference_no = db.Column(db.String(100), nullable=True)
    reference_date = db.Column(db.Date, nullable=True)
    entity_type = db.Column(db.String(50), nullable=True)
    entity_id = db.Column(db.Integer, nullable=True)
    voucher_id = db.Column(db.Integer, db.ForeignKey("journal_vouchers.id"), nullable=True)
    amount = db.Column(db.Numeric(18, 2), default=Decimal("0.00"))
    currency = db.Column(db.String(3), default="VND")
    exchange_rate = db.Column(db.Numeric(18, 4), default=Decimal("1.0000"))
    description = db.Column(db.String(500), nullable=True)
    attachment_count = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default="draft", nullable=False, index=True)
    approval_status = db.Column(db.String(20), default="pending", nullable=False, index=True)
    approval_request_id = db.Column(db.Integer, nullable=True)
    signed_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    signed_at = db.Column(db.DateTime, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    creator = db.relationship("User", backref="documents", foreign_keys=[created_by])
    signer = db.relationship("User", backref="signed_documents", foreign_keys=[signed_by])
    voucher = db.relationship("JournalVoucher", backref="documents")
    attachments = db.relationship("DocumentAttachment", backref="document", lazy="dynamic")

    __table_args__ = (
        db.Index("ix_document_date_type", "document_date", "document_type"),
        db.Index("ix_document_entity", "entity_type", "entity_id"),
    )

    def __repr__(self) -> str:
        return f"<Document {self.document_no} - {self.document_type}>"

    @property
    def total_amount_vnd(self) -> Decimal:
        """Get total amount in VND."""
        if self.currency == "VND":
            return self.amount
        return self.amount * self.exchange_rate

    @property
    def is_approved(self) -> bool:
        """Check if document is approved."""
        return self.approval_status == "approved"

    @property
    def is_signed(self) -> bool:
        """Check if document is signed."""
        return self.signed_at is not None

    def add_attachment(self, filename: str, file_path: str, file_type: str = None) -> "DocumentAttachment":
        """Add attachment to document."""
        attachment = DocumentAttachment(
            document_id=self.id,
            filename=filename,
            file_path=file_path,
            file_type=file_type,
        )
        db.session.add(attachment)
        self.attachment_count += 1
        db.session.commit()
        return attachment

    @classmethod
    def generate_document_no(cls, document_type: str) -> str:
        """Generate document number based on type."""
        year = datetime.now().year
        month = datetime.now().month
        prefix = DocumentType.PREFIXES.get(document_type, "DOC")

        last_doc = cls.query.filter(
            cls.document_type == document_type,
            cls.document_no.like(f"{prefix}-{year}%")
        ).order_by(cls.document_no.desc()).first()

        if last_doc:
            last_num = int(last_doc.document_no.split("-")[-1])
            new_num = last_num + 1
        else:
            new_num = 1

        return f"{prefix}-{year}{month:02d}-{new_num:05d}"

    def to_dict(self) -> dict:
        """Convert document to dictionary."""
        return {
            "id": self.id,
            "document_no": self.document_no,
            "document_type": self.document_type,
            "document_date": self.document_date.isoformat() if self.document_date else None,
            "reference_no": self.reference_no,
            "reference_date": self.reference_date.isoformat() if self.reference_date else None,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "voucher_id": self.voucher_id,
            "amount": float(self.amount) if self.amount else 0.0,
            "currency": self.currency,
            "exchange_rate": float(self.exchange_rate) if self.exchange_rate else 1.0,
            "total_amount_vnd": float(self.total_amount_vnd),
            "description": self.description,
            "attachment_count": self.attachment_count,
            "status": self.status,
            "approval_status": self.approval_status,
            "approval_request_id": self.approval_request_id,
            "is_signed": self.is_signed,
            "signed_at": self.signed_at.isoformat() if self.signed_at else None,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class DocumentAttachment(db.Model):
    """Document Attachment model for supporting documents."""

    __tablename__ = "document_attachments"

    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey("documents.id"), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(50), nullable=True)
    file_size = db.Column(db.Integer, nullable=True)
    mime_type = db.Column(db.String(100), nullable=True)
    description = db.Column(db.String(500), nullable=True)
    uploaded_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=utc_now, nullable=False)

    uploader = db.relationship("User", backref="uploaded_attachments")

    def __repr__(self) -> str:
        return f"<DocumentAttachment {self.filename}>"

    def to_dict(self) -> dict:
        """Convert attachment to dictionary."""
        return {
            "id": self.id,
            "document_id": self.document_id,
            "filename": self.filename,
            "original_filename": self.original_filename,
            "file_path": self.file_path,
            "file_type": self.file_type,
            "file_size": self.file_size,
            "mime_type": self.mime_type,
            "description": self.description,
            "uploaded_by": self.uploaded_by,
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None,
        }


class DocumentTemplate(db.Model):
    """Document Template model for standardized documents."""

    __tablename__ = "document_templates"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    document_type = db.Column(db.String(10), nullable=False, index=True)
    description = db.Column(db.String(500), nullable=True)
    template_content = db.Column(db.Text, nullable=True)
    required_fields = db.Column(db.JSON, nullable=True)
    optional_fields = db.Column(db.JSON, nullable=True)
    validation_rules = db.Column(db.JSON, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    creator = db.relationship("User", backref="document_templates")

    def __repr__(self) -> str:
        return f"<DocumentTemplate {self.code} - {self.name}>"

    def validate_data(self, data: dict) -> tuple:
        """Validate data against template rules."""
        errors = []
        warnings = []

        if self.required_fields:
            for field in self.required_fields:
                field_name = field.get("name")
                if field_name not in data or not data[field_name]:
                    errors.append(f"Trường '{field_name}' là bắt buộc")

        if self.validation_rules:
            for rule in self.validation_rules:
                field_name = rule.get("field")
                rule_type = rule.get("type")
                value = data.get(field_name)

                if rule_type == "min_length" and value and len(str(value)) < rule.get("value", 0):
                    errors.append(f"'{field_name}' phải có ít nhất {rule.get('value')} ký tự")
                elif rule_type == "max_length" and value and len(str(value)) > rule.get("value", 0):
                    errors.append(f"'{field_name}' không được quá {rule.get('value')} ký tự")
                elif rule_type == "min_value" and value and float(value) < rule.get("value", 0):
                    errors.append(f"'{field_name}' phải lớn hơn hoặc bằng {rule.get('value')}")
                elif rule_type == "max_value" and value and float(value) > rule.get("value", 0):
                    errors.append(f"'{field_name}' không được lớn hơn {rule.get('value')}")

        return errors, warnings

    @classmethod
    def generate_code(cls, document_type: str) -> str:
        """Generate template code."""
        prefix = DocumentType.PREFIXES.get(document_type, "TMP")
        return f"{prefix}-TPL"

    def to_dict(self) -> dict:
        """Convert template to dictionary."""
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "document_type": self.document_type,
            "description": self.description,
            "required_fields": self.required_fields,
            "optional_fields": self.optional_fields,
            "validation_rules": self.validation_rules,
            "is_active": self.is_active,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class DocumentStatus:
    """Document status constants."""

    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    SIGNED = "signed"
    CANCELLED = "cancelled"

    CHOICES = [
        (DRAFT, "Nháp"),
        (PENDING, "Chờ duyệt"),
        (APPROVED, "Đã duyệt"),
        (REJECTED, "Từ chối"),
        (SIGNED, "Đã ký"),
        (CANCELLED, "Hủy"),
    ]


class ApprovalStatus:
    """Approval status constants."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    SKIPPED = "skipped"

    CHOICES = [
        (PENDING, "Chờ duyệt"),
        (APPROVED, "Đã duyệt"),
        (REJECTED, "Từ chối"),
        (SKIPPED, "Bỏ qua"),
    ]
