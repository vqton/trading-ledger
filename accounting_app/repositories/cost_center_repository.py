from datetime import date
from decimal import Decimal
from typing import List, Optional, Tuple

from core.database import db
from models.cost_center import CostCenter


class CostCenterRepository:
    """Repository for CostCenter CRUD operations."""

    @staticmethod
    def get_all(
        page: int = 1,
        per_page: int = 20,
        is_active: Optional[bool] = None,
        department: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[CostCenter], int]:
        """Get paginated cost centers with filters."""
        query = CostCenter.query

        if is_active is not None:
            query = query.filter(CostCenter.is_active == is_active)

        if department:
            query = query.filter(CostCenter.department == department)

        if search:
            query = query.filter(
                db.or_(
                    CostCenter.code.ilike(f"%{search}%"),
                    CostCenter.name.ilike(f"%{search}%"),
                )
            )

        query = query.order_by(CostCenter.code)
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        return pagination.items, pagination.total

    @staticmethod
    def get_by_id(cost_center_id: int) -> Optional[CostCenter]:
        """Get cost center by ID."""
        return db.session.get(CostCenter, cost_center_id)

    @staticmethod
    def get_by_code(code: str) -> Optional[CostCenter]:
        """Get cost center by code."""
        return CostCenter.query.filter_by(code=code).first()

    @staticmethod
    def create(
        code: str,
        name: str,
        created_by: int,
        description: Optional[str] = None,
        parent_id: Optional[int] = None,
        department: Optional[str] = None,
        budget_allocated: Decimal = Decimal("0.00"),
    ) -> CostCenter:
        """Create a new cost center."""
        cost_center = CostCenter(
            code=code,
            name=name,
            description=description,
            parent_id=parent_id,
            department=department,
            budget_allocated=budget_allocated,
            created_by=created_by,
        )
        db.session.add(cost_center)
        db.session.commit()
        return cost_center

    @staticmethod
    def update(
        cost_center_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        parent_id: Optional[int] = None,
        department: Optional[str] = None,
        budget_allocated: Optional[Decimal] = None,
        is_active: Optional[bool] = None,
    ) -> Optional[CostCenter]:
        """Update cost center."""
        cost_center = db.session.get(CostCenter, cost_center_id)
        if not cost_center:
            return None

        if name is not None:
            cost_center.name = name
        if description is not None:
            cost_center.description = description
        if parent_id is not None:
            cost_center.parent_id = parent_id
        if department is not None:
            cost_center.department = department
        if budget_allocated is not None:
            cost_center.budget_allocated = budget_allocated
        if is_active is not None:
            cost_center.is_active = is_active

        db.session.commit()
        return cost_center

    @staticmethod
    def delete(cost_center_id: int) -> bool:
        """Delete cost center (soft delete by setting inactive)."""
        cost_center = db.session.get(CostCenter, cost_center_id)
        if not cost_center:
            return False

        cost_center.is_active = False
        db.session.commit()
        return True

    @staticmethod
    def get_children(parent_id: int) -> List[CostCenter]:
        """Get child cost centers."""
        return CostCenter.query.filter_by(parent_id=parent_id).order_by(CostCenter.code).all()

    @staticmethod
    def get_active() -> List[CostCenter]:
        """Get all active cost centers."""
        return CostCenter.query.filter_by(is_active=True).order_by(CostCenter.code).all()

    @staticmethod
    def get_departments() -> List[str]:
        """Get unique departments."""
        result = db.session.query(CostCenter.department).filter(
            CostCenter.department.isnot(None),
            CostCenter.is_active == True
        ).distinct().order_by(CostCenter.department).all()
        return [r[0] for r in result]

    @staticmethod
    def get_budget_summary(start_date: Optional[date] = None, end_date: Optional[date] = None) -> dict:
        """Get budget summary for all cost centers."""
        cost_centers = CostCenter.query.filter_by(is_active=True).all()
        summary = []
        total_allocated = Decimal("0.00")
        total_used = Decimal("0.00")

        for cc in cost_centers:
            budget_used = cc.get_budget_used(start_date, end_date)
            budget_remaining = cc.get_budget_remaining()
            total_allocated += cc.budget_allocated
            total_used += budget_used

            summary.append({
                "id": cc.id,
                "code": cc.code,
                "name": cc.name,
                "department": cc.department,
                "budget_allocated": cc.budget_allocated,
                "budget_used": budget_used,
                "budget_remaining": budget_remaining,
                "utilization_rate": (
                    (budget_used / cc.budget_allocated * 100) if cc.budget_allocated > 0 else Decimal("0.00")
                ),
            })

        return {
            "items": summary,
            "total_allocated": total_allocated,
            "total_used": total_used,
            "total_remaining": total_allocated - total_used,
        }
