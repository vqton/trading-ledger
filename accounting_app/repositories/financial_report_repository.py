from datetime import date, datetime
from decimal import Decimal
from typing import Dict, List, Optional

from sqlalchemy import func, and_

from models.journal import JournalVoucher, JournalEntry, VoucherStatus
from models.account import Account, AccountType
from core.database import db


class FinancialReportRepository:
    """Repository for Financial Report queries."""

    @staticmethod
    def get_account_type_balance(
        account_type: str,
        end_date: Optional[date] = None,
    ) -> Decimal:
        """Get total balance for an account type.
        
        For asset and expense accounts (debit normal): balance = debit - credit
        For liability, equity, and revenue accounts (credit normal): balance = credit - debit
        """
        is_debit_normal = account_type in [AccountType.ASSET, AccountType.EXPENSE]
        
        query = db.session.query(
            func.coalesce(func.sum(JournalEntry.debit), Decimal("0")).label("total_debit"),
            func.coalesce(func.sum(JournalEntry.credit), Decimal("0")).label("total_credit"),
        ).join(
            JournalVoucher, JournalEntry.voucher_id == JournalVoucher.id
        ).join(
            Account, JournalEntry.account_id == Account.id
        ).filter(
            Account.account_type == account_type,
            Account.is_postable == True,
            JournalVoucher.status == VoucherStatus.POSTED,
        )

        if end_date:
            query = query.filter(JournalVoucher.voucher_date <= end_date)

        result = query.first()
        if not result or (result.total_debit == 0 and result.total_credit == 0):
            return Decimal("0")
        
        debit = Decimal(str(result.total_debit))
        credit = Decimal(str(result.total_credit))
        
        if is_debit_normal:
            balance = debit - credit
        else:
            balance = credit - debit
            
        return balance

    @staticmethod
    def get_account_balances_by_type(
        account_type: str,
        end_date: Optional[date] = None,
    ) -> List[Dict]:
        """Get balances for all accounts of a type."""
        date_filter = True
        if end_date:
            date_filter = JournalVoucher.voucher_date <= end_date
        
        query = db.session.query(
            Account.id,
            Account.code,
            Account.name_vi,
            Account.normal_balance,
            func.coalesce(func.sum(JournalEntry.debit), Decimal("0")).label("total_debit"),
            func.coalesce(func.sum(JournalEntry.credit), Decimal("0")).label("total_credit"),
        ).outerjoin(
            JournalEntry, Account.id == JournalEntry.account_id
        ).outerjoin(
            JournalVoucher, and_(
                JournalEntry.voucher_id == JournalVoucher.id,
                JournalVoucher.status == VoucherStatus.POSTED,
                date_filter,
            )
        ).filter(
            Account.account_type == account_type,
            Account.is_postable == True,
            Account.is_active == True,
        ).group_by(
            Account.id, Account.code, Account.name_vi, Account.normal_balance
        )

        results = []
        for row in query.all():
            debit = Decimal(str(row.total_debit))
            credit = Decimal(str(row.total_credit))

            if row.normal_balance == "debit":
                balance = debit - credit
            else:
                balance = credit - debit

            results.append({
                "id": row.id,
                "account_code": row.code,
                "account_name": row.name_vi,
                "balance": balance,
            })

        return results

    @staticmethod
    def get_period_turnover(
        account_type: str,
        start_date: date,
        end_date: date,
    ) -> Decimal:
        """Get total debit turnover for a period (for income statement)."""
        query = db.session.query(
            func.coalesce(func.sum(JournalEntry.debit), Decimal("0"))
        ).join(
            JournalVoucher, JournalEntry.voucher_id == JournalVoucher.id
        ).join(
            Account, JournalEntry.account_id == Account.id
        ).filter(
            Account.account_type == account_type,
            Account.is_postable == True,
            JournalVoucher.status == VoucherStatus.POSTED,
            JournalVoucher.voucher_date >= start_date,
            JournalVoucher.voucher_date <= end_date,
        )

        result = query.scalar()
        return Decimal(str(result)) if result else Decimal("0")

    @staticmethod
    def get_account_period_balance(
        account_code_prefix: str,
        start_date: date,
        end_date: date,
    ) -> Decimal:
        """Get balance change for accounts with code prefix in period."""
        query = db.session.query(
            func.coalesce(func.sum(JournalEntry.debit), Decimal("0")) - 
            func.coalesce(func.sum(JournalEntry.credit), Decimal("0"))
        ).join(
            JournalVoucher, JournalEntry.voucher_id == JournalVoucher.id
        ).join(
            Account, JournalEntry.account_id == Account.id
        ).filter(
            Account.code.like(f"{account_code_prefix}%"),
            Account.is_postable == True,
            JournalVoucher.status == VoucherStatus.POSTED,
            JournalVoucher.voucher_date >= start_date,
            JournalVoucher.voucher_date <= end_date,
        )

        result = query.scalar()
        return Decimal(str(result)) if result else Decimal("0")

    @staticmethod
    def get_all_account_balances(
        end_date: Optional[date] = None,
    ) -> Dict[str, Decimal]:
        """Get balances for all main account types."""
        types = ["asset", "liability", "equity", "revenue", "expense"]
        result = {}

        for acc_type in types:
            result[acc_type] = FinancialReportRepository.get_account_type_balance(acc_type, end_date)

        return result
