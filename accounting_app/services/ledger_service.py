from datetime import date, datetime
from decimal import Decimal
from typing import Dict, List, Optional

from models.account import Account, AccountType
from repositories.account_repository import AccountRepository
from repositories.ledger_repository import LedgerRepository


class LedgerService:
    """Service for General Ledger operations."""

    @staticmethod
    def get_account_balance(
        account_id: int,
        end_date: Optional[date] = None,
    ) -> Decimal:
        """Get account balance up to date."""
        return LedgerRepository.get_account_balance(account_id, end_date)

    @staticmethod
    def get_ledger(
        account_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Dict:
        """Get complete ledger for an account."""
        account = AccountRepository.get_by_id(account_id)
        if not account:
            raise ValueError(f"Tài khoản {account_id} không tồn tại")

        opening_balance = Decimal("0")
        if start_date:
            opening_balance = LedgerRepository.get_opening_balance(account_id, start_date)

        entries = LedgerRepository.get_ledger_entries(account_id, start_date, end_date)

        closing_balance = opening_balance
        for entry in entries:
            if account.normal_balance == "debit":
                closing_balance = closing_balance + entry["debit"] - entry["credit"]
            else:
                closing_balance = closing_balance + entry["credit"] - entry["debit"]

        return {
            "account": account,
            "start_date": start_date,
            "end_date": end_date,
            "opening_balance": opening_balance,
            "entries": entries,
            "closing_balance": closing_balance,
        }

    @staticmethod
    def get_trial_balance(
        end_date: Optional[date] = None,
    ) -> Dict:
        """Get trial balance report.

        Validates: Total Debit = Total Credit
        """
        result = LedgerRepository.get_trial_balance(end_date)

        is_balanced = abs(result["total_debit"] - result["total_credit"]) == Decimal("0")

        return {
            "accounts": result["accounts"],
            "total_debit": result["total_debit"],
            "total_credit": result["total_credit"],
            "is_balanced": is_balanced,
            "end_date": end_date,
        }

    @staticmethod
    def get_general_ledger(
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[Dict]:
        """Get general ledger - all accounts with their balances."""
        accounts = AccountRepository.get_detail_accounts()

        ledger_data = []
        for account in accounts:
            opening_balance = Decimal("0")
            if start_date:
                opening_balance = LedgerRepository.get_opening_balance(account.id, start_date)

            entries = LedgerRepository.get_ledger_entries(account.id, start_date, end_date)

            closing_balance = opening_balance
            for entry in entries:
                if account.normal_balance == "debit":
                    closing_balance = closing_balance + entry["debit"] - entry["credit"]
                else:
                    closing_balance = closing_balance + entry["credit"] - entry["debit"]

            if opening_balance != Decimal("0") or closing_balance != Decimal("0") or entries:
                ledger_data.append({
                    "account": account,
                    "opening_balance": opening_balance,
                    "entries": entries,
                    "closing_balance": closing_balance,
                })

        return ledger_data

    @staticmethod
    def get_account_statement(
        account_id: int,
        start_date: date,
        end_date: date,
    ) -> Dict:
        """Get account statement for a period."""
        account = AccountRepository.get_by_id(account_id)
        if not account:
            raise ValueError(f"Tài khoản {account_id} không tồn tại")

        opening_balance = LedgerRepository.get_opening_balance(account_id, start_date)
        entries = LedgerRepository.get_ledger_entries(account_id, start_date, end_date)

        debit_turnover = sum(e["debit"] for e in entries)
        credit_turnover = sum(e["credit"] for e in entries)

        if account.normal_balance == "debit":
            closing_balance = opening_balance + debit_turnover - credit_turnover
        else:
            closing_balance = opening_balance + credit_turnover - debit_turnover

        return {
            "account": account,
            "start_date": start_date,
            "end_date": end_date,
            "opening_balance": opening_balance,
            "entries": entries,
            "debit_turnover": debit_turnover,
            "credit_turnover": credit_turnover,
            "closing_balance": closing_balance,
        }

    @staticmethod
    def validate_trial_balance(end_date: Optional[date] = None) -> Dict:
        """Validate trial balance - returns validation result."""
        result = LedgerService.get_trial_balance(end_date)

        return {
            "is_valid": result["is_balanced"],
            "difference": abs(result["total_debit"] - result["total_credit"]),
            "total_debit": result["total_debit"],
            "total_credit": result["total_credit"],
        }

    @staticmethod
    def get_accounts_with_activity(
        start_date: date,
        end_date: date,
    ) -> List[Account]:
        """Get all accounts with activity in date range."""
        from models.journal import JournalEntry, JournalVoucher
        from sqlalchemy import distinct

        account_ids = db.session.query(distinct(JournalEntry.account_id)).join(
            JournalVoucher, JournalEntry.voucher_id == JournalVoucher.id
        ).filter(
            JournalVoucher.status == VoucherStatus.POSTED,
            JournalVoucher.voucher_date >= start_date,
            JournalVoucher.voucher_date <= end_date,
        ).all()

        return [AccountRepository.get_by_id(a[0]) for a in account_ids if AccountRepository.get_by_id(a[0])]


from core.database import db
from models.journal import VoucherStatus
