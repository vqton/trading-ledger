from datetime import date
from decimal import Decimal
from typing import List, Optional, Tuple

from repositories.cost_center_repository import CostCenterRepository
from models.cost_center import CostCenter
from core.logging import log_audit


class CostCenterService:
    """Service for CostCenter business logic."""

    @staticmethod
    def get_cost_centers(
        page: int = 1,
        per_page: int = 20,
        is_active: Optional[bool] = None,
        department: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[CostCenter], int]:
        """Get paginated cost centers."""
        return CostCenterRepository.get_all(page, per_page, is_active, department, search)

    @staticmethod
    def get_cost_center(cost_center_id: int) -> Optional[CostCenter]:
        """Get cost center by ID."""
        return CostCenterRepository.get_by_id(cost_center_id)

    @staticmethod
    def get_cost_center_by_code(code: str) -> Optional[CostCenter]:
        """Get cost center by code."""
        return CostCenterRepository.get_by_code(code)

    @staticmethod
    def create_cost_center(
        name: str,
        created_by: int,
        code: Optional[str] = None,
        description: Optional[str] = None,
        parent_id: Optional[int] = None,
        department: Optional[str] = None,
        budget_allocated: Decimal = Decimal("0.00"),
    ) -> Tuple[Optional[CostCenter], Optional[str]]:
        """Create a new cost center with validation."""
        if code is None:
            code = CostCenter.generate_code()
        else:
            if CostCenterRepository.get_by_code(code):
                return None, f"Mã trung tâm chi phí '{code}' đã tồn tại"

        if len(name) < 3:
            return None, "Tên trung tâm chi phí phải có ít nhất 3 ký tự"

        if parent_id:
            parent = CostCenterRepository.get_by_id(parent_id)
            if not parent:
                return None, "Trung tâm chi phí cha không tồn tại"
            if not parent.is_active:
                return None, "Trung tâm chi phí cha đã bị vô hiệu hóa"

        cost_center = CostCenterRepository.create(
            code=code,
            name=name,
            description=description,
            parent_id=parent_id,
            department=department,
            budget_allocated=budget_allocated,
            created_by=created_by,
        )

        log_audit(
            user_id=created_by,
            action="create",
            entity="cost_center",
            entity_id=cost_center.id,
            new_value=cost_center.to_dict(),
        )

        return cost_center, None

    @staticmethod
    def update_cost_center(
        cost_center_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        parent_id: Optional[int] = None,
        department: Optional[str] = None,
        budget_allocated: Optional[Decimal] = None,
        is_active: Optional[bool] = None,
    ) -> Tuple[Optional[CostCenter], Optional[str]]:
        """Update cost center with validation."""
        old_cost_center = CostCenterRepository.get_by_id(cost_center_id)
        if not old_cost_center:
            return None, "Trung tâm chi phí không tồn tại"

        if name is not None and len(name) < 3:
            return None, "Tên trung tâm chi phí phải có ít nhất 3 ký tự"

        if parent_id is not None:
            if parent_id == cost_center_id:
                return None, "Trung tâm chi phí không thể là cha của chính nó"
            parent = CostCenterRepository.get_by_id(parent_id)
            if not parent:
                return None, "Trung tâm chi phí cha không tồn tại"
            if not parent.is_active:
                return None, "Trung tâm chi phí cha đã bị vô hiệu hóa"

        cost_center = CostCenterRepository.update(
            cost_center_id=cost_center_id,
            name=name,
            description=description,
            parent_id=parent_id,
            department=department,
            budget_allocated=budget_allocated,
            is_active=is_active,
        )

        log_audit(
            user_id=old_cost_center.created_by,
            action="update",
            entity="cost_center",
            entity_id=cost_center.id,
            old_value=old_cost_center.to_dict(),
            new_value=cost_center.to_dict(),
        )

        return cost_center, None

    @staticmethod
    def delete_cost_center(cost_center_id: int, user_id: int) -> Tuple[bool, Optional[str]]:
        """Soft delete cost center."""
        cost_center = CostCenterRepository.get_by_id(cost_center_id)
        if not cost_center:
            return False, "Trung tâm chi phí không tồn tại"

        children = CostCenterRepository.get_children(cost_center_id)
        if children:
            return False, "Không thể xóa trung tâm chi phí có trung tâm con"

        success = CostCenterRepository.delete(cost_center_id)
        if success:
            log_audit(
                user_id=user_id,
                action="delete",
                entity="cost_center",
                entity_id=cost_center_id,
                old_value=cost_center.to_dict(),
            )
        return success, None

    @staticmethod
    def get_active_cost_centers() -> List[CostCenter]:
        """Get all active cost centers."""
        return CostCenterRepository.get_active()

    @staticmethod
    def get_departments() -> List[str]:
        """Get unique departments."""
        return CostCenterRepository.get_departments()

    @staticmethod
    def get_budget_report(start_date: Optional[date] = None, end_date: Optional[date] = None) -> dict:
        """Get budget utilization report."""
        return CostCenterRepository.get_budget_summary(start_date, end_date)

    @staticmethod
    def get_cost_center_tree() -> List[dict]:
        """Get cost center tree structure."""
        root_cost_centers = CostCenter.query.filter_by(parent_id=None).order_by(CostCenter.code).all()
        tree = []
        for cc in root_cost_centers:
            tree.append(CostCenterService._build_tree_node(cc))
        return tree

    @staticmethod
    def _build_tree_node(cost_center: CostCenter) -> dict:
        """Build tree node recursively."""
        node = {
            "id": cost_center.id,
            "code": cost_center.code,
            "name": cost_center.name,
            "department": cost_center.department,
            "budget_allocated": float(cost_center.budget_allocated) if cost_center.budget_allocated else 0.0,
            "budget_used": float(cost_center.get_budget_used()),
            "budget_remaining": float(cost_center.get_budget_remaining()),
            "is_active": cost_center.is_active,
            "children": [],
        }
        for child in cost_center.children:
            if child.is_active:
                node["children"].append(CostCenterService._build_tree_node(child))
        return node
