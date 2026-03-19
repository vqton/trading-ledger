from datetime import date
from decimal import Decimal
from typing import List, Optional, Tuple

from repositories.tax_payment_repository import TaxPaymentRepository
from models.tax_payment import TaxPayment
from core.logging import log_audit


class TaxPaymentService:
    """Service for TaxPayment business logic."""

    @staticmethod
    def get_tax_payments(
        page: int = 1,
        per_page: int = 20,
        tax_type: Optional[str] = None,
        payment_status: Optional[str] = None,
        period_year: Optional[int] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[TaxPayment], int]:
        """Get paginated tax payments."""
        return TaxPaymentRepository.get_all(page, per_page, tax_type, payment_status, period_year, search)

    @staticmethod
    def get_tax_payment(tax_payment_id: int) -> Optional[TaxPayment]:
        """Get tax payment by ID."""
        return TaxPaymentRepository.get_by_id(tax_payment_id)

    @staticmethod
    def get_tax_payment_by_no(payment_no: str) -> Optional[TaxPayment]:
        """Get tax payment by payment number."""
        return TaxPaymentRepository.get_by_payment_no(payment_no)

    @staticmethod
    def create_tax_payment(
        tax_type: str,
        period_year: int,
        created_by: int,
        payment_no: Optional[str] = None,
        declaration_no: Optional[str] = None,
        declaration_date: Optional[date] = None,
        period_month: Optional[int] = None,
        period_quarter: Optional[int] = None,
        taxable_amount: Decimal = Decimal("0.00"),
        tax_rate: Decimal = Decimal("0.00"),
        tax_amount: Decimal = Decimal("0.00"),
        interest_amount: Decimal = Decimal("0.00"),
        penalty_amount: Decimal = Decimal("0.00"),
        payment_date: Optional[date] = None,
        due_date: Optional[date] = None,
        payment_status: str = "pending",
        payment_method: Optional[str] = None,
        bank_payment_date: Optional[date] = None,
        bank_transaction_no: Optional[str] = None,
        tax_authority: Optional[str] = None,
        tax_office_code: Optional[str] = None,
        notes: Optional[str] = None,
        voucher_id: Optional[int] = None,
    ) -> Tuple[Optional[TaxPayment], Optional[str]]:
        """Create a new tax payment with validation."""
        if payment_no is None:
            payment_no = TaxPayment.generate_payment_no(tax_type)
        else:
            if TaxPaymentRepository.get_by_payment_no(payment_no):
                return None, f"Số nộp thuế '{payment_no}' đã tồn tại"

        valid_tax_types = [choice[0] for choice in TaxPayment.TaxType.CHOICES]
        if tax_type not in valid_tax_types:
            return None, f"Loại thuế '{tax_type}' không hợp lệ"

        if taxable_amount < 0:
            return None, "Số tiền chịu thuế không được âm"

        if tax_rate < 0:
            return None, "Thuế suất không được âm"

        if tax_amount < 0:
            return None, "Số tiền thuế không được âm"

        if interest_amount < 0:
            return None, "Tiền lãi không được âm"

        if penalty_amount < 0:
            return None, "Tiền phạt không được âm"

        if period_month and (period_month < 1 or period_month > 12):
            return None, "Tháng kỳ tính thuế phải từ 1 đến 12"

        if period_quarter and (period_quarter < 1 or period_quarter > 4):
            return None, "Quý kỳ tính thuế phải từ 1 đến 4"

        if payment_date and due_date and payment_date > due_date:
            return None, "Ngày nộp thuế không thể sau ngày đến hạn"

        tax_payment = TaxPaymentRepository.create(
            payment_no=payment_no,
            tax_type=tax_type,
            declaration_no=declaration_no,
            declaration_date=declaration_date,
            period_year=period_year,
            period_month=period_month,
            period_quarter=period_quarter,
            taxable_amount=taxable_amount,
            tax_rate=tax_rate,
            tax_amount=tax_amount,
            interest_amount=interest_amount,
            penalty_amount=penalty_amount,
            payment_date=payment_date,
            due_date=due_date,
            payment_status=payment_status,
            payment_method=payment_method,
            bank_payment_date=bank_payment_date,
            bank_transaction_no=bank_transaction_no,
            tax_authority=tax_authority,
            tax_office_code=tax_office_code,
            notes=notes,
            voucher_id=voucher_id,
            created_by=created_by,
        )

        log_audit(
            user_id=created_by,
            action="create",
            entity="tax_payment",
            entity_id=tax_payment.id,
            new_value=tax_payment.to_dict(),
        )

        return tax_payment, None

    @staticmethod
    def update_tax_payment(
        tax_payment_id: int,
        declaration_no: Optional[str] = None,
        declaration_date: Optional[date] = None,
        period_month: Optional[int] = None,
        period_quarter: Optional[int] = None,
        taxable_amount: Optional[Decimal] = None,
        tax_rate: Optional[Decimal] = None,
        tax_amount: Optional[Decimal] = None,
        interest_amount: Optional[Decimal] = None,
        penalty_amount: Optional[Decimal] = None,
        payment_date: Optional[date] = None,
        due_date: Optional[date] = None,
        payment_status: Optional[str] = None,
        payment_method: Optional[str] = None,
        bank_payment_date: Optional[date] = None,
        bank_transaction_no: Optional[str] = None,
        tax_authority: Optional[str] = None,
        tax_office_code: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Tuple[Optional[TaxPayment], Optional[str]]:
        """Update tax payment with validation."""
        old_payment = TaxPaymentRepository.get_by_id(tax_payment_id)
        if not old_payment:
            return None, "Nộp thuế không tồn tại"

        if taxable_amount is not None and taxable_amount < 0:
            return None, "Số tiền chịu thuế không được âm"

        if tax_rate is not None and tax_rate < 0:
            return None, "Thuế suất không được âm"

        if tax_amount is not None and tax_amount < 0:
            return None, "Số tiền thuế không được âm"

        if interest_amount is not None and interest_amount < 0:
            return None, "Tiền lãi không được âm"

        if penalty_amount is not None and penalty_amount < 0:
            return None, "Tiền phạt không được âm"

        if period_month is not None and (period_month < 1 or period_month > 12):
            return None, "Tháng kỳ tính thuế phải từ 1 đến 12"

        if period_quarter is not None and (period_quarter < 1 or period_quarter > 4):
            return None, "Quý kỳ tính thuế phải từ 1 đến 4"

        if payment_status == "paid" and old_payment.payment_status != "paid":
            if payment_date is None and due_date is None:
                return None, "Cần cung cấp ngày nộp thuế khi đánh dấu đã nộp"

        tax_payment = TaxPaymentRepository.update(
            tax_payment_id=tax_payment_id,
            declaration_no=declaration_no,
            declaration_date=declaration_date,
            period_month=period_month,
            period_quarter=period_quarter,
            taxable_amount=taxable_amount,
            tax_rate=tax_rate,
            tax_amount=tax_amount,
            interest_amount=interest_amount,
            penalty_amount=penalty_amount,
            payment_date=payment_date,
            due_date=due_date,
            payment_status=payment_status,
            payment_method=payment_method,
            bank_payment_date=bank_payment_date,
            bank_transaction_no=bank_transaction_no,
            tax_authority=tax_authority,
            tax_office_code=tax_office_code,
            notes=notes,
        )

        log_audit(
            user_id=old_payment.created_by,
            action="update",
            entity="tax_payment",
            entity_id=tax_payment.id,
            old_value=old_payment.to_dict(),
            new_value=tax_payment.to_dict(),
        )

        return tax_payment, None

    @staticmethod
    def delete_tax_payment(tax_payment_id: int, user_id: int) -> Tuple[bool, Optional[str]]:
        """Delete tax payment."""
        tax_payment = TaxPaymentRepository.get_by_id(tax_payment_id)
        if not tax_payment:
            return False, "Nộp thuế không tồn tại"

        success = TaxPaymentRepository.delete(tax_payment_id)
        if success:
            log_audit(
                user_id=user_id,
                action="delete",
                entity="tax_payment",
                entity_id=tax_payment_id,
                old_value=tax_payment.to_dict(),
            )
        return success, None

    @staticmethod
    def mark_as_paid(
        tax_payment_id: int,
        payment_date: date,
        payment_method: str,
        bank_transaction_no: Optional[str] = None,
    ) -> Tuple[Optional[TaxPayment], Optional[str]]:
        """Mark tax payment as paid."""
        tax_payment = TaxPaymentRepository.get_by_id(tax_payment_id)
        if not tax_payment:
            return None, "Nộp thuế không tồn tại"

        if tax_payment.payment_status == "paid":
            return None, "Nộp thuế đã được đánh dấu là đã nộp"

        updated = TaxPaymentRepository.mark_as_paid(
            tax_payment_id=tax_payment_id,
            payment_date=payment_date,
            payment_method=payment_method,
            bank_transaction_no=bank_transaction_no,
        )

        log_audit(
            user_id=tax_payment.created_by,
            action="mark_paid",
            entity="tax_payment",
            entity_id=tax_payment_id,
            new_value=updated.to_dict(),
        )

        return updated, None

    @staticmethod
    def get_pending_payments(year: Optional[int] = None) -> List[TaxPayment]:
        """Get pending tax payments."""
        return TaxPaymentRepository.get_pending(year)

    @staticmethod
    def get_overdue_payments() -> List[TaxPayment]:
        """Get overdue tax payments."""
        return TaxPaymentRepository.get_overdue()

    @staticmethod
    def get_tax_summary(year: int) -> Tuple[dict, int]:
        """Get tax payment summary for a year."""
        return TaxPaymentRepository.get_summary(year)

    @staticmethod
    def get_tax_payments_by_voucher(voucher_id: int) -> List[TaxPayment]:
        """Get tax payments linked to a voucher."""
        return TaxPayment.query.filter_by(voucher_id=voucher_id).all()
