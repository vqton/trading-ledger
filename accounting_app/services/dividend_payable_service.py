"""
Dividend Payable Service - Business logic for TK 332 dividend payments.
Circular 99/2025/TT-BTC compliant dividend management.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any, Tuple

from core.database import db
from core.utils import utc_now


class DividendPayableService:
    """Service for managing dividend payables (TK 332)."""

    WHT_RATE = Decimal("0.05")

    @staticmethod
    def create_dividend(
        shareholder_name: str,
        shareholder_type: str,
        share_quantity: Decimal,
        dividend_per_share: Decimal,
        declaration_date: date,
        due_date: date = None,
        notes: str = None,
        created_by: int = None,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Create a new dividend obligation.

        Args:
            shareholder_name: Shareholder name
            shareholder_type: Type (individual/corporate/foreign)
            share_quantity: Number of shares
            dividend_per_share: Dividend per share
            declaration_date: Declaration date
            due_date: Payment due date
            notes: Notes
            created_by: Creator user ID

        Returns:
            Tuple of (success, result)
        """
        try:
            from models.dividend_payable import DividendPayable

            if isinstance(declaration_date, str):
                declaration_date = datetime.strptime(declaration_date, "%Y-%m-%d").date()
            if isinstance(due_date, str):
                due_date = datetime.strptime(due_date, "%Y-%m-%d").date()

            total_gross = share_quantity * dividend_per_share
            withholding_tax = total_gross * DividendPayableService.WHT_RATE
            net_amount = total_gross - withholding_tax

            voucher_no = DividendPayable.generate_voucher_no()
            fiscal_year = declaration_date.year if isinstance(declaration_date, date) else datetime.now().year

            dividend = DividendPayable(
                voucher_no=voucher_no,
                shareholder_name=shareholder_name,
                shareholder_type=shareholder_type,
                shares_owned=share_quantity,
                dividend_per_share=dividend_per_share,
                gross_amount=total_gross,
                withholding_tax_rate=DividendPayableService.WHT_RATE,
                withholding_tax_amount=withholding_tax,
                net_amount=net_amount,
                declaration_date=declaration_date,
                payment_date=None,
                fiscal_year=fiscal_year,
                notes=notes,
                created_by=created_by or 1,
            )
            db.session.add(dividend)
            db.session.commit()
            return True, dividend.to_dict()
        except Exception as e:
            db.session.rollback()
            return False, {"error": str(e)}

    @staticmethod
    def update_dividend(
        dividend_id: int,
        **kwargs,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Update dividend.

        Args:
            dividend_id: Dividend ID
            **kwargs: Fields to update

        Returns:
            Tuple of (success, result)
        """
        try:
            from models.dividend_payable import DividendPayable

            dividend = db.session.get(DividendPayable, dividend_id)
            if not dividend:
                return False, {"error": "Dividend not found"}

            if dividend.status == "paid":
                return False, {"error": "Cannot update paid dividend"}

            for key, value in kwargs.items():
                if hasattr(dividend, key) and key not in ["id", "payment_no", "created_at"]:
                    setattr(dividend, key, value)

            dividend.updated_at = utc_now()
            db.session.commit()
            return True, dividend.to_dict()
        except Exception as e:
            db.session.rollback()
            return False, {"error": str(e)}

    @staticmethod
    def record_payment(
        dividend_id: int,
        payment_date: date,
        payment_method: str,
        bank_account: str = None,
        notes: str = None,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Record dividend payment.

        Args:
            dividend_id: Dividend ID
            payment_date: Payment date
            payment_method: Payment method
            bank_account: Bank account used
            notes: Payment notes

        Returns:
            Tuple of (success, result)
        """
        try:
            from models.dividend_payable import DividendPayable

            dividend = db.session.get(DividendPayable, dividend_id)
            if not dividend:
                return False, {"error": "Dividend not found"}

            if dividend.status == "paid":
                return False, {"error": "Dividend already paid"}

            dividend.payment_date = payment_date
            dividend.payment_method = payment_method
            dividend.bank_account = bank_account
            dividend.status = "paid"
            dividend.notes = notes

            db.session.commit()
            return True, dividend.to_dict()
        except Exception as e:
            db.session.rollback()
            return False, {"error": str(e)}

    @staticmethod
    def cancel_dividend(
        dividend_id: int,
        reason: str = None,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Cancel dividend obligation.

        Args:
            dividend_id: Dividend ID
            reason: Cancellation reason

        Returns:
            Tuple of (success, result)
        """
        try:
            from models.dividend_payable import DividendPayable

            dividend = db.session.get(DividendPayable, dividend_id)
            if not dividend:
                return False, {"error": "Dividend not found"}

            if dividend.status == "paid":
                return False, {"error": "Cannot cancel paid dividend"}

            dividend.status = "cancelled"
            dividend.notes = f"{dividend.notes}\nCancellation: {reason}" if reason else dividend.notes

            db.session.commit()
            return True, dividend.to_dict()
        except Exception as e:
            db.session.rollback()
            return False, {"error": str(e)}

    @staticmethod
    def get_dividends(
        status: str = None,
        shareholder_type: str = None,
        start_date: date = None,
        end_date: date = None,
        fiscal_year: int = None,
    ) -> List[Dict[str, Any]]:
        """
        Get dividends with filters.

        Args:
            status: Filter by status
            shareholder_type: Filter by shareholder type
            start_date: Filter start date
            end_date: Filter end date
            fiscal_year: Filter by fiscal year

        Returns:
            List of dividends
        """
        from models.dividend_payable import DividendPayable

        query = DividendPayable.query

        if status:
            query = query.filter(DividendPayable.payment_status == status)
        if shareholder_type:
            query = query.filter_by(shareholder_type=shareholder_type)
        if start_date:
            query = query.filter(DividendPayable.declaration_date >= start_date)
        if end_date:
            query = query.filter(DividendPayable.declaration_date <= end_date)
        if fiscal_year:
            query = query.filter(DividendPayable.declaration_date.between(
                date(fiscal_year, 1, 1),
                date(fiscal_year, 12, 31)
            ))

        dividends = query.order_by(DividendPayable.declaration_date.desc()).all()
        return [d.to_dict() for d in dividends]

    @staticmethod
    def get_dividend_by_id(dividend_id: int) -> Optional[Dict[str, Any]]:
        """Get dividend by ID."""
        from models.dividend_payable import DividendPayable

        dividend = db.session.get(DividendPayable, dividend_id)
        return dividend.to_dict() if dividend else None

    @staticmethod
    def get_outstanding_dividends() -> Dict[str, Any]:
        """
        Get outstanding dividend totals.

        Returns:
            Dictionary with totals
        """
        from models.dividend_payable import DividendPayable

        pending = DividendPayable.query.filter_by(status="pending").all()
        overdue = DividendPayable.query.filter_by(status="overdue").all()

        pending_total = sum(d.net_amount or Decimal("0") for d in pending)
        overdue_total = sum(d.net_amount or Decimal("0") for d in overdue)

        return {
            "pending_count": len(pending),
            "pending_amount": pending_total,
            "overdue_count": len(overdue),
            "overdue_amount": overdue_total,
            "total_outstanding": pending_total + overdue_total,
        }

    @staticmethod
    def get_dividend_summary(fiscal_year: int) -> Dict[str, Any]:
        """
        Get dividend summary for fiscal year.

        Args:
            fiscal_year: Fiscal year

        Returns:
            Dictionary with summary
        """
        from models.dividend_payable import DividendPayable

        dividends = DividendPayable.query.filter(
            DividendPayable.declaration_date.between(
                date(fiscal_year, 1, 1),
                date(fiscal_year, 12, 31)
            )
        ).all()

        total_gross = sum(d.gross_amount or Decimal("0") for d in dividends)
        total_wht = sum(d.withholding_tax_amount or Decimal("0") for d in dividends)
        total_net = sum(d.net_amount or Decimal("0") for d in dividends)
        paid_amount = sum(d.net_amount or Decimal("0") for d in dividends if d.payment_status == "paid")
        outstanding = total_net - paid_amount

        by_type = {}
        for sh_type in ["individual", "corporate", "foreign"]:
            type_divs = [d for d in dividends if d.shareholder_type == sh_type]
            by_type[sh_type] = {
                "count": len(type_divs),
                "total_gross": sum(d.gross_amount or Decimal("0") for d in type_divs),
                "total_wht": sum(d.withholding_tax_amount or Decimal("0") for d in type_divs),
            }

        return {
            "fiscal_year": fiscal_year,
            "total_dividends": len(dividends),
            "total_gross_amount": total_gross,
            "total_withholding_tax": total_wht,
            "total_net_amount": total_net,
            "paid_amount": paid_amount,
            "outstanding_amount": outstanding,
            "by_shareholder_type": by_type,
        }

    @staticmethod
    def check_overdue() -> int:
        """
        Mark overdue dividends.

        Returns:
            Number of dividends marked as overdue
        """
        from models.dividend_payable import DividendPayable

        today = date.today()
        overdue = DividendPayable.query.filter(
            DividendPayable.status == "pending",
            DividendPayable.due_date < today
        ).all()

        count = 0
        for dividend in overdue:
            dividend.status = "overdue"
            count += 1

        db.session.commit()
        return count
