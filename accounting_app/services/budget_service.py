"""Budget Service - Budget creation, tracking, variance analysis."""

from datetime import date
from decimal import Decimal
from typing import Dict, List, Optional

from core.database import db
from models.budget import Budget, BudgetActual, BudgetDetail, BudgetStatus
from models.journal import JournalEntry
from sqlalchemy import func


class BudgetService:
    """Service for budget operations."""

    @staticmethod
    def get_all_budgets() -> List[Budget]:
        """Get all budgets."""
        return Budget.query.order_by(Budget.fiscal_year.desc()).all()

    @staticmethod
    def get_budget(budget_id: int) -> Optional[Budget]:
        """Get budget by ID."""
        return db.session.get(Budget, budget_id)

    @staticmethod
    def get_budget_by_year(fiscal_year: int) -> Optional[Budget]:
        """Get budget by fiscal year."""
        return Budget.query.filter_by(fiscal_year=fiscal_year).first()

    @staticmethod
    def create_budget(budget_data: Dict, user_id: int) -> Budget:
        """Create new budget."""
        existing = Budget.query.filter_by(fiscal_year=budget_data["fiscal_year"]).first()
        if existing:
            raise ValueError(f"Ngân sách năm {budget_data['fiscal_year']} đã tồn tại")

        budget = Budget(
            code=f"BUDGET-{budget_data['fiscal_year']}",
            name=budget_data["name"],
            fiscal_year=budget_data["fiscal_year"],
            period_type=budget_data.get("period_type", "annual"),
            start_date=budget_data["start_date"],
            end_date=budget_data["end_date"],
            description=budget_data.get("description"),
            status=BudgetStatus.DRAFT,
            created_by=user_id,
        )
        db.session.add(budget)
        db.session.flush()
        return budget

    @staticmethod
    def add_budget_detail(budget_id: int, account_id: int, amount: Decimal) -> BudgetDetail:
        """Add budget detail for an account."""
        budget = db.session.get(Budget, budget_id)
        if not budget:
            raise ValueError("Budget not found")

        if budget.status != BudgetStatus.DRAFT:
            raise ValueError("Budget đã được duyệt, không thể thêm chi tiết")

        existing = BudgetDetail.query.filter_by(
            budget_id=budget_id,
            account_id=account_id,
        ).first()

        if existing:
            existing.budget_amount = amount
            db.session.commit()
            return existing

        detail = BudgetDetail(
            budget_id=budget_id,
            account_id=account_id,
            budget_amount=amount,
        )
        db.session.add(detail)
        db.session.commit()
        return detail

    @staticmethod
    def approve_budget(budget_id: int) -> Budget:
        """Approve a budget."""
        budget = db.session.get(Budget, budget_id)
        if not budget:
            raise ValueError("Budget not found")

        if budget.status != BudgetStatus.DRAFT:
            raise ValueError("Budget không ở trạng thái nháp")

        budget.status = BudgetStatus.APPROVED
        db.session.commit()
        return budget

    @staticmethod
    def close_budget(budget_id: int) -> Budget:
        """Close a budget."""
        budget = db.session.get(Budget, budget_id)
        if not budget:
            raise ValueError("Budget not found")

        if budget.status != BudgetStatus.APPROVED:
            raise ValueError("Budget phải được duyệt trước khi đóng")

        budget.status = BudgetStatus.CLOSED
        db.session.commit()
        return budget

    @staticmethod
    def get_actual_amounts(
        budget_id: int,
        start_date: date,
        end_date: date,
    ) -> Dict[int, Decimal]:
        """Get actual amounts for budget accounts."""
        budget = db.session.get(Budget, budget_id)
        if not budget:
            return {}

        details = BudgetDetail.query.filter_by(budget_id=budget_id).all()
        result = {}

        for detail in details:
            actual = db.session.query(
                func.coalesce(func.sum(JournalEntry.debit), Decimal("0"))
            ).filter(
                JournalEntry.account_id == detail.account_id,
                JournalEntry.voucher.has(
                    JournalEntry.voucher.has(
                        voucher_date__gte=start_date,
                        voucher_date__lte=end_date,
                        status="posted",
                    )
                ),
            ).scalar() or Decimal("0")

            result[detail.account_id] = actual

        return result

    @staticmethod
    def get_budget_variance(
        budget_id: int,
        period_year: int,
        period_month: int,
    ) -> List[Dict]:
        """Get budget variance report for a period."""
        from datetime import datetime
        
        budget = db.session.get(Budget, budget_id)
        if not budget:
            return []

        start_date = date(period_year, period_month, 1)
        if period_month == 12:
            end_date = date(period_year, 12, 31)
        else:
            end_date = date(period_year, period_month + 1, 1)

        actuals = BudgetService.get_actual_amounts(budget_id, start_date, end_date)

        details = BudgetDetail.query.filter_by(budget_id=budget_id).all()
        variance = []

        for detail in details:
            budget_amount = detail.budget_amount
            actual_amount = actuals.get(detail.account_id, Decimal("0"))
            variance_amount = budget_amount - actual_amount
            variance_pct = (variance_amount / budget_amount * 100) if budget_amount > 0 else Decimal("0")

            variance.append({
                "account_id": detail.account_id,
                "account_code": detail.account.code,
                "account_name": detail.account.name_vi,
                "budget_amount": budget_amount,
                "actual_amount": actual_amount,
                "variance_amount": variance_amount,
                "variance_pct": variance_pct,
            })

        return variance

    @staticmethod
    def get_budget_summary(budget_id: int) -> Dict:
        """Get budget summary."""
        budget = db.session.get(Budget, budget_id)
        if not budget:
            return {}

        total_budget = sum(d.budget_amount for d in budget.details)
        
        start_date = budget.start_date
        end_date = min(budget.end_date, date.today())
        actuals = BudgetService.get_actual_amounts(budget_id, start_date, end_date)
        
        total_actual = sum(actuals.values())
        total_variance = total_budget - total_actual

        return {
            "budget_id": budget.id,
            "fiscal_year": budget.fiscal_year,
            "status": budget.status,
            "total_budget": total_budget,
            "total_actual": total_actual,
            "total_variance": total_variance,
            "variance_pct": (total_variance / total_budget * 100) if total_budget > 0 else Decimal("0"),
        }

    @staticmethod
    def get_ytd_budget_report(
        fiscal_year: int,
        period_month: int,
    ) -> List[Dict]:
        """Get year-to-date budget report."""
        budget = Budget.query.filter_by(fiscal_year=fiscal_year).first()
        if not budget:
            return []

        start_date = date(fiscal_year, 1, 1)
        end_date = date(fiscal_year, period_month, 1)
        
        actuals = BudgetService.get_actual_amounts(budget.id, start_date, end_date)

        details = BudgetDetail.query.filter_by(budget_id=budget.id).all()
        report = []

        for detail in details:
            budget_ytd = detail.budget_amount / 12 * period_month
            actual_ytd = actuals.get(detail.account_id, Decimal("0"))
            variance = budget_ytd - actual_ytd

            report.append({
                "account_code": detail.account.code,
                "account_name": detail.account.name_vi,
                "annual_budget": detail.budget_amount,
                "budget_ytd": budget_ytd,
                "actual_ytd": actual_ytd,
                "variance": variance,
            })

        return report
