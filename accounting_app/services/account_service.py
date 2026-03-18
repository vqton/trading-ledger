from typing import Dict, List, Optional
from datetime import datetime, date
from decimal import Decimal

from models.account import Account, AccountType, NormalBalance
from models.audit_log import AuditLog, AuditAction, AuditEntity
from models.journal import JournalEntry, JournalVoucher, VoucherStatus
from core.database import db
from repositories.account_repository import AccountRepository


class AccountService:
    """Service for Account business logic."""

    @staticmethod
    def get_all_accounts() -> List[Account]:
        """Get all accounts."""
        return AccountRepository.get_all()

    @staticmethod
    def get_account(account_id: int) -> Optional[Account]:
        """Get account by ID."""
        return AccountRepository.get_by_id(account_id)

    @staticmethod
    def get_active_accounts() -> List[Account]:
        """Get all active accounts."""
        return AccountRepository.get_active()

    @staticmethod
    def get_detail_accounts() -> List[Account]:
        """Get detail accounts for journal entry dropdown."""
        return AccountRepository.get_detail_accounts()

    @staticmethod
    def create_account(account_data: Dict, user_id: int, ip_address: Optional[str] = None) -> Account:
        """Create new account with validation."""
        existing = AccountRepository.get_by_code(account_data["code"])
        if existing:
            raise ValueError(f"Mã tài khoản {account_data['code']} đã tồn tại")

        if account_data.get("parent_id"):
            parent = AccountRepository.get_by_id(account_data["parent_id"])
            if not parent:
                raise ValueError("Tài khoản cha không tồn tại")
            if parent.account_type != account_data["account_type"]:
                raise ValueError("Tài khoản con phải cùng loại với tài khoản cha")

        account = AccountRepository.create(account_data)

        AuditLog.log(
            action=AuditAction.CREATE,
            entity=AuditEntity.ACCOUNT,
            entity_id=account.id,
            user_id=user_id,
            new_value={
                "account_code": account.account_code,
                "account_name": account.account_name,
                "account_type": account.account_type,
            },
            ip_address=ip_address,
        )

        return account

    @staticmethod
    def update_account(
        account_id: int,
        account_data: Dict,
        user_id: int,
        ip_address: Optional[str] = None,
    ) -> Account:
        """Update account with validation."""
        account = AccountRepository.get_by_id(account_id)
        if not account:
            raise ValueError(f"Tài khoản {account_id} không tồn tại")

        if AccountRepository.has_children(account_id) and account_data.get("is_detail"):
            raise ValueError("Không thể chuyển tài khoản cha thành tài khoản chi tiết")

        if AccountRepository.has_transactions(account_id):
            if account_data.get("account_code") and account_data["account_code"] != account.account_code:
                raise ValueError("Không thể thay đổi mã tài khoản đã có giao dịch")
            if account_data.get("account_type") and account_data["account_type"] != account.account_type:
                raise ValueError("Không thể thay đổi loại tài khoản đã có giao dịch")

        old_value = {
            "account_code": account.account_code,
            "account_name": account.account_name,
            "account_type": account.account_type,
            "is_active": account.is_active,
        }

        account = AccountRepository.update(account_id, account_data)

        AuditLog.log(
            action=AuditAction.UPDATE,
            entity=AuditEntity.ACCOUNT,
            entity_id=account.id,
            user_id=user_id,
            old_value=old_value,
            new_value={
                "account_code": account.account_code,
                "account_name": account.account_name,
                "account_type": account.account_type,
                "is_active": account.is_active,
            },
            ip_address=ip_address,
        )

        return account

    @staticmethod
    def delete_account(
        account_id: int,
        user_id: int,
        ip_address: Optional[str] = None,
    ) -> bool:
        """Soft delete account with validation."""
        account = AccountRepository.get_by_id(account_id)
        if not account:
            raise ValueError(f"Tài khoản {account_id} không tồn tại")

        if AccountRepository.has_children(account_id):
            raise ValueError("Không thể xóa tài khoản có tài khoản con")

        if AccountRepository.has_transactions(account_id):
            raise ValueError("Không thể xóa tài khoản đã có giao dịch")

        AuditLog.log(
            action=AuditAction.DELETE,
            entity=AuditEntity.ACCOUNT,
            entity_id=account.id,
            user_id=user_id,
            old_value={
                "account_code": account.account_code,
                "account_name": account.account_name,
            },
            ip_address=ip_address,
        )

        return AccountRepository.delete(account_id)

    @staticmethod
    def get_account_tree() -> List[Dict]:
        """Get accounts in tree structure."""
        accounts = AccountRepository.get_all()
        tree = []

        def build_tree(parent_id: int = None) -> List[Dict]:
            result = []
            for account in accounts:
                if account.parent_id == parent_id:
                    node = {
                        "id": account.id,
                        "code": account.account_code,
                        "name": account.account_name,
                        "type": account.account_type,
                        "is_detail": account.is_detail,
                        "is_active": account.is_active,
                        "children": build_tree(account.id),
                    }
                    result.append(node)
            return result

        return build_tree()

    @staticmethod
    def get_accounts_by_type(account_type: str) -> List[Account]:
        """Get accounts filtered by type."""
        return AccountRepository.get_by_type(account_type)

    @staticmethod
    def search_accounts(query: str) -> List[Account]:
        """Search accounts by code or name."""
        return AccountRepository.search(query)

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

    @staticmethod
    def get_dashboard_kpis(end_date: date = None) -> Dict:
        """Get dashboard KPIs for overview."""
        if end_date is None:
            end_date = date.today()
        
        kpis = {
            "cash_balance": Decimal("0"),
            "bank_balance": Decimal("0"),
            "receivable_balance": Decimal("0"),
            "payable_balance": Decimal("0"),
            "monthly_revenue": Decimal("0"),
            "monthly_expense": Decimal("0"),
            "monthly_profit": Decimal("0"),
            "vouchers_draft": 0,
            "vouchers_posted": 0,
        }
        
        cash_accounts = Account.query.filter(
            Account.code.in_(["111", "1111", "1112", "1113"])
        ).all()
        for acc in cash_accounts:
            balance = db.session.query(
                db.func.coalesce(db.func.sum(JournalEntry.debit), 0) -
                db.func.coalesce(db.func.sum(JournalEntry.credit), 0)
            ).filter(
                JournalEntry.account_id == acc.id
            ).scalar() or Decimal("0")
            kpis["cash_balance"] += Decimal(str(balance))
        
        bank_accounts = Account.query.filter(
            Account.code.in_(["112", "1121", "1122"])
        ).all()
        for acc in bank_accounts:
            balance = db.session.query(
                db.func.coalesce(db.func.sum(JournalEntry.debit), 0) -
                db.func.coalesce(db.func.sum(JournalEntry.credit), 0)
            ).filter(
                JournalEntry.account_id == acc.id
            ).scalar() or Decimal("0")
            kpis["bank_balance"] += Decimal(str(balance))
        
        receivable_accounts = Account.query.filter(
            Account.code.like("131%")
        ).all()
        for acc in receivable_accounts:
            balance = db.session.query(
                db.func.coalesce(db.func.sum(JournalEntry.debit), 0) -
                db.func.coalesce(db.func.sum(JournalEntry.credit), 0)
            ).filter(
                JournalEntry.account_id == acc.id
            ).scalar() or Decimal("0")
            kpis["receivable_balance"] += Decimal(str(balance))
        
        payable_accounts = Account.query.filter(
            Account.code.like("33%")
        ).all()
        for acc in payable_accounts:
            balance = db.session.query(
                db.func.coalesce(db.func.sum(JournalEntry.credit), 0) -
                db.func.coalesce(db.func.sum(JournalEntry.debit), 0)
            ).filter(
                JournalEntry.account_id == acc.id
            ).scalar() or Decimal("0")
            kpis["payable_balance"] += Decimal(str(balance))
        
        from models.journal import JournalVoucher, VoucherStatus
        start_of_month = end_date.replace(day=1)
        
        revenue_accounts = Account.query.filter(
            Account.code.like("5%")
        ).all()
        revenue_ids = [acc.id for acc in revenue_accounts]
        if revenue_ids:
            revenue_total = db.session.query(
                db.func.coalesce(db.func.sum(JournalEntry.credit), 0)
            ).join(JournalVoucher).filter(
                JournalEntry.account_id.in_(revenue_ids),
                JournalVoucher.voucher_date >= start_of_month,
                JournalVoucher.voucher_date <= end_date,
                JournalVoucher.status == VoucherStatus.POSTED
            ).scalar() or Decimal("0")
            kpis["monthly_revenue"] = Decimal(str(revenue_total))
        
        expense_accounts = Account.query.filter(
            Account.code.like("6%")
        ).all()
        expense_ids = [acc.id for acc in expense_accounts]
        if expense_ids:
            expense_total = db.session.query(
                db.func.coalesce(db.func.sum(JournalEntry.debit), 0)
            ).join(JournalVoucher).filter(
                JournalEntry.account_id.in_(expense_ids),
                JournalVoucher.voucher_date >= start_of_month,
                JournalVoucher.voucher_date <= end_date,
                JournalVoucher.status == VoucherStatus.POSTED
            ).scalar() or Decimal("0")
            kpis["monthly_expense"] = Decimal(str(expense_total))
        
        kpis["monthly_profit"] = kpis["monthly_revenue"] - kpis["monthly_expense"]
        
        from models.journal import JournalVoucher
        kpis["vouchers_draft"] = JournalVoucher.query.filter(
            JournalVoucher.status == VoucherStatus.DRAFT
        ).count()
        kpis["vouchers_posted"] = JournalVoucher.query.filter(
            JournalVoucher.status == VoucherStatus.POSTED
        ).count()
        
        return kpis

    @staticmethod
    def get_account_balance(account_id: int, end_date: date = None) -> Decimal:
        """Get account balance up to a date."""
        if end_date is None:
            end_date = date.today()
        
        account = AccountRepository.get_by_id(account_id)
        if not account:
            return Decimal("0")
        
        result = db.session.query(
            db.func.coalesce(db.func.sum(JournalEntry.debit), 0) -
            db.func.coalesce(db.func.sum(JournalEntry.credit), 0)
        ).join(JournalVoucher).filter(
            JournalEntry.account_id == account_id,
            JournalVoucher.voucher_date <= end_date,
            JournalVoucher.status == VoucherStatus.POSTED
        ).scalar() or Decimal("0")
        
        if account.normal_balance == "credit":
            result = -result
        
        return Decimal(str(result))
