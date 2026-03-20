"""
Tax Service - VAT tracking and tax reports.
Based on Circular 99/2025/TT-BTC for Vietnamese accounting standards.
"""

from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

from models.account import Account
from models.journal import JournalVoucher, JournalEntry, VoucherStatus
from models.tax_policy import TaxPolicy, TaxPolicyType, get_active_policy
from repositories.tax_repository import TaxRepository
from core.database import db


@dataclass
class VATTransaction:
    """VAT transaction detail."""
    voucher_no: str
    voucher_date: date
    partner_name: str
    tax_code: str
    base_amount: Decimal
    vat_amount: Decimal
    total_amount: Decimal
    vat_rate: Decimal
    vat_input: bool
    description: str = ""


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
    transactions_input: List[Dict]
    transactions_output: List[Dict]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "period": self.period,
            "year": self.year,
            "month": self.month,
            "vat_input": self.vat_input,
            "vat_output": self.vat_output,
            "vat_payable": self.vat_payable,
            "vat_refundable": self.vat_refundable,
            "transactions_input": self.transactions_input,
            "transactions_output": self.transactions_output,
        }


@dataclass
class CITEstimate:
    """CIT estimate data."""
    year: int
    total_revenue: Decimal
    total_expense: Decimal
    gross_profit: Decimal
    cit_rate: Decimal
    estimated_tax: Decimal
    paid_tax: Decimal
    outstanding_tax: Decimal

    def to_dict(self) -> Dict[str, Any]:
        return {
            "year": self.year,
            "total_revenue": self.total_revenue,
            "total_expense": self.total_expense,
            "gross_profit": self.gross_profit,
            "cit_rate": self.cit_rate,
            "estimated_tax": self.estimated_tax,
            "paid_tax": self.paid_tax,
            "outstanding_tax": self.outstanding_tax,
        }


@dataclass
class QuarterlyVATSummary:
    """Quarterly VAT summary."""
    quarter: int
    year: int
    period: str
    start_date: date
    end_date: date
    vat_input: Decimal
    vat_output: Decimal
    vat_payable: Decimal
    vat_refundable: Decimal

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class TaxService:
    """Service for tax calculations and reporting."""

    VAT_RATES = {
        "0": Decimal("0"),
        "5": Decimal("0.05"),
        "8": Decimal("0.08"),
        "10": Decimal("0.10"),
    }

    DEFAULT_CIT_RATE = Decimal("0.20")

    @staticmethod
    def get_vat_declaration(year: int, month: int) -> VATDeclaration:
        """Get monthly VAT declaration with transaction details."""
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year, 12, 31)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)

        vat_input = TaxRepository.get_vat_input_total(start_date, end_date)
        vat_output = TaxRepository.get_vat_output_total(start_date, end_date)

        transactions_input = TaxRepository.get_vat_transactions(start_date, end_date, "input")
        transactions_output = TaxRepository.get_vat_transactions(start_date, end_date, "output")

        return VATDeclaration(
            period=f"{year}/{month:02d}",
            year=year,
            month=month,
            vat_input=vat_input,
            vat_output=vat_output,
            vat_payable=max(Decimal("0"), vat_output - vat_input),
            vat_refundable=max(Decimal("0"), vat_input - vat_output),
            transactions_input=transactions_input,
            transactions_output=transactions_output,
        )

    @staticmethod
    def get_monthly_vat_summary(year: int) -> List[Dict]:
        """Get monthly VAT summary for a year."""
        return TaxRepository.get_monthly_vat_summary(year)

    @staticmethod
    def get_quarterly_vat_summary(year: int) -> List[QuarterlyVATSummary]:
        """Get quarterly VAT summary for a year."""
        summaries = TaxRepository.get_quarterly_vat_summary(year)
        return [QuarterlyVATSummary(**s) for s in summaries]

    @staticmethod
    def get_cit_estimate(year: int) -> CITEstimate:
        """Get CIT estimate for a year."""
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)

        total_revenue = TaxRepository.get_revenue_total(start_date, end_date)
        total_expense = TaxRepository.get_expense_total(start_date, end_date)
        gross_profit = total_revenue - total_expense

        policy = TaxRepository.get_or_create_cit_policy(year)
        cit_rate = Decimal(str(policy.rate))

        estimated_tax = max(Decimal("0"), gross_profit * cit_rate)

        paid_tax = TaxRepository.get_cit_amount(start_date, end_date)

        return CITEstimate(
            year=year,
            total_revenue=total_revenue,
            total_expense=total_expense,
            gross_profit=gross_profit,
            cit_rate=cit_rate,
            estimated_tax=estimated_tax,
            paid_tax=paid_tax,
            outstanding_tax=estimated_tax - paid_tax,
        )

    @staticmethod
    def get_quarterly_cit_estimate(year: int, quarter: int) -> CITEstimate:
        """Get CIT estimate for a specific quarter."""
        start_month = (quarter - 1) * 3 + 1
        end_month = start_month + 2
        start_date = date(year, start_month, 1)
        end_date = date(year, end_month, 1) + timedelta(days=31)
        end_date = date(end_date.year, end_date.month, 1) - timedelta(days=1)

        total_revenue = TaxRepository.get_revenue_total(start_date, end_date)
        total_expense = TaxRepository.get_expense_total(start_date, end_date)
        gross_profit = total_revenue - total_expense

        policy = TaxRepository.get_or_create_cit_policy(year)
        cit_rate = Decimal(str(policy.rate))

        estimated_tax = max(Decimal("0"), gross_profit * cit_rate)
        paid_tax = TaxRepository.get_cit_amount(start_date, end_date)

        return CITEstimate(
            year=year,
            total_revenue=total_revenue,
            total_expense=total_expense,
            gross_profit=gross_profit,
            cit_rate=cit_rate,
            estimated_tax=estimated_tax,
            paid_tax=paid_tax,
            outstanding_tax=estimated_tax - paid_tax,
        )

    @staticmethod
    def get_cit_rate(year: int) -> Decimal:
        """Get CIT rate for a year."""
        policy = TaxRepository.get_or_create_cit_policy(year)
        return Decimal(str(policy.rate))

    @staticmethod
    def calculate_vat_from_amount(amount: Decimal, vat_rate_str: str = "10") -> Dict[str, Decimal]:
        """Calculate VAT from amount including VAT."""
        vat_rate = TaxService.VAT_RATES.get(vat_rate_str, Decimal("0.10"))
        vat_amount = amount * vat_rate / (Decimal("1") + vat_rate)
        base_amount = amount - vat_amount
        return {
            "base_amount": base_amount,
            "vat_amount": vat_amount,
            "total_amount": amount,
            "vat_rate": vat_rate,
        }

    @staticmethod
    def calculate_vat_exclusive(amount: Decimal, vat_rate_str: str = "10") -> Dict[str, Decimal]:
        """Calculate VAT from amount excluding VAT."""
        vat_rate = TaxService.VAT_RATES.get(vat_rate_str, Decimal("0.10"))
        vat_amount = amount * vat_rate
        total_amount = amount + vat_amount
        return {
            "base_amount": amount,
            "vat_amount": vat_amount,
            "total_amount": total_amount,
            "vat_rate": vat_rate,
        }

    @staticmethod
    def get_vat_account_balances(end_date: date) -> Dict[str, Decimal]:
        """Get VAT account balances."""
        return {
            "vat_input": TaxRepository.get_account_balance("1331", end_date),
            "vat_input_import": TaxRepository.get_account_balance("1332", end_date),
            "vat_output": TaxRepository.get_account_balance("3331", end_date),
        }

    @staticmethod
    def get_tax_summary(year: int) -> Dict[str, Any]:
        """Get comprehensive tax summary for a year."""
        monthly_vat = TaxService.get_monthly_vat_summary(year)
        quarterly_vat = [s.to_dict() for s in TaxService.get_quarterly_vat_summary(year)]
        cit_estimate = TaxService.get_cit_estimate(year)

        total_vat_payable = sum(m["vat_payable"] for m in monthly_vat)
        total_vat_refundable = sum(m["vat_refundable"] for m in monthly_vat)

        return {
            "year": year,
            "monthly_vat": monthly_vat,
            "quarterly_vat": quarterly_vat,
            "cit_estimate": cit_estimate.to_dict(),
            "total_vat_payable": total_vat_payable,
            "total_vat_refundable": total_vat_refundable,
        }

    @staticmethod
    def get_tax_policies(tax_type: Optional[str] = None) -> List[TaxPolicy]:
        """Get all tax policies."""
        return TaxRepository.get_all_tax_policies(tax_type)

    @staticmethod
    def create_tax_policy(
        tax_type: str,
        year: int,
        rate: Decimal,
        rate_name: str,
        description: str = ""
    ) -> TaxPolicy:
        """Create or update tax policy."""
        return TaxRepository.create_tax_policy(tax_type, year, rate, rate_name, description)
