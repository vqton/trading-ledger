from datetime import date, datetime
from decimal import Decimal
from typing import Dict, List, Optional

from models.journal import JournalVoucher, JournalEntry, VoucherStatus, VoucherType
from models.audit_log import AuditLog, AuditAction, AuditEntity
from models.account import Account
from repositories.journal_repository import JournalRepository
from repositories.account_repository import AccountRepository
from services.voucher_numbering_service import generate_voucher_number


class JournalService:
    """Service for Journal business logic - Double-entry accounting."""

    @staticmethod
    def get_all_vouchers(
        status: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[JournalVoucher]:
        """Get all vouchers with filters."""
        return JournalRepository.get_all_vouchers(status, start_date, end_date, limit, offset)

    @staticmethod
    def get_voucher(voucher_id: int) -> Optional[JournalVoucher]:
        """Get voucher by ID."""
        return JournalRepository.get_voucher_by_id(voucher_id)

    @staticmethod
    def create_voucher(
        voucher_data: Dict,
        entries_data: List[Dict],
        user_id: int,
        ip_address: Optional[str] = None,
    ) -> JournalVoucher:
        """Create new voucher with entries.

        Core validation: Total Debit must equal Total Credit
        """
        voucher_date = voucher_data.get("voucher_date", date.today())
        voucher_type = voucher_data.get("voucher_type", "general")
        voucher_no = voucher_data.get("voucher_no")
        
        if not voucher_no:
            voucher_no = generate_voucher_number(voucher_type, voucher_date)
        
        voucher_data["voucher_no"] = voucher_no
        voucher_data["created_by"] = user_id

        total_debit = sum(Decimal(str(e.get("debit", 0))) for e in entries_data)
        total_credit = sum(Decimal(str(e.get("credit", 0))) for e in entries_data)

        if total_debit != total_credit:
            raise ValueError(f"Chứng từ không cân bằng: Nợ {total_debit} ≠ Có {total_credit}")

        for entry_data in entries_data:
            account_id = entry_data.get("account_id")
            if not AccountService.can_use_account(account_id):
                account = AccountRepository.get_by_id(account_id)
                raise ValueError(f"Tài khoản {account.account_code if account else account_id} không thể sử dụng")

            debit = Decimal(str(entry_data.get("debit", 0)))
            credit = Decimal(str(entry_data.get("credit", 0)))

            if debit > 0 and credit > 0:
                raise ValueError("Một dòng chỉ được có Nợ hoặc Có, không được có cả hai")
            if debit == 0 and credit == 0:
                raise ValueError("Một dòng phải có giá trị Nợ hoặc Có")

        voucher = JournalRepository.create_voucher(voucher_data)

        for idx, entry_data in enumerate(entries_data):
            entry_data["line_number"] = idx + 1
            JournalRepository.add_entry(voucher.id, entry_data)

        AuditLog.log(
            action=AuditAction.CREATE,
            entity=AuditEntity.JOURNAL_VOUCHER,
            entity_id=voucher.id,
            user_id=user_id,
            new_value={
                "voucher_no": voucher.voucher_no,
                "voucher_date": str(voucher.voucher_date),
                "total_debit": str(total_debit),
                "total_credit": str(total_credit),
            },
            ip_address=ip_address,
        )

        return voucher

    @staticmethod
    def update_voucher(
        voucher_id: int,
        voucher_data: Dict,
        entries_data: List[Dict],
        user_id: int,
        ip_address: Optional[str] = None,
    ) -> JournalVoucher:
        """Update voucher with entries."""
        voucher = JournalRepository.get_voucher_by_id(voucher_id)
        if not voucher:
            raise ValueError(f"Chứng từ {voucher_id} không tồn tại")

        if voucher.status != VoucherStatus.DRAFT:
            raise ValueError("Chỉ có thể sửa chứng từ nháp")

        total_debit = sum(Decimal(str(e.get("debit", 0))) for e in entries_data)
        total_credit = sum(Decimal(str(e.get("credit", 0))) for e in entries_data)

        if total_debit != total_credit:
            raise ValueError(f"Chứng từ không cân bằng: Nợ {total_debit} ≠ Có {total_credit}")

        old_value = {
            "voucher_no": voucher.voucher_no,
            "voucher_date": str(voucher.voucher_date),
            "description": voucher.description,
        }

        voucher = JournalRepository.update_voucher(voucher_id, voucher_data)
        JournalRepository.clear_entries(voucher_id)

        for idx, entry_data in enumerate(entries_data):
            entry_data["line_number"] = idx + 1
            JournalRepository.add_entry(voucher.id, entry_data)

        AuditLog.log(
            action=AuditAction.UPDATE,
            entity=AuditEntity.JOURNAL_VOUCHER,
            entity_id=voucher.id,
            user_id=user_id,
            old_value=old_value,
            new_value={
                "voucher_no": voucher.voucher_no,
                "voucher_date": str(voucher.voucher_date),
                "total_debit": str(total_debit),
            },
            ip_address=ip_address,
        )

        return voucher

    @staticmethod
    def delete_voucher(
        voucher_id: int,
        user_id: int,
        ip_address: Optional[str] = None,
    ) -> bool:
        """Delete voucher."""
        voucher = JournalRepository.get_voucher_by_id(voucher_id)
        if not voucher:
            raise ValueError(f"Chứng từ {voucher_id} không tồn tại")

        if voucher.status != VoucherStatus.DRAFT:
            raise ValueError("Chỉ có thể xóa chứng từ nháp")

        AuditLog.log(
            action=AuditAction.DELETE,
            entity=AuditEntity.JOURNAL_VOUCHER,
            entity_id=voucher.id,
            user_id=user_id,
            old_value={"voucher_no": voucher.voucher_no},
            ip_address=ip_address,
        )

        return JournalRepository.delete_voucher(voucher_id)

    @staticmethod
    def post_voucher(
        voucher_id: int,
        user_id: int,
        ip_address: Optional[str] = None,
    ) -> JournalVoucher:
        """Post voucher to ledger.

        This is the key step that makes entries affect the general ledger.
        """
        voucher = JournalRepository.get_voucher_by_id(voucher_id)
        if not voucher:
            raise ValueError(f"Chứng từ {voucher_id} không tồn tại")

        if not voucher.is_balanced:
            raise ValueError("Chứng từ không cân bằng - không thể ghi sổ")

        if not voucher.entries:
            raise ValueError("Chứng từ không có dòng nào - không thể ghi sổ")

        voucher = JournalRepository.post_voucher(voucher_id, user_id)

        AuditLog.log(
            action=AuditAction.POST,
            entity=AuditEntity.JOURNAL_VOUCHER,
            entity_id=voucher.id,
            user_id=user_id,
            new_value={"voucher_no": voucher.voucher_no, "status": "posted"},
            ip_address=ip_address,
        )

        return voucher

    @staticmethod
    def unpost_voucher(
        voucher_id: int,
        user_id: int,
        ip_address: Optional[str] = None,
    ) -> JournalVoucher:
        """Unpost voucher (reverse from ledger)."""
        voucher = JournalRepository.get_voucher_by_id(voucher_id)
        if not voucher:
            raise ValueError(f"Chứng từ {voucher_id} không tồn tại")

        voucher = JournalRepository.unpost_voucher(voucher_id)

        AuditLog.log(
            action=AuditAction.UNPOST,
            entity=AuditEntity.JOURNAL_VOUCHER,
            entity_id=voucher.id,
            user_id=user_id,
            new_value={"voucher_no": voucher.voucher_no, "status": "draft"},
            ip_address=ip_address,
        )

        return voucher

    @staticmethod
    def lock_voucher(
        voucher_id: int,
        user_id: int,
        ip_address: Optional[str] = None,
    ) -> JournalVoucher:
        """Lock posted voucher."""
        voucher = JournalRepository.get_voucher_by_id(voucher_id)
        if not voucher:
            raise ValueError(f"Chứng từ {voucher_id} không tồn tại")

        voucher = JournalRepository.lock_voucher(voucher_id)

        AuditLog.log(
            action=AuditAction.LOCK,
            entity=AuditEntity.JOURNAL_VOUCHER,
            entity_id=voucher.id,
            user_id=user_id,
            new_value={"voucher_no": voucher.voucher_no, "status": "locked"},
            ip_address=ip_address,
        )

        return voucher

    @staticmethod
    def validate_entries(entries_data: List[Dict]) -> Dict:
        """Validate entries without saving."""
        errors = []
        warnings = []

        if not entries_data:
            errors.append("Chứng từ phải có ít nhất một dòng")
            return {"valid": False, "errors": errors, "warnings": warnings}

        total_debit = Decimal("0")
        total_credit = Decimal("0")

        for idx, entry in enumerate(entries_data):
            line = idx + 1

            account_id = entry.get("account_id")
            if not account_id:
                errors.append(f"Dòng {line}: Chưa chọn tài khoản")
                continue

            account = AccountRepository.get_by_id(account_id)
            if not account:
                errors.append(f"Dòng {line}: Tài khoản không tồn tại")
            elif not account.is_active:
                errors.append(f"Dòng {line}: Tài khoản {account.account_code} đã bị khóa")
            elif not account.is_detail:
                warnings.append(f"Dòng {line}: Tài khoản {account.account_code} là tài khoản tổng hợp")

            debit = Decimal(str(entry.get("debit", 0)))
            credit = Decimal(str(entry.get("credit", 0)))

            if debit > 0 and credit > 0:
                errors.append(f"Dòng {line}: Không thể có cả Nợ và Có")
            elif debit == 0 and credit == 0:
                errors.append(f"Dòng {line}: Phải có giá trị Nợ hoặc Có")

            total_debit += debit
            total_credit += credit

        if total_debit != total_credit:
            errors.append(f"Tổng Nợ ({total_debit}) phải bằng Tổng Có ({total_credit})")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "total_debit": str(total_debit),
            "total_credit": str(total_credit),
        }

    @staticmethod
    def get_voucher_count(status: Optional[str] = None) -> int:
        """Get count of vouchers."""
        return JournalRepository.count_vouchers(status)


class AccountService:
    """Helper service for account validation."""

    @staticmethod
    def can_use_account(account_id: int) -> bool:
        """Check if account can be used in journal entries."""
        account = AccountRepository.get_by_id(account_id)
        if not account:
            return False
        if not account.is_active:
            return False
        if not account.is_detail:
            return False
        return True
