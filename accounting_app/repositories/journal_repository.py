from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy.orm import selectinload

from models.journal import JournalVoucher, JournalEntry, VoucherStatus, VoucherType
from models.account import Account
from core.database import db
from core.utils import utc_now
from services.coa_engine import COAEngine


class JournalRepository:
    """Repository for Journal database operations."""

    @staticmethod
    def get_all_vouchers(
        status: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[JournalVoucher]:
        """Get vouchers with optional filters."""
        query = JournalVoucher.query.options(selectinload(JournalVoucher.entries))

        if status:
            query = query.filter(JournalVoucher.status == status)
        if start_date:
            query = query.filter(JournalVoucher.voucher_date >= start_date)
        if end_date:
            query = query.filter(JournalVoucher.voucher_date <= end_date)

        return query.order_by(JournalVoucher.voucher_date.desc(), JournalVoucher.voucher_no.desc()).offset(offset).limit(limit).all()

    @staticmethod
    def get_voucher_by_id(voucher_id: int) -> Optional[JournalVoucher]:
        """Get voucher by ID with entries."""
        return JournalVoucher.query.options(selectinload(JournalVoucher.entries)).get(voucher_id)

    @staticmethod
    def get_voucher_by_no(voucher_no: str) -> Optional[JournalVoucher]:
        """Get voucher by voucher number."""
        return JournalVoucher.query.options(selectinload(JournalVoucher.entries)).filter_by(voucher_no=voucher_no).first()

    @staticmethod
    def create_voucher(voucher_data: dict) -> JournalVoucher:
        """Create new voucher."""
        if not voucher_data.get("voucher_no"):
            voucher_data["voucher_no"] = JournalVoucher.generate_voucher_no()
        
        voucher = JournalVoucher(
            voucher_no=voucher_data["voucher_no"],
            voucher_date=voucher_data["voucher_date"],
            voucher_type=voucher_data.get("voucher_type", "general"),
            description=voucher_data.get("description"),
            reference=voucher_data.get("reference"),
            status=VoucherStatus.DRAFT,
            created_by=voucher_data["created_by"],
        )
        db.session.add(voucher)
        db.session.flush()
        return voucher

    @staticmethod
    def update_voucher(voucher_id: int, voucher_data: dict) -> JournalVoucher:
        """Update voucher."""
        voucher = db.session.get(JournalVoucher, voucher_id)
        if not voucher:
            raise ValueError(f"Voucher {voucher_id} not found")
        
        if voucher.status != VoucherStatus.DRAFT:
            raise ValueError("Không thể sửa chứng từ đã ghi sổ")

        if "voucher_date" in voucher_data:
            voucher.voucher_date = voucher_data["voucher_date"]
        if "voucher_type" in voucher_data:
            voucher.voucher_type = voucher_data["voucher_type"]
        if "description" in voucher_data:
            voucher.description = voucher_data["description"]
        if "reference" in voucher_data:
            voucher.reference = voucher_data["reference"]

        db.session.commit()
        return voucher

    @staticmethod
    def delete_voucher(voucher_id: int) -> bool:
        """Delete voucher (must be draft)."""
        voucher = db.session.get(JournalVoucher, voucher_id)
        if not voucher:
            return False

        if voucher.status != VoucherStatus.DRAFT:
            raise ValueError("Chỉ có thể xóa chứng từ nháp")

        db.session.delete(voucher)
        db.session.commit()
        return True

    @staticmethod
    def add_entry(voucher_id: int, entry_data: dict) -> JournalEntry:
        """Add journal entry to voucher."""
        entry = JournalEntry(
            voucher_id=voucher_id,
            account_id=entry_data["account_id"],
            line_number=entry_data.get("line_number", 1),
            debit=entry_data.get("debit", Decimal("0.00")),
            credit=entry_data.get("credit", Decimal("0.00")),
            description=entry_data.get("description"),
            reference=entry_data.get("reference"),
            cost_center=entry_data.get("cost_center"),
        )
        db.session.add(entry)
        db.session.flush()
        return entry

    @staticmethod
    def update_entry(entry_id: int, entry_data: dict) -> JournalEntry:
        """Update journal entry."""
        entry = db.session.get(JournalEntry, entry_id)
        if not entry:
            raise ValueError(f"Entry {entry_id} not found")

        if "account_id" in entry_data:
            entry.account_id = entry_data["account_id"]
        if "line_number" in entry_data:
            entry.line_number = entry_data["line_number"]
        if "debit" in entry_data:
            entry.debit = entry_data["debit"]
        if "credit" in entry_data:
            entry.credit = entry_data["credit"]
        if "description" in entry_data:
            entry.description = entry_data["description"]
        if "reference" in entry_data:
            entry.reference = entry_data["reference"]
        if "cost_center" in entry_data:
            entry.cost_center = entry_data["cost_center"]

        db.session.commit()
        return entry

    @staticmethod
    def delete_entry(entry_id: int) -> bool:
        """Delete journal entry."""
        entry = db.session.get(JournalEntry, entry_id)
        if not entry:
            return False

        db.session.delete(entry)
        db.session.commit()
        return True

    @staticmethod
    def clear_entries(voucher_id: int) -> None:
        """Clear all entries for a voucher."""
        JournalEntry.query.filter_by(voucher_id=voucher_id).delete()
        db.session.commit()

    @staticmethod
    def post_voucher(voucher_id: int, user_id: int) -> JournalVoucher:
        """Post a voucher (change status to posted).
        
        Validates using COA Engine for posting rules.
        """
        voucher = db.session.get(JournalVoucher, voucher_id)
        if not voucher:
            raise ValueError(f"Voucher {voucher_id} not found")

        if voucher.status != VoucherStatus.DRAFT:
            raise ValueError("Chỉ có thể ghi sổ chứng từ nháp")

        if not voucher.is_balanced:
            raise ValueError("Chứng từ không cân bằng (Tổng Nợ ≠ Tợ Có)")

        coa_engine = COAEngine()
        entries = JournalEntry.query.filter_by(voucher_id=voucher_id).all()
        
        for entry in entries:
            account = db.session.get(Account, entry.account_id)
            if not account:
                raise ValueError(f"Tài khoản ID {entry.account_id} không tồn tại")
            
            result = coa_engine.validate_posting(account.code)
            if not result.success:
                raise ValueError(result.message)
            
            result = coa_engine.validate_subledger(
                account.code,
                customer_id=entry.customer_id,
                vendor_id=entry.vendor_id,
                bank_account_id=entry.bank_account_id,
                inventory_item_id=entry.inventory_item_id,
            )
            if not result.success:
                raise ValueError(result.message)

        voucher.status = VoucherStatus.POSTED
        voucher.posted_by = user_id
        voucher.posted_at = utc_now()
        db.session.commit()
        return voucher

    @staticmethod
    def unpost_voucher(voucher_id: int) -> JournalVoucher:
        """Unpost a voucher (change status to draft)."""
        voucher = db.session.get(JournalVoucher, voucher_id)
        if not voucher:
            raise ValueError(f"Voucher {voucher_id} not found")

        if voucher.status != VoucherStatus.POSTED:
            raise ValueError("Chỉ có thể bỏ ghi sổ chứng từ đã ghi")

        voucher.status = VoucherStatus.DRAFT
        voucher.posted_by = None
        voucher.posted_at = None
        db.session.commit()
        return voucher

    @staticmethod
    def lock_voucher(voucher_id: int) -> JournalVoucher:
        """Lock a posted voucher."""
        voucher = db.session.get(JournalVoucher, voucher_id)
        if not voucher:
            raise ValueError(f"Voucher {voucher_id} not found")

        if voucher.status != VoucherStatus.POSTED:
            raise ValueError("Chỉ có thể khóa chứng từ đã ghi sổ")

        voucher.status = VoucherStatus.LOCKED
        db.session.commit()
        return voucher

    @staticmethod
    def count_vouchers(status: Optional[str] = None) -> int:
        """Count vouchers with optional status filter."""
        query = JournalVoucher.query
        if status:
            query = query.filter(JournalVoucher.status == status)
        return query.count()
