"""Bank & Cash Service - Bank reconciliation and cash flow."""

from datetime import date, timedelta
from decimal import Decimal
from typing import Dict, List, Optional

from core.database import db
from models.bank import BankAccount, BankReconciliation, BankStatement, ReconciliationStatus
from models.journal import JournalEntry, JournalVoucher
from sqlalchemy import func


class BankService:
    """Service for bank operations."""

    @staticmethod
    def get_all_bank_accounts() -> List[BankAccount]:
        """Get all bank accounts."""
        return BankAccount.query.filter_by(is_active=True).all()

    @staticmethod
    def get_bank_account(account_id: int) -> Optional[BankAccount]:
        """Get bank account by ID."""
        return db.session.get(BankAccount, account_id)

    @staticmethod
    def create_bank_account(account_data: Dict) -> BankAccount:
        """Create new bank account."""
        existing = BankAccount.query.filter_by(code=account_data["code"]).first()
        if existing:
            raise ValueError(f"Mã tài khoản ngân hàng {account_data['code']} đã tồn tại")

        bank_account = BankAccount(
            code=account_data["code"],
            name=account_data["name"],
            bank_name=account_data.get("bank_name"),
            account_number=account_data.get("account_number"),
            account_id=account_data["account_id"],
            currency=account_data.get("currency", "VND"),
            opening_balance=account_data.get("opening_balance", Decimal("0")),
            current_balance=account_data.get("opening_balance", Decimal("0")),
            is_active=True,
        )
        db.session.add(bank_account)
        db.session.commit()
        return bank_account

    @staticmethod
    def update_bank_balance(bank_account_id: int) -> None:
        """Update bank account balance from journal entries."""
        bank_account = db.session.get(BankAccount, bank_account_id)
        if not bank_account:
            return

        entries = JournalEntry.query.join(JournalVoucher).filter(
            JournalEntry.account_id == bank_account.account_id,
            JournalVoucher.status == "posted",
        ).all()

        total_debit = sum(e.debit for e in entries)
        total_credit = sum(e.credit for e in entries)

        bank_account.current_balance = bank_account.opening_balance + total_debit - total_credit
        db.session.commit()

    @staticmethod
    def import_statement(bank_account_id: int, statement_data: Dict) -> BankStatement:
        """Import bank statement."""
        bank_account = db.session.get(BankAccount, bank_account_id)
        if not bank_account:
            raise ValueError("Bank account not found")

        statement = BankStatement(
            bank_account_id=bank_account_id,
            statement_date=statement_data["statement_date"],
            statement_no=statement_data["statement_no"],
            description=statement_data.get("description"),
            debit=statement_data.get("debit", Decimal("0")),
            credit=statement_data.get("credit", Decimal("0")),
            balance=statement_data.get("balance", Decimal("0")),
            reference=statement_data.get("reference"),
            is_reconciled=False,
        )
        db.session.add(statement)
        db.session.commit()
        return statement

    @staticmethod
    def get_unreconciled_statements(bank_account_id: int) -> List[BankStatement]:
        """Get unreconciled bank statements."""
        return BankStatement.query.filter_by(
            bank_account_id=bank_account_id,
            is_reconciled=False,
        ).order_by(BankStatement.statement_date).all()

    @staticmethod
    def create_reconciliation(
        bank_account_id: int,
        period_year: int,
        period_month: int,
        user_id: int,
    ) -> BankReconciliation:
        """Create bank reconciliation for a period."""
        existing = BankReconciliation.query.filter_by(
            bank_account_id=bank_account_id,
            period_year=period_year,
            period_month=period_month,
        ).first()

        if existing:
            raise ValueError(f"Đã có đối chiếu ngân hàng kỳ {period_month}/{period_year}")

        bank_account = db.session.get(BankAccount, bank_account_id)
        if not bank_account:
            raise ValueError("Bank account not found")

        stmt = BankStatement.query.filter(
            BankStatement.bank_account_id == bank_account_id,
        ).order_by(BankStatement.statement_date.desc()).first()

        bank_balance = stmt.balance if stmt else bank_account.opening_balance
        book_balance = bank_account.current_balance

        reconciliation = BankReconciliation(
            bank_account_id=bank_account_id,
            reconciliation_date=date.today(),
            period_year=period_year,
            period_month=period_month,
            bank_balance=bank_balance,
            book_balance=book_balance,
            reconciled_balance=bank_balance,
            status=ReconciliationStatus.DRAFT,
            created_by=user_id,
        )
        db.session.add(reconciliation)
        db.session.commit()
        return reconciliation

    @staticmethod
    def complete_reconciliation(
        reconciliation_id: int,
        deposit_in_transit: Decimal,
        outstanding_checks: Decimal,
        bank_charges: Decimal,
        interest_income: Decimal,
    ) -> BankReconciliation:
        """Complete bank reconciliation."""
        recon = db.session.get(BankReconciliation, reconciliation_id)
        if not recon:
            raise ValueError("Reconciliation not found")

        recon.deposit_in_transit = deposit_in_transit
        recon.outstanding_checks = outstanding_checks
        recon.bank_charges = bank_charges
        recon.interest_income = interest_income
        recon.reconciled_balance = (
            recon.bank_balance - deposit_in_transit + outstanding_checks - bank_charges + interest_income
        )
        recon.status = ReconciliationStatus.COMPLETED
        db.session.commit()
        return recon


class CashFlowService:
    """Service for cash flow statements."""

    @staticmethod
    def get_cash_flow_statement(
        start_date: date,
        end_date: date,
        method: str = "indirect",
    ) -> Dict:
        """Generate cash flow statement."""
        cash_accounts = Account.query.filter(
            Account.code.in_(["111", "112"])
        ).all()
        cash_account_ids = [acc.id for acc in cash_accounts]
        
        if not cash_account_ids:
            return {
                "start_date": start_date,
                "end_date": end_date,
                "method": method,
                "operating_activities": Decimal("0"),
                "investing_activities": Decimal("0"),
                "financing_activities": Decimal("0"),
                "net_change": Decimal("0"),
            }
        
        cash_inflows = db.session.query(
            func.coalesce(func.sum(JournalEntry.debit), Decimal("0"))
        ).join(JournalVoucher).filter(
            JournalEntry.account_id.in_(cash_account_ids),
            JournalVoucher.voucher_date >= start_date,
            JournalVoucher.voucher_date <= end_date,
            JournalVoucher.status == "posted",
        ).scalar() or Decimal("0")

        cash_outflows = db.session.query(
            func.coalesce(func.sum(JournalEntry.credit), Decimal("0"))
        ).join(JournalVoucher).filter(
            JournalEntry.account_id.in_(cash_account_ids),
            JournalVoucher.voucher_date >= start_date,
            JournalVoucher.voucher_date <= end_date,
            JournalVoucher.status == "posted",
        ).scalar() or Decimal("0")

        net_change = cash_inflows - cash_outflows

        return {
            "start_date": start_date,
            "end_date": end_date,
            "method": method,
            "operating_activities": CashFlowService._get_operating_cash_flow(start_date, end_date),
            "investing_activities": CashFlowService._get_investing_cash_flow(start_date, end_date),
            "financing_activities": CashFlowService._get_financing_cash_flow(start_date, end_date),
            "net_change": net_change,
        }

    @staticmethod
    def _get_operating_cash_flow(start_date: date, end_date: date) -> Decimal:
        """Calculate operating cash flow."""
        revenue_accounts = Account.query.filter(
            Account.code.in_(["511", "5111", "5112", "5113", "5114", "5115", "5116", "5117", "5118", "515"])
        ).all()
        expense_accounts = Account.query.filter(
            Account.code.in_(["621", "622", "623", "627", "632", "635", "641", "642"])
        ).all()
        
        revenue_ids = [acc.id for acc in revenue_accounts]
        expense_ids = [acc.id for acc in expense_accounts]
        
        cash_received = Decimal("0")
        if revenue_ids:
            cash_received = db.session.query(
                func.coalesce(func.sum(JournalEntry.credit), Decimal("0"))
            ).join(JournalVoucher).filter(
                JournalEntry.account_id.in_(revenue_ids),
                JournalVoucher.voucher_date >= start_date,
                JournalVoucher.voucher_date <= end_date,
                JournalVoucher.status == "posted",
            ).scalar() or Decimal("0")

        cash_paid = Decimal("0")
        if expense_ids:
            cash_paid = db.session.query(
                func.coalesce(func.sum(JournalEntry.debit), Decimal("0"))
            ).join(JournalVoucher).filter(
                JournalEntry.account_id.in_(expense_ids),
                JournalVoucher.voucher_date >= start_date,
                JournalVoucher.voucher_date <= end_date,
                JournalVoucher.status == "posted",
            ).scalar() or Decimal("0")

        return cash_received - cash_paid

    @staticmethod
    def _get_investing_cash_flow(start_date: date, end_date: date) -> Decimal:
        """Calculate investing cash flow."""
        fixed_asset_accounts = Account.query.filter(
            Account.code.in_(["211", "212", "213", "241"])
        ).all()
        
        asset_ids = [acc.id for acc in fixed_asset_accounts]
        
        asset_purchases = Decimal("0")
        if asset_ids:
            asset_purchases = db.session.query(
                func.coalesce(func.sum(JournalEntry.debit), Decimal("0"))
            ).join(JournalVoucher).filter(
                JournalEntry.account_id.in_(asset_ids),
                JournalVoucher.voucher_date >= start_date,
                JournalVoucher.voucher_date <= end_date,
                JournalVoucher.status == "posted",
            ).scalar() or Decimal("0")

        asset_disposals = Decimal("0")
        if asset_ids:
            asset_disposals = db.session.query(
                func.coalesce(func.sum(JournalEntry.credit), Decimal("0"))
            ).join(JournalVoucher).filter(
                JournalEntry.account_id.in_(asset_ids),
                JournalVoucher.voucher_date >= start_date,
                JournalVoucher.voucher_date <= end_date,
                JournalVoucher.status == "posted",
            ).scalar() or Decimal("0")

        return asset_disposals - asset_purchases

    @staticmethod
    def _get_financing_cash_flow(start_date: date, end_date: date) -> Decimal:
        """Calculate financing cash flow."""
        equity_accounts = Account.query.filter(
            Account.code.in_(["411", "4111", "4112", "412", "413", "414", "418", "419", "421", "4211", "4212"])
        ).all()
        loan_accounts = Account.query.filter(
            Account.code.in_(["311", "341", "343"])
        ).all()
        
        equity_ids = [acc.id for acc in equity_accounts]
        loan_ids = [acc.id for acc in loan_accounts]
        
        capital_received = Decimal("0")
        if equity_ids:
            capital_received = db.session.query(
                func.coalesce(func.sum(JournalEntry.credit), Decimal("0"))
            ).join(JournalVoucher).filter(
                JournalEntry.account_id.in_(equity_ids),
                JournalVoucher.voucher_date >= start_date,
                JournalVoucher.voucher_date <= end_date,
                JournalVoucher.status == "posted",
            ).scalar() or Decimal("0")

        loans_received = Decimal("0")
        if loan_ids:
            loans_received = db.session.query(
                func.coalesce(func.sum(JournalEntry.credit), Decimal("0"))
            ).join(JournalVoucher).filter(
                JournalEntry.account_id.in_(loan_ids),
                JournalVoucher.voucher_date >= start_date,
                JournalVoucher.voucher_date <= end_date,
                JournalVoucher.status == "posted",
        ).scalar() or Decimal("0")

        return asset_disposals - asset_purchases

    @staticmethod
    def _get_financing_cash_flow(start_date: date, end_date: date) -> Decimal:
        """Calculate financing cash flow."""
        equity_accounts = [411, 421]
        loan_accounts = [311, 341]
        
        capital_received = db.session.query(
            func.coalesce(func.sum(JournalEntry.credit), Decimal("0"))
        ).join(JournalVoucher).filter(
            JournalEntry.account_id.in_(equity_accounts),
            JournalVoucher.voucher_date >= start_date,
            JournalVoucher.voucher_date <= end_date,
            JournalVoucher.status == "posted",
        ).scalar() or Decimal("0")

        loans_received = db.session.query(
            func.coalesce(func.sum(JournalEntry.credit), Decimal("0"))
        ).join(JournalVoucher).filter(
            JournalEntry.account_id.in_(loan_accounts),
            JournalVoucher.voucher_date >= start_date,
            JournalVoucher.voucher_date <= end_date,
            JournalVoucher.status == "posted",
        ).scalar() or Decimal("0")

        return capital_received + loans_received
