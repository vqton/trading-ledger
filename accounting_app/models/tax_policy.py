"""
Tax Policy Model - Store tax rates by year and type.
Based on Circular 99/2025/TT-BTC for Vietnamese accounting standards.
"""

from datetime import datetime
from decimal import Decimal
from core.database import db


class TaxPolicy(db.Model):
    """Tax policy for CIT, VAT, etc. by year."""
    
    __tablename__ = "tax_policies"
    
    id = db.Column(db.Integer, primary_key=True)
    tax_type = db.Column(db.String(20), nullable=False, index=True)  # 'cit', 'vat', 'vat_input', 'vat_output'
    year = db.Column(db.Integer, nullable=False, index=True)
    rate = db.Column(db.Numeric(5, 4), nullable=False)  # e.g., 0.20 for 20%
    rate_name = db.Column(db.String(100), nullable=True)  # e.g., "Thuế suất thu nhập doanh nghiệp"
    active = db.Column(db.Boolean, default=True, nullable=False)
    description = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        db.Index("ix_tax_policies_type_year", "tax_type", "year"),
        db.UniqueConstraint("tax_type", "year", name="uq_tax_policy_type_year"),
    )
    
    def __repr__(self) -> str:
        return f"<TaxPolicy {self.tax_type} {self.year} {self.rate}>"
    
    @property
    def rate_percentage(self) -> int:
        """Get rate as percentage (e.g., 20 for 20%)."""
        return int(self.rate * 100)
    
    @property
    def is_current(self) -> bool:
        """Check if this policy is for current year."""
        from datetime import date
        return self.year == date.today().year


class TaxPolicyType:
    """Tax policy type constants."""
    
    CIT = "cit"           # Corporate Income Tax
    VAT = "vat"           # General VAT
    VAT_INPUT = "vat_input"    # VAT Input
    VAT_OUTPUT = "vat_output"  # VAT Output
    PIT = "pit"           # Personal Income Tax
    
    CHOICES = [
        (CIT, "Thuế TNDN"),
        (VAT, "Thuế GTGT"),
        (VAT_INPUT, "Thuế GTGT vào"),
        (VAT_OUTPUT, "Thuế GTGT ra"),
        (PIT, "Thuế TNCN"),
    ]


def get_active_policy(tax_type: str, year: int) -> TaxPolicy:
    """Get active tax policy for a type and year."""
    return TaxPolicy.query.filter_by(
        tax_type=tax_type,
        year=year,
        active=True
    ).first()


def get_or_create_default_cit_policy(year: int) -> TaxPolicy:
    """Get or create default CIT policy for a year."""
    policy = get_active_policy(TaxPolicyType.CIT, year)
    
    if not policy:
        policy = TaxPolicy(
            tax_type=TaxPolicyType.CIT,
            year=year,
            rate=Decimal("0.20"),
            rate_name="Thuế suất thu nhập doanh nghiệp",
            active=True,
            description=f"Thuế suất TNDN theo quy định - Áp dụng năm {year}"
        )
        db.session.add(policy)
        db.session.commit()
    
    return policy
