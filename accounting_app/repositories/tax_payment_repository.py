from datetime import date
from decimal import Decimal
from typing import List, Optional, Tuple

from core.database import db
from models.tax_payment import TaxPayment


class TaxPaymentRepository:
    """Repository for TaxPayment CRUD operations."""

    @staticmethod
    def get_all(
        page: int = 1,
        per_page: int = 20,
        tax_type: Optional[str] = None,
        payment_status: Optional[str] = None,
        period_year: Optional[int] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[TaxPayment], int]:
        """Get paginated tax payments with filters."""
        query = TaxPayment.query

        if tax_type:
            query = query.filter(TaxPayment.tax_type == tax_type)

        if payment_status:
            query = query.filter(TaxPayment.payment_status == payment_status)

        if period_year:
            query = query.filter(TaxPayment.period_year == period_year)

        if search:
            query = query.filter(
                db.or_(
                    TaxPayment.payment_no.ilike(f"%{search}%"),
                    TaxPayment.declaration_no.ilike(f"%{search}%"),
                )
            )

        query = query.order_by(TaxPayment.due_date.desc().nullsfirst())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        return pagination.items, pagination.total

    @staticmethod
    def get_by_id(tax_payment_id: int) -> Optional[TaxPayment]:
        """Get tax payment by ID."""
        return db.session.get(TaxPayment, tax_payment_id)

    @staticmethod
    def get_by_payment_no(payment_no: str) -> Optional[TaxPayment]:
        """Get tax payment by payment number."""
        return TaxPayment.query.filter_by(payment_no=payment_no).first()

    @staticmethod
    def create(
        payment_no: str,
        tax_type: str,
        period_year: int,
        created_by: int,
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
    ) -> TaxPayment:
        """Create a new tax payment."""
        total_amount = tax_amount + interest_amount + penalty_amount

        tax_payment = TaxPayment(
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
            total_amount=total_amount,
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
        db.session.add(tax_payment)
        db.session.commit()
        return tax_payment

    @staticmethod
    def update(
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
    ) -> Optional[TaxPayment]:
        """Update tax payment."""
        tax_payment = db.session.get(TaxPayment, tax_payment_id)
        if not tax_payment:
            return None

        if declaration_no is not None:
            tax_payment.declaration_no = declaration_no
        if declaration_date is not None:
            tax_payment.declaration_date = declaration_date
        if period_month is not None:
            tax_payment.period_month = period_month
        if period_quarter is not None:
            tax_payment.period_quarter = period_quarter
        if taxable_amount is not None:
            tax_payment.taxable_amount = taxable_amount
        if tax_rate is not None:
            tax_payment.tax_rate = tax_rate
        if tax_amount is not None:
            tax_payment.tax_amount = tax_amount
        if interest_amount is not None:
            tax_payment.interest_amount = interest_amount
        if penalty_amount is not None:
            tax_payment.penalty_amount = penalty_amount
        if payment_date is not None:
            tax_payment.payment_date = payment_date
        if due_date is not None:
            tax_payment.due_date = due_date
        if payment_status is not None:
            tax_payment.payment_status = payment_status
        if payment_method is not None:
            tax_payment.payment_method = payment_method
        if bank_payment_date is not None:
            tax_payment.bank_payment_date = bank_payment_date
        if bank_transaction_no is not None:
            tax_payment.bank_transaction_no = bank_transaction_no
        if tax_authority is not None:
            tax_payment.tax_authority = tax_authority
        if tax_office_code is not None:
            tax_payment.tax_office_code = tax_office_code
        if notes is not None:
            tax_payment.notes = notes

        tax_payment.total_amount = (
            tax_payment.tax_amount + 
            tax_payment.interest_amount + 
            tax_payment.penalty_amount
        )
        db.session.commit()
        return tax_payment

    @staticmethod
    def delete(tax_payment_id: int) -> bool:
        """Delete tax payment."""
        tax_payment = db.session.get(TaxPayment, tax_payment_id)
        if not tax_payment:
            return False

        db.session.delete(tax_payment)
        db.session.commit()
        return True

    @staticmethod
    def mark_as_paid(
        tax_payment_id: int,
        payment_date: date,
        payment_method: str,
        bank_transaction_no: Optional[str] = None,
    ) -> Optional[TaxPayment]:
        """Mark tax payment as paid."""
        tax_payment = db.session.get(TaxPayment, tax_payment_id)
        if not tax_payment:
            return None

        tax_payment.payment_date = payment_date
        tax_payment.payment_status = "paid"
        tax_payment.payment_method = payment_method
        tax_payment.bank_transaction_no = bank_transaction_no
        if payment_method == "bank_transfer":
            tax_payment.bank_payment_date = payment_date
        db.session.commit()
        return tax_payment

    @staticmethod
    def get_pending(year: Optional[int] = None) -> List[TaxPayment]:
        """Get pending tax payments."""
        query = TaxPayment.query.filter(
            TaxPayment.payment_status.in_(["pending", "partial", "overdue"])
        )
        if year:
            query = query.filter(TaxPayment.period_year == year)
        return query.order_by(TaxPayment.due_date).all()

    @staticmethod
    def get_overdue() -> List[TaxPayment]:
        """Get overdue tax payments."""
        today = date.today()
        return TaxPayment.query.filter(
            TaxPayment.payment_status.in_(["pending", "partial"]),
            TaxPayment.due_date < today
        ).order_by(TaxPayment.due_date).all()

    @staticmethod
    def get_summary(year: int) -> dict:
        """Get tax payment summary for a year."""
        summary = {}
        for tax_type_choice, _ in TaxPayment.TaxType.CHOICES:
            paid = TaxPaymentRepository.get_total_by_type(tax_type_choice, year)
            outstanding = TaxPaymentRepository.get_outstanding_by_type(tax_type_choice, year)
            summary[tax_type_choice] = {
                "paid": paid,
                "outstanding": outstanding,
                "total": paid + outstanding,
            }

        overdue_count = len(TaxPaymentRepository.get_overdue())
        return summary, overdue_count
