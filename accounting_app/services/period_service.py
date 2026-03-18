"""
Period Service - Manage accounting periods.
"""

from datetime import datetime, date
from typing import List, Optional
from decimal import Decimal

from models.accounting_period import AccountingPeriod
from core.database import db


class PeriodService:
    """Service for managing accounting periods."""
    
    @staticmethod
    def get_all_periods() -> List[AccountingPeriod]:
        """Get all periods ordered by year and month."""
        return AccountingPeriod.query.order_by(
            AccountingPeriod.year.desc(),
            AccountingPeriod.month.desc()
        ).all()
    
    @staticmethod
    def get_periods_by_year(year: int) -> List[AccountingPeriod]:
        """Get all periods for a specific year."""
        return AccountingPeriod.query.filter(
            AccountingPeriod.year == year
        ).order_by(AccountingPeriod.month).all()
    
    @staticmethod
    def get_period(period_id: int) -> Optional[AccountingPeriod]:
        """Get period by ID."""
        return db.session.get(AccountingPeriod, period_id)
    
    @staticmethod
    def get_period_by_code(period_code: str) -> Optional[AccountingPeriod]:
        """Get period by code."""
        return AccountingPeriod.query.filter_by(period_code=period_code).first()
    
    @staticmethod
    def get_current_period() -> AccountingPeriod:
        """Get the current accounting period."""
        today = date.today()
        period = AccountingPeriod.query.filter(
            AccountingPeriod.year == today.year,
            AccountingPeriod.month == today.month
        ).first()
        
        if not period:
            period = AccountingPeriod(
                period_code=f"{today.year}{today.month:02d}",
                period_name=f"Tháng {today.month}",
                year=today.year,
                month=today.month,
                start_date=date(today.year, today.month, 1),
                end_date=PeriodService._get_end_of_month(today.year, today.month),
                is_open=True,
            )
            db.session.add(period)
            db.session.commit()
        
        return period
    
    @staticmethod
    def get_open_periods() -> List[AccountingPeriod]:
        """Get all open periods."""
        return AccountingPeriod.query.filter(
            AccountingPeriod.is_open == True
        ).order_by(AccountingPeriod.year.desc(), AccountingPeriod.month.desc()).all()
    
    @staticmethod
    def is_period_open(period_id: int) -> bool:
        """Check if a period is open for transactions."""
        period = db.session.get(AccountingPeriod, period_id)
        return period and period.is_open and not period.is_closed
    
    @staticmethod
    def can_post_to_period(voucher_date: date) -> bool:
        """Check if a voucher can be posted to a period based on date."""
        period = AccountingPeriod.query.filter(
            AccountingPeriod.start_date <= voucher_date,
            AccountingPeriod.end_date >= voucher_date
        ).first()
        
        if not period:
            period = AccountingPeriod(
                period_code=f"{voucher_date.year}{voucher_date.month:02d}",
                period_name=f"Tháng {voucher_date.month}",
                year=voucher_date.year,
                month=voucher_date.month,
                start_date=date(voucher_date.year, voucher_date.month, 1),
                end_date=PeriodService._get_end_of_month(voucher_date.year, voucher_date.month),
                is_open=True,
            )
            db.session.add(period)
            db.session.commit()
            return True
        
        return period.is_open and not period.is_closed
    
    @staticmethod
    def open_period(period_id: int, user_id: int) -> AccountingPeriod:
        """Open a period for transactions."""
        period = db.session.get(AccountingPeriod, period_id)
        if not period:
            raise ValueError("Kỳ kế toán không tồn tại")
        
        if period.is_closed:
            raise ValueError("Không thể mở kỳ đã đóng")
        
        period.is_open = True
        db.session.commit()
        
        return period
    
    @staticmethod
    def close_period(period_id: int, user_id: int) -> AccountingPeriod:
        """Close a period - prevents new transactions."""
        period = db.session.get(AccountingPeriod, period_id)
        if not period:
            raise ValueError("Kỳ kế toán không tồn tại")
        
        if period.is_closed:
            raise ValueError("Kỳ kế toán đã đóng")
        
        period.is_closed = True
        period.is_open = False
        period.closed_at = datetime.utcnow()
        period.closed_by = user_id
        db.session.commit()
        
        return period
    
    @staticmethod
    def lock_period(period_id: int, user_id: int) -> AccountingPeriod:
        """Lock a period - prevents any modifications."""
        period = db.session.get(AccountingPeriod, period_id)
        if not period:
            raise ValueError("Kỳ kế toán không tồn tại")
        
        period.is_open = False
        db.session.commit()
        
        return period
    
    @staticmethod
    def create_year_periods(year: int, user_id: int) -> List[AccountingPeriod]:
        """Create all 12 periods for a year."""
        existing = AccountingPeriod.query.filter_by(year=year).first()
        if existing:
            raise ValueError(f"Các kỳ kế toán cho năm {year} đã tồn tại")
        
        periods = []
        month_names = {
            1: "Tháng 1", 2: "Tháng 2", 3: "Tháng 3",
            4: "Tháng 4", 5: "Tháng 5", 6: "Tháng 6",
            7: "Tháng 7", 8: "Tháng 8", 9: "Tháng 9",
            10: "Tháng 10", 11: "Tháng 11", 12: "Tháng 12",
        }
        
        for month in range(1, 13):
            period = AccountingPeriod(
                period_code=f"{year}{month:02d}",
                period_name=month_names[month],
                year=year,
                month=month,
                start_date=date(year, month, 1),
                end_date=PeriodService._get_end_of_month(year, month),
                is_open=True,
            )
            periods.append(period)
        
        db.session.add_all(periods)
        db.session.commit()
        
        return periods
    
    @staticmethod
    def get_year_summary(year: int) -> dict:
        """Get summary of a year's periods."""
        periods = AccountingPeriod.query.filter(
            AccountingPeriod.year == year
        ).all()
        
        return {
            "year": year,
            "total_periods": len(periods),
            "open_periods": sum(1 for p in periods if p.is_open),
            "closed_periods": sum(1 for p in periods if p.is_closed),
            "locked_periods": sum(1 for p in periods if not p.is_open and not p.is_closed),
        }
    
    @staticmethod
    def _get_end_of_month(year: int, month: int) -> date:
        """Get the last day of a month."""
        if month == 12:
            return date(year, 12, 31)
        else:
            from datetime import timedelta
            return date(year, month + 1, 1) - timedelta(days=1)
