"""
Tax Engine - Centralized tax calculation and validation engine.
Based on Circular 99/2025/TT-BTC for Vietnamese accounting standards.
"""

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Any

from repositories.tax_repository import TaxRepository


class TaxType(Enum):
    VAT = "vat"
    CIT = "cit"
    PIT = "pit"
    PILLAR2 = "pillar2"


class VATRateType(Enum):
    ZERO = "0"
    FIVE = "5"
    EIGHT = "8"
    TEN = "10"


@dataclass
class ValidationResult:
    success: bool
    message: str = ""
    code: str = ""
    
    @classmethod
    def ok(cls, message: str = "", code: str = ""):
        return cls(success=True, message=message, code=code)
    
    @classmethod
    def error(cls, message: str, code: str = ""):
        return cls(success=False, message=message, code=code)


@dataclass
class VATCalculation:
    """VAT calculation result."""
    base_amount: Decimal
    vat_rate: Decimal
    vat_amount: Decimal
    total_amount: Decimal
    rate_type: str


@dataclass
class CITCalculation:
    """CIT calculation result."""
    revenue: Decimal
    expenses: Decimal
    gross_profit: Decimal
    cit_rate: Decimal
    estimated_tax: Decimal
    paid_tax: Decimal
    outstanding_tax: Decimal


class TaxEngine:
    """
    Centralized Tax validation and calculation engine.
    Single source of truth for tax-related business rules.
    
    Usage:
        engine = TaxEngine()
        
        # VAT Calculation
        result = engine.calculate_vat_inclusive(1_100_000, "10")
        
        # CIT Calculation
        result = engine.estimate_cit(year=2026, revenue=100_000_000, expenses=60_000_000)
        
        # VAT Rate Validation
        result = engine.validate_vat_rate("10")
    """
    
    VAT_RATES = {
        "0": Decimal("0"),
        "5": Decimal("0.05"),
        "8": Decimal("0.08"),
        "10": Decimal("0.10"),
    }
    
    DEFAULT_CIT_RATE = Decimal("0.20")
    PILLAR2_RATE = Decimal("0.15")
    
    VAT_ACCOUNT_CODES = {
        "input": ["1331", "1332"],
        "output": ["3331", "33311", "33312"],
    }
    
    @classmethod
    def calculate_vat_inclusive(cls, total_amount: Decimal, rate_str: str = "10") -> VATCalculation:
        """
        Calculate VAT from amount that already includes VAT.
        
        Args:
            total_amount: Total amount including VAT
            rate_str: VAT rate as string (0, 5, 8, 10)
            
        Returns:
            VATCalculation with base_amount, vat_amount, total_amount
        """
        vat_rate = cls.VAT_RATES.get(rate_str, Decimal("0.10"))
        divisor = Decimal("1") + vat_rate
        base_amount = total_amount / divisor
        vat_amount = total_amount - base_amount
        
        return VATCalculation(
            base_amount=base_amount.quantize(Decimal("0.01")),
            vat_rate=vat_rate,
            vat_amount=vat_amount.quantize(Decimal("0.01")),
            total_amount=total_amount.quantize(Decimal("0.01")),
            rate_type=rate_str,
        )
    
    @classmethod
    def calculate_vat_exclusive(cls, base_amount: Decimal, rate_str: str = "10") -> VATCalculation:
        """
        Calculate VAT from base amount (excluding VAT).
        
        Args:
            base_amount: Base amount before VAT
            rate_str: VAT rate as string (0, 5, 8, 10)
            
        Returns:
            VATCalculation with base_amount, vat_amount, total_amount
        """
        vat_rate = cls.VAT_RATES.get(rate_str, Decimal("0.10"))
        vat_amount = base_amount * vat_rate
        total_amount = base_amount + vat_amount
        
        return VATCalculation(
            base_amount=base_amount.quantize(Decimal("0.01")),
            vat_rate=vat_rate,
            vat_amount=vat_amount.quantize(Decimal("0.01")),
            total_amount=total_amount.quantize(Decimal("0.01")),
            rate_type=rate_str,
        )
    
    @classmethod
    def validate_vat_rate(cls, rate_str: str) -> ValidationResult:
        """
        Validate VAT rate.
        
        Args:
            rate_str: VAT rate as string
            
        Returns:
            ValidationResult indicating if rate is valid
        """
        if rate_str not in cls.VAT_RATES:
            return ValidationResult.error(
                f"Thuế suất VAT '{rate_str}' không hợp lệ. Các thuế suất hợp lệ: 0%, 5%, 8%, 10%",
                code="VAT_RATE_INVALID"
            )
        return ValidationResult.ok(f"Thuế suất {rate_str}% hợp lệ", code=rate_str)
    
    @classmethod
    def estimate_cit(
        cls,
        year: int,
        revenue: Decimal,
        expenses: Decimal,
        cit_rate: Optional[Decimal] = None
    ) -> CITCalculation:
        """
        Estimate CIT based on revenue and expenses.
        
        Args:
            year: Tax year
            revenue: Total revenue
            expenses: Total deductible expenses
            cit_rate: CIT rate (optional, uses default 20% if not provided)
            
        Returns:
            CITCalculation with profit and tax breakdown
        """
        if cit_rate is None:
            policy = TaxRepository.get_or_create_cit_policy(year)
            cit_rate = Decimal(str(policy.rate))
        
        gross_profit = revenue - expenses
        estimated_tax = max(Decimal("0"), gross_profit * cit_rate)
        paid_tax = TaxRepository.get_cit_amount(
            date(year, 1, 1),
            date(year, 12, 31)
        )
        outstanding_tax = estimated_tax - paid_tax
        
        return CITCalculation(
            revenue=revenue,
            expenses=expenses,
            gross_profit=gross_profit,
            cit_rate=cit_rate,
            estimated_tax=estimated_tax,
            paid_tax=paid_tax,
            outstanding_tax=outstanding_tax,
        )
    
    @classmethod
    def validate_cit_rate(cls, rate: Decimal) -> ValidationResult:
        """
        Validate CIT rate is within acceptable range.
        
        Args:
            rate: CIT rate as decimal (e.g., 0.20 for 20%)
            
        Returns:
            ValidationResult
        """
        if rate < Decimal("0") or rate > Decimal("1"):
            return ValidationResult.error(
                f"Thuế suất TNDN {rate * 100}% không hợp lệ. Phải nằm trong khoảng 0-100%",
                code="CIT_RATE_INVALID"
            )
        
        if rate > Decimal("0.25"):
            return ValidationResult.warning(
                f"Thuế suất TNDN {rate * 100}% cao bất thường. Kiểm tra lại.",
                code="CIT_RATE_HIGH"
            )
        
        return ValidationResult.ok(f"Thuế suất {rate * 100}% hợp lệ", code="CIT_RATE_VALID")
    
    @classmethod
    def get_vat_accounts(cls, vat_type: str = "input") -> List[str]:
        """Get VAT account codes by type."""
        return cls.VAT_ACCOUNT_CODES.get(vat_type, [])
    
    @classmethod
    def validate_vat_declaration(
        cls,
        year: int,
        month: int
    ) -> ValidationResult:
        """
        Validate VAT declaration data.
        
        Args:
            year: Year of declaration
            month: Month of declaration
            
        Returns:
            ValidationResult with validation status
        """
        if month < 1 or month > 12:
            return ValidationResult.error(
                f"Tháng '{month}' không hợp lệ. Tháng phải từ 1-12",
                code="VAT_MONTH_INVALID"
            )
        
        if year < 2000 or year > 2100:
            return ValidationResult.error(
                f"Năm '{year}' không hợp lệ",
                code="VAT_YEAR_INVALID"
            )
        
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year, 12, 31)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)
        
        vat_input = TaxRepository.get_vat_input_total(start_date, end_date)
        vat_output = TaxRepository.get_vat_output_total(start_date, end_date)
        
        if vat_input < Decimal("0"):
            return ValidationResult.warning(
                f"VAT đầu vào ({vat_input}) bị âm. Kiểm tra lại dữ liệu.",
                code="VAT_INPUT_NEGATIVE"
            )
        
        if vat_output < Decimal("0"):
            return ValidationResult.warning(
                f"VAT đầu ra ({vat_output}) bị âm. Kiểm tra lại dữ liệu.",
                code="VAT_OUTPUT_NEGATIVE"
            )
        
        return ValidationResult.ok(
            f"Khai thuế GTGT {year}/{month:02d} hợp lệ. "
            f"VAT vào: {vat_input}, VAT ra: {vat_output}",
            code="VAT_DECLARATION_OK"
        )
    
    @classmethod
    def get_vat_summary(cls, year: int) -> Dict[str, Any]:
        """Get comprehensive VAT summary for a year."""
        monthly_data = TaxRepository.get_monthly_vat_summary(year)
        quarterly_data = TaxRepository.get_quarterly_vat_summary(year)
        
        total_vat_input = sum(m["vat_input"] for m in monthly_data)
        total_vat_output = sum(m["vat_output"] for m in monthly_data)
        total_vat_payable = sum(m["vat_payable"] for m in monthly_data)
        total_vat_refundable = sum(m["vat_refundable"] for m in monthly_data)
        
        return {
            "year": year,
            "monthly_data": monthly_data,
            "quarterly_data": quarterly_data,
            "totals": {
                "vat_input": total_vat_input,
                "vat_output": total_vat_output,
                "vat_payable": total_vat_payable,
                "vat_refundable": total_vat_refundable,
            }
        }


class ValidationResultWithWarning(ValidationResult):
    """Validation result that includes warnings."""
    
    @classmethod
    def warning(cls, message: str, code: str = ""):
        result = cls(success=True, message=message, code=code)
        result.is_warning = True
        return result


TaxEngine.validate_cit_rate = ValidationResultWithWarning.warning.__get__(
    TaxEngine.validate_cit_rate, ValidationResultWithWarning
)

from typing import Any
ValidationResultWithWarning.warning.__doc__ = "Return a warning result that still passes validation."
