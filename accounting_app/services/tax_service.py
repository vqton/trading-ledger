"""
Tax Service - VAT tracking and tax reports.
Based on Circular 99/2025/TT-BTC for Vietnamese accounting standards.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Dict, List, Optional
from dataclasses import dataclass

from models.account import Account
from models.journal import JournalVoucher, JournalEntry, VoucherStatus
from models.tax_policy import TaxPolicy, TaxPolicyType, get_active_policy
from core.database import db


@dataclass
class VATTransaction:
    """VAT transaction detail."""
    voucher_no: str
    voucher_date: date
    partner_name: str
    tax_code: str
    amount: Decimal
    vat_rate: Decimal
    vat_amount: Decimal
    vat_input: bool


@dataclass
class VATDeclaration:
    """Monthly VAT declaration data."""
    period: str
    year: int
    month: int
    vat_input: Decimal
    vat_output: Decimal
    vat_payable: Decimal
    vat_refundable: Decimal
    transactions: List[VATTransaction]


class TaxService:
    """Service for tax calculations and reporting."""
    
    VAT_INPUT_ACCOUNTS = ["1331", "1332"]  # VAT receivable
    VAT_OUTPUT_ACCOUNTS = ["3331", "33311", "33312"]  # VAT payable
    VAT_RATES = {
        "0": Decimal("0"),
        "5": Decimal("0.05"),
        "10": Decimal("0.10"),
    }
    
    DEFAULT_CIT_RATE = Decimal("0.20")  # Default 20% as per current regulations
    
    @staticmethod
    def _get_cit_rate(year: int) -> Decimal:
        """Get CIT rate from policy, fallback to default 20%."""
        policy = get_active_policy(TaxPolicyType.CIT, year)
        if policy and policy.rate:
            return Decimal(str(policy.rate))
        return TaxService.DEFAULT_CIT_RATE
    
    @staticmethod
    def get_cit_rate(year: int) -> Decimal:
        """Public method to get CIT rate for a year."""
        return TaxService._get_cit_rate(year)
    
    @staticmethod
    def get_cit_policy(year: int) -> Optional[TaxPolicy]:
        """Get CIT policy for a year."""
        return get_active_policy(TaxPolicyType.CIT, year)
    
    @staticmethod
    def get_vat_rate(year: int, vat_type: str = "vat_output") -> Decimal:
        """Get VAT rate from policy, fallback to default rates."""
        policy = get_active_policy(vat_type, year)
        if policy and policy.rate:
            return Decimal(str(policy.rate))
        return TaxService.VAT_RATES.get("10", Decimal("0.10"))
    
    @staticmethod
    def get_vat_input(start_date: date, end_date: date) -> Decimal:
        """Get total VAT input for a period."""
        vat_accounts = Account.query.filter(
            Account.code.in_(TaxService.VAT_INPUT_ACCOUNTS)
        ).all()
        
        if not vat_accounts:
            return Decimal("0")
        
        vat_account_ids = [acc.id for acc in vat_accounts]
        
        total = db.session.query(
            db.func.coalesce(db.func.sum(JournalEntry.debit), 0) -
            db.func.coalesce(db.func.sum(JournalEntry.credit), 0)
        ).join(JournalVoucher).filter(
            JournalEntry.account_id.in_(vat_account_ids),
            JournalVoucher.voucher_date >= start_date,
            JournalVoucher.voucher_date <= end_date,
            JournalVoucher.status == VoucherStatus.POSTED
        ).scalar() or Decimal("0")
        
        return Decimal(str(total))
    
    @staticmethod
    def get_vat_output(start_date: date, end_date: date) -> Decimal:
        """Get total VAT output for a period."""
        vat_accounts = Account.query.filter(
            Account.code.in_(TaxService.VAT_OUTPUT_ACCOUNTS)
        ).all()
        
        if not vat_accounts:
            return Decimal("0")
        
        vat_account_ids = [acc.id for acc in vat_accounts]
        
        total = db.session.query(
            db.func.coalesce(db.func.sum(JournalEntry.credit), 0) -
            db.func.coalesce(db.func.sum(JournalEntry.debit), 0)
        ).join(JournalVoucher).filter(
            JournalEntry.account_id.in_(vat_account_ids),
            JournalVoucher.voucher_date >= start_date,
            JournalVoucher.voucher_date <= end_date,
            JournalVoucher.status == VoucherStatus.POSTED
        ).scalar() or Decimal("0")
        
        return Decimal(str(total))
    
    @staticmethod
    def get_vat_declaration(year: int, month: int) -> VATDeclaration:
        """Get monthly VAT declaration."""
        start_date = date(year, month, 1)
        
        if month == 12:
            end_date = date(year, 12, 31)
        else:
            from datetime import timedelta
            end_date = date(year, month + 1, 1) - timedelta(days=1)
        
        vat_input = TaxService.get_vat_input(start_date, end_date)
        vat_output = TaxService.get_vat_output(start_date, end_date)
        
        vat_payable = max(Decimal("0"), vat_output - vat_input)
        vat_refundable = max(Decimal("0"), vat_input - vat_output)
        
        return VATDeclaration(
            period=f"{year}/{month:02d}",
            year=year,
            month=month,
            vat_input=vat_input,
            vat_output=vat_output,
            vat_payable=vat_payable,
            vat_refundable=vat_refundable,
            transactions=[],
        )
    
    @staticmethod
    def estimate_tndn(year: int) -> Dict:
        """Estimate corporate income tax based on profit using policy rate."""
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
        
        revenue_accounts = Account.query.filter(
            Account.code.like("5%"),
            Account.is_postable == True
        ).all()
        revenue_ids = [acc.id for acc in revenue_accounts]
        
        total_revenue = Decimal("0")
        if revenue_ids:
            total_revenue = db.session.query(
                db.func.coalesce(db.func.sum(JournalEntry.credit), 0)
            ).join(JournalVoucher).filter(
                JournalEntry.account_id.in_(revenue_ids),
                JournalVoucher.voucher_date >= start_date,
                JournalVoucher.voucher_date <= end_date,
                JournalVoucher.status == VoucherStatus.POSTED
            ).scalar() or Decimal("0")
        
        expense_accounts = Account.query.filter(
            Account.code.like("6%"),
            Account.is_postable == True
        ).all()
        expense_ids = [acc.id for acc in expense_accounts]
        
        total_expense = Decimal("0")
        if expense_ids:
            total_expense = db.session.query(
                db.func.coalesce(db.func.sum(JournalEntry.debit), 0)
            ).join(JournalVoucher).filter(
                JournalEntry.account_id.in_(expense_ids),
                JournalVoucher.voucher_date >= start_date,
                JournalVoucher.voucher_date <= end_date,
                JournalVoucher.status == VoucherStatus.POSTED
            ).scalar() or Decimal("0")
        
        gross_profit = Decimal(str(total_revenue)) - Decimal(str(total_expense))
        
        cit_rate = TaxService._get_cit_rate(year)
        estimated_tax = max(Decimal("0"), gross_profit * cit_rate)
        
        policy = TaxService.get_cit_policy(year)
        
        return {
            "year": year,
            "total_revenue": Decimal(str(total_revenue)),
            "total_expense": Decimal(str(total_expense)),
            "gross_profit": gross_profit,
            "cit_rate": cit_rate,
            "cit_rate_percentage": int(cit_rate * 100),
            "tax_rate": f"{int(cit_rate * 100)}%",
            "estimated_tax": estimated_tax,
            "policy_name": policy.rate_name if policy else "Thuế suất TNDN",
            "policy_description": policy.description if policy else f"Áp dụng năm {year}",
        }
    
    @staticmethod
    def get_tax_summary(year: int) -> List[Dict]:
        """Get monthly tax summary for a year."""
        summaries = []
        
        for month in range(1, 13):
            declaration = TaxService.get_vat_declaration(year, month)
            
            if declaration.vat_input > 0 or declaration.vat_output > 0:
                summaries.append({
                    "month": month,
                    "period": declaration.period,
                    "vat_input": declaration.vat_input,
                    "vat_output": declaration.vat_output,
                    "vat_payable": declaration.vat_payable,
                })
        
        return summaries
    
    @staticmethod
    def get_all_cit_policies() -> List[TaxPolicy]:
        """Get all CIT policies."""
        return TaxPolicy.query.filter_by(tax_type=TaxPolicyType.CIT).order_by(TaxPolicy.year.desc()).all()
