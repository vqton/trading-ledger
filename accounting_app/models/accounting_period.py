"""
Accounting Period Model - For managing fiscal periods.
"""

from datetime import datetime, date
from core.database import db
from typing import Optional


class AccountingPeriod(db.Model):
    """Accounting period model for managing fiscal years and periods."""
    
    __tablename__ = "accounting_periods"
    
    id = db.Column(db.Integer, primary_key=True)
    period_code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    period_name = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False, index=True)
    month = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    is_open = db.Column(db.Boolean, default=True, nullable=False)
    is_closed = db.Column(db.Boolean, default=False, nullable=False)
    closed_at = db.Column(db.DateTime, nullable=True)
    closed_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.Index("ix_periods_year_month", "year", "month"),
    )
    
    def __repr__(self) -> str:
        return f"<Period {self.period_code}>"
    
    @property
    def is_current(self) -> bool:
        """Check if this is the current period."""
        today = date.today()
        return self.start_date <= today <= self.end_date
    
    @property
    def status(self) -> str:
        """Get period status."""
        if self.is_closed:
            return "closed"
        elif self.is_open:
            return "open"
        else:
            return "locked"


def create_periods_for_year(year: int) -> list:
    """Create 12 periods for a fiscal year."""
    periods = []
    period_names = {
        1: "Tháng 1", 2: "Tháng 2", 3: "Tháng 3",
        4: "Tháng 4", 5: "Tháng 5", 6: "Tháng 6",
        7: "Tháng 7", 8: "Tháng 8", 9: "Tháng 9",
        10: "Tháng 10", 11: "Tháng 11", 12: "Tháng 12",
    }
    
    for month in range(1, 13):
        start_day = 1
        if month == 12:
            end_day = 31
        else:
            end_day = (date(year, month + 1, 1) - datetime.timedelta(days=1)).day
        
        period = AccountingPeriod(
            period_code=f"{year}{month:02d}",
            period_name=period_names[month],
            year=year,
            month=month,
            start_date=date(year, month, start_day),
            end_date=date(year, month, end_day),
            is_open=True,
        )
        periods.append(period)
    
    return periods


def get_or_create_current_period() -> AccountingPeriod:
    """Get or create the current accounting period."""
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
            end_date=date(today.year, today.month, 28),
            is_open=True,
        )
        
        if today.month == 12:
            end_date = date(today.year, 12, 31)
        else:
            from datetime import timedelta
            end_date = date(today.year, today.month + 1, 1) - timedelta(days=1)
        
        period.end_date = end_date
        
        from core.database import db
        db.session.add(period)
        db.session.commit()
    
    return period
