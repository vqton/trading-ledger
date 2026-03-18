from datetime import date, datetime
from decimal import Decimal
from typing import Dict, List, Optional, Tuple

from sqlalchemy import func, and_

from models.journal import JournalVoucher, JournalEntry, VoucherStatus
from models.account import Account
from core.database import db


class LedgerRepository:
    """Repository for Ledger database operations with optimized queries."""

    @staticmethod
    def get_account_balance(
        account_id: int,
        end_date: Optional[date] = None,
        include_children: bool = False,
    ) -> Decimal:
        """Calculate account balance up to end_date.

        Balance = Sum(Debit) - Sum(Credit) for posted entries
        """
        query = db.session.query(
            func.coalesce(func.sum(JournalEntry.debit), Decimal("0")) - 
            func.coalesce(func.sum(JournalEntry.credit), Decimal("0"))
        ).join(
            JournalVoucher, JournalEntry.voucher_id == JournalVoucher.id
        ).filter(
            JournalEntry.account_id == account_id,
            JournalVoucher.status == VoucherStatus.POSTED,
        )

        if end_date:
            query = query.filter(JournalVoucher.voucher_date <= end_date)

        result = query.scalar()
        return Decimal(str(result)) if result else Decimal("0")

    @staticmethod
    def get_account_balances(
        account_ids: List[int],
        end_date: Optional[date] = None,
    ) -> Dict[int, Decimal]:
        """Get balances for multiple accounts in one query."""
        query = db.session.query(
            JournalEntry.account_id,
            func.coalesce(func.sum(JournalEntry.debit), Decimal("0")) - 
            func.coalesce(func.sum(JournalEntry.credit), Decimal("0"))
        ).join(
            JournalVoucher, JournalEntry.voucher_id == JournalVoucher.id
        ).filter(
            JournalEntry.account_id.in_(account_ids),
            JournalVoucher.status == VoucherStatus.POSTED,
        )

        if end_date:
            query = query.filter(JournalVoucher.voucher_date <= end_date)

        query = query.group_by(JournalEntry.account_id)
        results = query.all()

        return {row[0]: row[1] for row in results}

    @staticmethod
    def get_ledger_entries(
        account_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[Dict]:
        """Get ledger entries for an account with optional date range."""
        query = db.session.query(
            JournalEntry,
            JournalVoucher,
            Account
        ).join(
            JournalVoucher, JournalEntry.voucher_id == JournalVoucher.id
        ).join(
            Account, JournalEntry.account_id == Account.id
        ).filter(
            JournalEntry.account_id == account_id,
            JournalVoucher.status == VoucherStatus.POSTED,
        )

        if start_date:
            query = query.filter(JournalVoucher.voucher_date >= start_date)
        if end_date:
            query = query.filter(JournalVoucher.voucher_date <= end_date)

        query = query.order_by(JournalVoucher.voucher_date, JournalVoucher.voucher_no)

        results = []
        running_balance = Decimal("0")
        account = db.session.get(Account, account_id)

        for entry, voucher, account in query.all():
            debit = entry.debit or Decimal("0")
            credit = entry.credit or Decimal("0")

            if account.normal_balance == "debit":
                running_balance = running_balance + debit - credit
            else:
                running_balance = running_balance + credit - debit

            results.append({
                "date": voucher.voucher_date,
                "voucher_no": voucher.voucher_no,
                "description": entry.description or voucher.description,
                "debit": debit,
                "credit": credit,
                "balance": running_balance,
                "reference": entry.reference,
            })

        return results

    @staticmethod
    def get_opening_balance(
        account_id: int,
        start_date: date,
    ) -> Decimal:
        """Get opening balance before start_date."""
        query = db.session.query(
            func.coalesce(func.sum(JournalEntry.debit), Decimal("0")) - 
            func.coalesce(func.sum(JournalEntry.credit), Decimal("0"))
        ).join(
            JournalVoucher, JournalEntry.voucher_id == JournalVoucher.id
        ).filter(
            JournalEntry.account_id == account_id,
            JournalVoucher.status == VoucherStatus.POSTED,
            JournalVoucher.voucher_date < start_date,
        )

        result = query.scalar()
        return Decimal(str(result)) if result else Decimal("0")

    @staticmethod
    def get_trial_balance(
        end_date: Optional[date] = None,
    ) -> List[Dict]:
        """Get trial balance - all accounts with debit/credit totals."""
        query = db.session.query(
            Account.id,
            Account.code,
            Account.name_vi,
            Account.account_type,
            Account.normal_balance,
            func.coalesce(func.sum(JournalEntry.debit), Decimal("0")).label("total_debit"),
            func.coalesce(func.sum(JournalEntry.credit), Decimal("0")).label("total_credit"),
        ).outerjoin(
            JournalEntry, Account.id == JournalEntry.account_id
        ).outerjoin(
            JournalVoucher, and_(
                JournalEntry.voucher_id == JournalVoucher.id,
                JournalVoucher.status == VoucherStatus.POSTED,
                JournalVoucher.voucher_date <= end_date if end_date else True,
            )
        ).filter(
            Account.is_active == True,
            Account.is_postable == True,
        ).group_by(
            Account.id, Account.code, Account.name_vi,
            Account.account_type, Account.normal_balance
        )

        results = []
        total_debit = Decimal("0")
        total_credit = Decimal("0")

        for row in query.all():
            debit = Decimal(str(row.total_debit))
            credit = Decimal(str(row.total_credit))

            if row.normal_balance == "debit":
                balance = debit - credit
                debit_balance = balance if balance > 0 else Decimal("0")
                credit_balance = -balance if balance < 0 else Decimal("0")
            else:
                balance = credit - debit
                credit_balance = balance if balance > 0 else Decimal("0")
                debit_balance = -balance if balance < 0 else Decimal("0")

            results.append({
                "id": row.id,
                "account_code": row.code,
                "account_name": row.name_vi,
                "account_type": row.account_type,
                "debit_balance": debit_balance,
                "credit_balance": credit_balance,
            })

            total_debit += debit_balance
            total_credit += credit_balance

        return {
            "accounts": results,
            "total_debit": total_debit,
            "total_credit": total_credit,
        }

    @staticmethod
    def get_account_turnover(
        account_id: int,
        start_date: date,
        end_date: date,
    ) -> Tuple[Decimal, Decimal]:
        """Get total debit and credit turnover for period."""
        query = db.session.query(
            func.coalesce(func.sum(JournalEntry.debit), Decimal("0")),
            func.coalesce(func.sum(JournalEntry.credit), Decimal("0")),
        ).join(
            JournalVoucher, JournalEntry.voucher_id == JournalVoucher.id
        ).filter(
            JournalEntry.account_id == account_id,
            JournalVoucher.status == VoucherStatus.POSTED,
            JournalVoucher.voucher_date >= start_date,
            JournalVoucher.voucher_date <= end_date,
        )

        result = query.first()
        return (Decimal(str(result[0])), Decimal(str(result[1]))) if result else (Decimal("0"), Decimal("0"))

    @staticmethod
    def get_posted_voucher_count(
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> int:
        """Count posted vouchers in date range."""
        query = JournalVoucher.query.filter(JournalVoucher.status == VoucherStatus.POSTED)

        if start_date:
            query = query.filter(JournalVoucher.voucher_date >= start_date)
        if end_date:
            query = query.filter(JournalVoucher.voucher_date <= end_date)

        return query.count()
