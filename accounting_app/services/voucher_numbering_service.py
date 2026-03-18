"""
Voucher numbering service - Auto-generate voucher numbers.
"""

from datetime import date
from typing import Optional
from dataclasses import dataclass


VOUCHER_TYPE_PREFIXES = {
    "general": "CT",
    "cash_receipt": "PT",
    "cash_payment": "PC",
    "bank_receipt": "BN",
    "bank_payment": "BQ",
    "purchase": "PU",
    "sales": "SA",
}

VOUCHER_TYPE_NAMES = {
    "general": "Chứng từ chung",
    "cash_receipt": "Phiếu thu",
    "cash_payment": "Phiếu chi",
    "bank_receipt": "Biên nhận NH",
    "bank_payment": "Chi NH",
    "purchase": "Mua hàng",
    "sales": "Bán hàng",
}


@dataclass
class NumberingConfig:
    """Voucher numbering configuration."""
    prefix_format: str = "{type}{year}{month}"
    start_number: int = 1
    padding: int = 5


def generate_voucher_number(
    voucher_type: str,
    voucher_date: date = None,
    config: NumberingConfig = None
) -> str:
    """Generate voucher number based on type and date.
    
    Format: {TYPE}{YYYYMM}{00001}
    Example: PU20260300001
    """
    if config is None:
        config = NumberingConfig()
    
    if voucher_date is None:
        voucher_date = date.today()
    
    prefix = VOUCHER_TYPE_PREFIXES.get(voucher_type, "CT")
    
    year = voucher_date.strftime("%Y")
    month = voucher_date.strftime("%m")
    
    from models.journal import JournalVoucher
    
    start_of_month = voucher_date.replace(day=1)
    end_of_month = voucher_date.replace(day=28)
    if voucher_date.month == 12:
        end_of_month = end_of_month.replace(month=12, day=31)
    else:
        end_of_month = end_of_month.replace(month=voucher_date.month + 1, day=1)
    from datetime import timedelta
    end_of_month = end_of_month - timedelta(days=1)
    
    count = JournalVoucher.query.filter(
        JournalVoucher.voucher_no.like(f"{prefix}{year}{month}%"),
        JournalVoucher.voucher_date >= start_of_month,
        JournalVoucher.voucher_date <= end_of_month,
    ).count()
    
    next_number = count + 1
    padded_number = str(next_number).zfill(config.padding)
    
    return f"{prefix}{year}{month}{padded_number}"


def get_voucher_type_choices():
    """Get voucher type choices for forms."""
    return [(k, v) for k, v in VOUCHER_TYPE_NAMES.items()]


def get_voucher_type_name(voucher_type: str) -> str:
    """Get voucher type display name."""
    return VOUCHER_TYPE_NAMES.get(voucher_type, voucher_type)
