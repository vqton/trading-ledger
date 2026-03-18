"""
Seed tax policies based on Circular 99/2025/TT-BTC.

This script seeds default CIT (Corporate Income Tax) policies
for years 2024-2027 as per current Vietnamese tax regulations.

Note: These are default rates. For the most current rates,
always refer to the latest circular from BTC (Ministry of Finance).
"""

import os
import sys
from decimal import Decimal
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from core.database import db
from models.tax_policy import TaxPolicy, TaxPolicyType


def seed_tax_policies():
    """Seed tax policies for CIT based on Circular 99/2025/TT-BTC."""
    app = create_app("development")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///accounting.db"
    
    with app.app_context():
        existing_policies = TaxPolicy.query.filter_by(tax_type=TaxPolicyType.CIT).all()
        
        if existing_policies:
            print(f"Found {len(existing_policies)} existing CIT policies. Skipping seed.")
            return
        
        policies_data = [
            {
                "year": 2024,
                "rate": Decimal("0.20"),
                "rate_name": "Thuế suất thu nhập doanh nghiệp",
                "description": "Thuế suất TNDN theo quy định - Áp dụng năm 2024 (20%)",
            },
            {
                "year": 2025,
                "rate": Decimal("0.20"),
                "rate_name": "Thuế suất thu nhập doanh nghiệp",
                "description": "Thuế suất TNDN theo Circular 99/2025/TT-BTC - Áp dụng năm 2025 (20%)",
            },
            {
                "year": 2026,
                "rate": Decimal("0.20"),
                "rate_name": "Thuế suất thu nhập doanh nghiệp",
                "description": "Thuế suất TNDN dự kiến - Áp dụng năm 2026 (20%)",
            },
            {
                "year": 2027,
                "rate": Decimal("0.20"),
                "rate_name": "Thuế suất thu nhập doanh nghiệp",
                "description": "Thuế suất TNDN dự kiến - Áp dụng năm 2027 (20%)",
            },
        ]
        
        policies = []
        for data in policies_data:
            policy = TaxPolicy(
                tax_type=TaxPolicyType.CIT,
                year=data["year"],
                rate=data["rate"],
                rate_name=data["rate_name"],
                active=True,
                description=data["description"],
            )
            policies.append(policy)
        
        db.session.add_all(policies)
        db.session.commit()
        
        print(f"Successfully seeded {len(policies)} CIT tax policies for years 2024-2027.")
        
        for p in TaxPolicy.query.filter_by(tax_type=TaxPolicyType.CIT).all():
            print(f"  - Year {p.year}: {int(p.rate * 100)}% - {p.description}")


def seed_vat_policies():
    """Seed VAT policies (optional - for future use)."""
    app = create_app("development")
    
    with app.app_context():
        existing = TaxPolicy.query.filter(
            TaxPolicy.tax_type.in_([TaxPolicyType.VAT_INPUT, TaxPolicyType.VAT_OUTPUT])
        ).first()
        
        if existing:
            print("VAT policies already exist. Skipping.")
            return
        
        vat_policies = [
            {
                "tax_type": TaxPolicyType.VAT_OUTPUT,
                "year": 2024,
                "rate": Decimal("0.10"),
                "rate_name": "Thuế GTGT đầu ra",
                "description": "Thuế GTGT đầu ra mặc định 10%",
            },
            {
                "tax_type": TaxPolicyType.VAT_OUTPUT,
                "year": 2025,
                "rate": Decimal("0.10"),
                "rate_name": "Thuế GTGT đầu ra",
                "description": "Thuế GTGT đầu ra mặc định 10%",
            },
        ]
        
        for data in vat_policies:
            policy = TaxPolicy(
                tax_type=data["tax_type"],
                year=data["year"],
                rate=data["rate"],
                rate_name=data["rate_name"],
                active=True,
                description=data["description"],
            )
            db.session.add(policy)
        
        db.session.commit()
        
        print(f"Seeded {len(vat_policies)} VAT policies.")


if __name__ == "__main__":
    print("Seeding tax policies based on Circular 99/2025/TT-BTC...")
    print("=" * 60)
    
    seed_tax_policies()
    seed_vat_policies()
    
    print("=" * 60)
    print("Done!")
