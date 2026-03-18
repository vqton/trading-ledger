"""
Voucher Templates - Quick entry for common transactions.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class VoucherTemplate:
    """Voucher template definition."""
    id: str
    name: str
    name_vi: str
    icon: str
    description: str
    voucher_type: str
    entries: List[Dict]


VOUCHER_TEMPLATES = [
    VoucherTemplate(
        id="mua_hang",
        name="Purchase",
        name_vi="Mua hàng",
        icon="fa-cart-shopping",
        description="Mua hàng hóa, dịch vụ",
        voucher_type="purchase",
        entries=[
            {"account_type": "expense", "debit": True, "credit": False, "label": "Giá vốn/Tài sản"},
            {"account_type": "liability", "debit": False, "credit": True, "label": "Phải trả người bán"},
        ]
    ),
    VoucherTemplate(
        id="ban_hang",
        name="Sales",
        name_vi="Bán hàng",
        icon="fa-shopping-cart",
        description="Bán hàng hóa, dịch vụ",
        voucher_type="sales",
        entries=[
            {"account_type": "asset", "debit": True, "credit": False, "label": "Phải thu/Tiền"},
            {"account_type": "revenue", "debit": False, "credit": True, "label": "Doanh thu"},
        ]
    ),
    VoucherTemplate(
        id="thu_tien",
        name="Cash Receipt",
        name_vi="Thu tiền",
        icon="fa-money-bill-wave",
        description="Thu tiền từ khách hàng",
        voucher_type="cash_receipt",
        entries=[
            {"account_type": "asset", "debit": True, "credit": False, "label": "Tiền mặt/TK ngân hàng"},
            {"account_type": "asset", "debit": False, "credit": True, "label": "Phải thu KH"},
        ]
    ),
    VoucherTemplate(
        id="chi_tien",
        name="Cash Payment",
        name_vi="Chi tiền",
        icon="fa-money-bill-trend-down",
        description="Chi tiền cho nhà cung cấp",
        voucher_type="cash_payment",
        entries=[
            {"account_type": "liability", "debit": True, "credit": False, "label": "Phải trả NCC"},
            {"account_type": "asset", "debit": False, "credit": True, "label": "Tiền mặt/TK ngân hàng"},
        ]
    ),
    VoucherTemplate(
        id="chuyen_tien",
        name="Transfer",
        name_vi="Chuyển tiền",
        icon="fa-exchange",
        description="Chuyển tiền giữa các TK",
        voucher_type="general",
        entries=[
            {"account_type": "asset", "debit": True, "credit": False, "label": "TK nhận"},
            {"account_type": "asset", "debit": False, "credit": True, "label": "TK nguồn"},
        ]
    ),
    VoucherTemplate(
        id="chi_phi",
        name="Expense",
        name_vi="Chi phí",
        icon="fa-file-invoice-dollar",
        description="Chi phí kinh doanh",
        voucher_type="general",
        entries=[
            {"account_type": "expense", "debit": True, "credit": False, "label": "Chi phí"},
            {"account_type": "asset", "debit": False, "credit": True, "label": "Tiền"},
        ]
    ),
]


def get_template(template_id: str) -> Optional[VoucherTemplate]:
    """Get template by ID."""
    for template in VOUCHER_TEMPLATES:
        if template.id == template_id:
            return template
    return None


def get_all_templates() -> List[VoucherTemplate]:
    """Get all voucher templates."""
    return VOUCHER_TEMPLATES


def get_template_accounts(template: VoucherTemplate) -> Dict[str, List[Dict]]:
    """Get recommended accounts for a template based on account type."""
    from models.account import Account, AccountType
    from core.database import db
    
    result = {}
    for entry in template.entries:
        account_type = entry["account_type"]
        accounts = Account.query.filter(
            Account.account_type == account_type,
            Account.is_active == True,
            Account.is_postable == True
        ).order_by(Account.code).all()
        
        result[account_type] = [
            {"id": acc.id, "code": acc.code, "name": acc.name_vi}
            for acc in accounts
        ]
    
    return result
