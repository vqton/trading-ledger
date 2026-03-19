from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List

from core.database import db
from core.utils import utc_now


class SupportingDocument(db.Model):
    """Supporting Document model for voucher attachments.

    Tracks attachments and supporting documents for journal vouchers
    per Vietnamese accounting document management requirements.
    """

    __tablename__ = "supporting_documents"

    id = db.Column(db.Integer, primary_key=True)
    document_no = db.Column(db.String(50), nullable=False, index=True)
    document_type = db.Column(db.String(50), nullable=False, index=True)
    voucher_id = db.Column(db.Integer, nullable=True, index=True)
    entity_type = db.Column(db.String(50), nullable=True)
    entity_id = db.Column(db.Integer, nullable=True)
    document_date = db.Column(db.Date, nullable=True, index=True)
    issue_date = db.Column(db.Date, nullable=True)
    expiry_date = db.Column(db.Date, nullable=True)
    description = db.Column(db.String(500), nullable=True)
    file_name = db.Column(db.String(255), nullable=True)
    file_path = db.Column(db.String(500), nullable=True)
    file_type = db.Column(db.String(50), nullable=True)
    file_size = db.Column(db.Integer, nullable=True)
    original_name = db.Column(db.String(255), nullable=True)
    document_number = db.Column(db.String(100), nullable=True)
    issuer = db.Column(db.String(200), nullable=True)
    serial_no = db.Column(db.String(100), nullable=True)
    fiscal_tax_no = db.Column(db.String(50), nullable=True)
    total_amount = db.Column(db.Numeric(18, 2), default=Decimal("0.00"))
    vat_amount = db.Column(db.Numeric(18, 2), default=Decimal("0.00"))
    status = db.Column(db.String(20), default="active", index=True)
    verified = db.Column(db.Boolean, default=False)
    verified_by = db.Column(db.Integer, nullable=True)
    verified_at = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    creator = db.relationship("User", backref="supporting_documents")

    __table_args__ = (
        db.Index("ix_doc_entity", "entity_type", "entity_id"),
        db.Index("ix_doc_type_date", "document_type", "document_date"),
        db.Index("ix_doc_status", "status"),
    )

    def __repr__(self) -> str:
        return f"<SupportingDocument {self.document_no} - {self.document_type}>"

    @property
    def is_expired(self) -> bool:
        """Check if document is expired."""
        if self.expiry_date:
            return date.today() > self.expiry_date
        return False

    @property
    def is_valid(self) -> bool:
        """Check if document is valid (active, not expired, verified)."""
        return self.status == "active" and not self.is_expired

    @classmethod
    def generate_document_no(cls, document_type: str) -> str:
        """Generate next document number."""
        year = datetime.now().year
        prefix_map = {
            "invoice": "INV",
            "receipt": "RCP",
            "contract": "CTR",
            "report": "RPT",
            "certificate": "CER",
            "other": "DOC",
        }
        prefix = prefix_map.get(document_type, "DOC")

        last_doc = cls.query.filter(
            cls.document_no.like(f"{prefix}-{year}%")
        ).order_by(cls.document_no.desc()).first()

        if last_doc:
            last_num = int(last_doc.document_no.split("-")[-1])
            new_num = last_num + 1
        else:
            new_num = 1

        return f"{prefix}-{year}-{new_num:05d}"

    @classmethod
    def get_by_voucher(cls, voucher_id: int) -> List["SupportingDocument"]:
        """Get all documents for a voucher."""
        return cls.query.filter_by(voucher_id=voucher_id).all()

    @classmethod
    def get_by_entity(cls, entity_type: str, entity_id: int) -> List["SupportingDocument"]:
        """Get all documents for an entity."""
        return cls.query.filter_by(
            entity_type=entity_type,
            entity_id=entity_id
        ).all()

    def verify(self, user_id: int) -> None:
        """Mark document as verified."""
        self.verified = True
        self.verified_by = user_id
        self.verified_at = utc_now()
        db.session.commit()

    def to_dict(self) -> dict:
        """Convert supporting document to dictionary."""
        return {
            "id": self.id,
            "document_no": self.document_no,
            "document_type": self.document_type,
            "voucher_id": self.voucher_id,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "document_date": self.document_date.isoformat() if self.document_date else None,
            "issue_date": self.issue_date.isoformat() if self.issue_date else None,
            "expiry_date": self.expiry_date.isoformat() if self.expiry_date else None,
            "description": self.description,
            "file_name": self.file_name,
            "file_path": self.file_path,
            "file_type": self.file_type,
            "file_size": self.file_size,
            "original_name": self.original_name,
            "document_number": self.document_number,
            "issuer": self.issuer,
            "serial_no": self.serial_no,
            "fiscal_tax_no": self.fiscal_tax_no,
            "total_amount": float(self.total_amount) if self.total_amount else 0.0,
            "vat_amount": float(self.vat_amount) if self.vat_amount else 0.0,
            "status": self.status,
            "verified": self.verified,
            "verified_by": self.verified_by,
            "verified_at": self.verified_at.isoformat() if self.verified_at else None,
            "is_expired": self.is_expired,
            "is_valid": self.is_valid,
            "notes": self.notes,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class DocumentType:
    """Supporting document type constants."""

    INVOICE = "invoice"
    RECEIPT = "receipt"
    CONTRACT = "contract"
    REPORT = "report"
    CERTIFICATE = "certificate"
    BANK_STATEMENT = "bank_statement"
    LEDGER = "ledger"
    OTHER = "other"

    CHOICES = [
        (INVOICE, "Hóa đơn"),
        (RECEIPT, "Biên nhận"),
        (CONTRACT, "Hợp đồng"),
        (REPORT, "Báo cáo"),
        (CERTIFICATE, "Giấy chứng nhận"),
        (BANK_STATEMENT, "Sao kê ngân hàng"),
        (LEDGER, "Sổ sách"),
        (OTHER, "Khác"),
    ]


class DocumentStatus:
    """Supporting document status constants."""

    ACTIVE = "active"
    USED = "used"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

    CHOICES = [
        (ACTIVE, "Còn hiệu lực"),
        (USED, "Đã sử dụng"),
        (CANCELLED, "Hủy bỏ"),
        (EXPIRED, "Hết hạn"),
    ]
