"""
Tax Repository - Database operations for tax calculations.
Based on Circular 99/2025/TT-BTC for Vietnamese accounting standards.
"""

from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Tuple

from sqlalchemy import func, and_, or_

from models.journal import JournalVoucher, JournalEntry, VoucherStatus
from models.account import Account
from models.tax_policy import TaxPolicy, TaxPolicyType
from core.database import db


class TaxRepository:
    """Repository for tax-related database operations."""

    VAT_INPUT_CODES = ["1331", "1332"]
    VAT_OUTPUT_CODES = ["3331", "33311", "33312"]
    CIT_ACCOUNT_CODES = ["8211", "8212"]
    PILLAR2_CODE = "82112"

    @classmethod
    def get_vat_accounts(cls, account_codes: List[str]) -> List[int]:
        """Get account IDs for given account codes."""
        accounts = Account.query.filter(Account.code.in_(account_codes)).all()
        return [acc.id for acc in accounts]

    @classmethod
    def get_vat_input_total(cls, start_date: date, end_date: date) -> Decimal:
        """Calculate total VAT input (debit - credit on 1331, 1332)."""
        account_ids = cls.get_vat_accounts(cls.VAT_INPUT_CODES)
        if not account_ids:
            return Decimal("0")

        result = db.session.query(
            func.coalesce(func.sum(JournalEntry.debit), 0) -
            func.coalesce(func.sum(JournalEntry.credit), 0)
        ).join(
            JournalVoucher, JournalEntry.voucher_id == JournalVoucher.id
        ).filter(
            JournalEntry.account_id.in_(account_ids),
            JournalVoucher.voucher_date >= start_date,
            JournalVoucher.voucher_date <= end_date,
            JournalVoucher.status == VoucherStatus.POSTED
        ).scalar()

        return Decimal(str(result or 0))

    @classmethod
    def get_vat_output_total(cls, start_date: date, end_date: date) -> Decimal:
        """Calculate total VAT output (credit - debit on 3331, 33311, 33312)."""
        account_ids = cls.get_vat_accounts(cls.VAT_OUTPUT_CODES)
        if not account_ids:
            return Decimal("0")

        result = db.session.query(
            func.coalesce(func.sum(JournalEntry.credit), 0) -
            func.coalesce(func.sum(JournalEntry.debit), 0)
        ).join(
            JournalVoucher, JournalEntry.voucher_id == JournalVoucher.id
        ).filter(
            JournalEntry.account_id.in_(account_ids),
            JournalVoucher.voucher_date >= start_date,
            JournalVoucher.voucher_date <= end_date,
            JournalVoucher.status == VoucherStatus.POSTED
        ).scalar()

        return Decimal(str(result or 0))

    @classmethod
    def get_vat_transactions(
        cls,
        start_date: date,
        end_date: date,
        vat_type: str = "input"
    ) -> List[Dict]:
        """Get detailed VAT transactions for a period."""
        account_codes = cls.VAT_INPUT_CODES if vat_type == "input" else cls.VAT_OUTPUT_CODES
        account_ids = cls.get_vat_accounts(account_codes)
        
        if not account_ids:
            return []

        entries = db.session.query(JournalEntry).join(
            JournalVoucher, JournalEntry.voucher_id == JournalVoucher.id
        ).filter(
            JournalEntry.account_id.in_(account_ids),
            JournalVoucher.voucher_date >= start_date,
            JournalVoucher.voucher_date <= end_date,
            JournalVoucher.status == VoucherStatus.POSTED
        ).order_by(JournalVoucher.voucher_date).all()

        transactions = []
        for entry in entries:
            voucher = entry.voucher
            account = db.session.get(Account, entry.account_id)
            
            partner_id = entry.vendor_id if vat_type == "input" else entry.customer_id
            partner_name = f"Đối tượng #{partner_id}" if partner_id else voucher.description or ""
            tax_code = ""

            amount = entry.debit if vat_type == "input" else entry.credit
            vat_rate = Decimal("0.10")
            vat_amount = amount * vat_rate / (Decimal("1") + vat_rate) if amount > 0 else Decimal("0")
            base_amount = amount - vat_amount

            transactions.append({
                "voucher_no": voucher.voucher_no,
                "voucher_date": voucher.voucher_date,
                "partner_name": partner_name,
                "tax_code": tax_code,
                "base_amount": base_amount,
                "vat_amount": vat_amount,
                "total_amount": amount,
                "vat_rate": vat_rate,
                "description": entry.description or voucher.description,
            })

        return transactions

    @classmethod
    def get_revenue_total(cls, start_date: date, end_date: date) -> Decimal:
        """Get total revenue (credit on 5xx accounts)."""
        revenue_accounts = Account.query.filter(
            Account.code.like("5%"),
            Account.is_detail == True
        ).all()
        revenue_ids = [acc.id for acc in revenue_accounts]
        
        if not revenue_ids:
            return Decimal("0")

        result = db.session.query(
            func.coalesce(func.sum(JournalEntry.credit), 0)
        ).join(
            JournalVoucher, JournalEntry.voucher_id == JournalVoucher.id
        ).filter(
            JournalEntry.account_id.in_(revenue_ids),
            JournalVoucher.voucher_date >= start_date,
            JournalVoucher.voucher_date <= end_date,
            JournalVoucher.status == VoucherStatus.POSTED
        ).scalar()

        return Decimal(str(result or 0))

    @classmethod
    def get_expense_total(cls, start_date: date, end_date: date) -> Decimal:
        """Get total expenses (debit on 6xx accounts)."""
        expense_accounts = Account.query.filter(
            Account.code.like("6%"),
            Account.is_detail == True
        ).all()
        expense_ids = [acc.id for acc in expense_accounts]
        
        if not expense_ids:
            return Decimal("0")

        result = db.session.query(
            func.coalesce(func.sum(JournalEntry.debit), 0)
        ).join(
            JournalVoucher, JournalEntry.voucher_id == JournalVoucher.id
        ).filter(
            JournalEntry.account_id.in_(expense_ids),
            JournalVoucher.voucher_date >= start_date,
            JournalVoucher.voucher_date <= end_date,
            JournalVoucher.status == VoucherStatus.POSTED
        ).scalar()

        return Decimal(str(result or 0))

    @classmethod
    def get_cit_amount(cls, start_date: date, end_date: date) -> Decimal:
        """Get CIT amount paid (debit on 8211, 8212)."""
        cit_accounts = Account.query.filter(
            Account.code.in_(cls.CIT_ACCOUNT_CODES + [cls.PILLAR2_CODE])
        ).all()
        cit_ids = [acc.id for acc in cit_accounts]
        
        if not cit_ids:
            return Decimal("0")

        result = db.session.query(
            func.coalesce(func.sum(JournalEntry.debit), 0)
        ).join(
            JournalVoucher, JournalEntry.voucher_id == JournalVoucher.id
        ).filter(
            JournalEntry.account_id.in_(cit_ids),
            JournalVoucher.voucher_date >= start_date,
            JournalVoucher.voucher_date <= end_date,
            JournalVoucher.status == VoucherStatus.POSTED
        ).scalar()

        return Decimal(str(result or 0))

    @classmethod
    def get_tax_policy(cls, tax_type: str, year: int) -> Optional[TaxPolicy]:
        """Get active tax policy for type and year."""
        return TaxPolicy.query.filter_by(
            tax_type=tax_type,
            year=year,
            active=True
        ).first()

    @classmethod
    def get_or_create_cit_policy(cls, year: int) -> TaxPolicy:
        """Get or create default CIT policy."""
        policy = cls.get_tax_policy(TaxPolicyType.CIT, year)
        if policy:
            return policy

        policy = TaxPolicy(
            tax_type=TaxPolicyType.CIT,
            year=year,
            rate=Decimal("0.20"),
            rate_name="Thuế suất TNDN thông thường",
            active=True,
            description=f"Thuế suất TNDN theo quy định pháp luật Việt Nam - Áp dụng năm {year}"
        )
        db.session.add(policy)
        db.session.commit()
        return policy

    @classmethod
    def get_all_tax_policies(cls, tax_type: Optional[str] = None) -> List[TaxPolicy]:
        """Get all tax policies, optionally filtered by type."""
        query = TaxPolicy.query
        if tax_type:
            query = query.filter_by(tax_type=tax_type)
        return query.order_by(TaxPolicy.year.desc()).all()

    @classmethod
    def create_tax_policy(
        cls,
        tax_type: str,
        year: int,
        rate: Decimal,
        rate_name: str,
        description: str = ""
    ) -> TaxPolicy:
        """Create a new tax policy."""
        existing = cls.get_tax_policy(tax_type, year)
        if existing:
            existing.rate = rate
            existing.rate_name = rate_name
            existing.description = description
            db.session.commit()
            return existing

        policy = TaxPolicy(
            tax_type=tax_type,
            year=year,
            rate=rate,
            rate_name=rate_name,
            active=True,
            description=description
        )
        db.session.add(policy)
        db.session.commit()
        return policy

    @classmethod
    def get_monthly_vat_summary(cls, year: int) -> List[Dict]:
        """Get monthly VAT summary for a year."""
        summaries = []
        for month in range(1, 13):
            start_date = date(year, month, 1)
            if month == 12:
                end_date = date(year, 12, 31)
            else:
                end_date = date(year, month + 1, 1) - timedelta(days=1)

            vat_input = cls.get_vat_input_total(start_date, end_date)
            vat_output = cls.get_vat_output_total(start_date, end_date)

            summaries.append({
                "month": month,
                "year": year,
                "period": f"{year}/{month:02d}",
                "start_date": start_date,
                "end_date": end_date,
                "vat_input": vat_input,
                "vat_output": vat_output,
                "vat_payable": max(Decimal("0"), vat_output - vat_input),
                "vat_refundable": max(Decimal("0"), vat_input - vat_output),
            })
        return summaries

    @classmethod
    def get_quarterly_vat_summary(cls, year: int) -> List[Dict]:
        """Get quarterly VAT summary for a year."""
        quarters = [
            (1, 1, 3),
            (2, 4, 6),
            (3, 7, 9),
            (4, 10, 12),
        ]
        summaries = []
        for q, start_month, end_month in quarters:
            start_date = date(year, start_month, 1)
            end_date = date(year, end_month, 1) + timedelta(days=31)
            end_date = date(end_date.year, end_date.month, 1) - timedelta(days=1)
            
            vat_input = Decimal("0")
            vat_output = Decimal("0")
            for month in range(start_month, end_month + 1):
                m_start = date(year, month, 1)
                m_end = date(year, month, 1) + timedelta(days=32)
                m_end = date(m_end.year, m_end.month, 1) - timedelta(days=1)
                vat_input += cls.get_vat_input_total(m_start, m_end)
                vat_output += cls.get_vat_output_total(m_start, m_end)

            summaries.append({
                "quarter": q,
                "year": year,
                "period": f"Q{q}/{year}",
                "start_date": start_date,
                "end_date": end_date,
                "vat_input": vat_input,
                "vat_output": vat_output,
                "vat_payable": max(Decimal("0"), vat_output - vat_input),
                "vat_refundable": max(Decimal("0"), vat_input - vat_output),
            })
        return summaries

    @classmethod
    def get_account_balance(cls, account_code: str, end_date: date) -> Decimal:
        """Get account balance up to a date."""
        account = Account.query.filter_by(code=account_code, is_detail=True).first()
        if not account:
            return Decimal("0")

        entries = db.session.query(
            func.coalesce(func.sum(JournalEntry.debit), 0),
            func.coalesce(func.sum(JournalEntry.credit), 0)
        ).join(
            JournalVoucher, JournalEntry.voucher_id == JournalVoucher.id
        ).filter(
            JournalEntry.account_id == account.id,
            JournalVoucher.voucher_date <= end_date,
            JournalVoucher.status == VoucherStatus.POSTED
        ).group_by(JournalEntry.account_id).first()

        if not entries:
            return Decimal("0")

        debit_total, credit_total = entries
        if account.normal_balance == "debit":
            return Decimal(str(debit_total or 0)) - Decimal(str(credit_total or 0))
        else:
            return Decimal(str(credit_total or 0)) - Decimal(str(debit_total or 0))
