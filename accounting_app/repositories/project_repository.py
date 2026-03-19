from datetime import date
from decimal import Decimal
from typing import List, Optional, Tuple

from core.database import db
from models.project import Project


class ProjectRepository:
    """Repository for Project CRUD operations."""

    @staticmethod
    def get_all(
        page: int = 1,
        per_page: int = 20,
        is_active: Optional[bool] = None,
        status: Optional[str] = None,
        project_type: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[Project], int]:
        """Get paginated projects with filters."""
        query = Project.query

        if is_active is not None:
            query = query.filter(Project.is_active == is_active)

        if status:
            query = query.filter(Project.status == status)

        if project_type:
            query = query.filter(Project.project_type == project_type)

        if search:
            query = query.filter(
                db.or_(
                    Project.code.ilike(f"%{search}%"),
                    Project.name.ilike(f"%{search}%"),
                )
            )

        query = query.order_by(Project.code)
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        return pagination.items, pagination.total

    @staticmethod
    def get_by_id(project_id: int) -> Optional[Project]:
        """Get project by ID."""
        return db.session.get(Project, project_id)

    @staticmethod
    def get_by_code(code: str) -> Optional[Project]:
        """Get project by code."""
        return Project.query.filter_by(code=code).first()

    @staticmethod
    def create(
        code: str,
        name: str,
        created_by: int,
        description: Optional[str] = None,
        customer_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        expected_completion_date: Optional[date] = None,
        status: str = "planning",
        project_type: str = "service",
        total_contract_value: Decimal = Decimal("0.00"),
        manager_id: Optional[int] = None,
        cost_center_id: Optional[int] = None,
    ) -> Project:
        """Create a new project."""
        project = Project(
            code=code,
            name=name,
            description=description,
            customer_id=customer_id,
            start_date=start_date,
            end_date=end_date,
            expected_completion_date=expected_completion_date,
            status=status,
            project_type=project_type,
            total_contract_value=total_contract_value,
            manager_id=manager_id,
            cost_center_id=cost_center_id,
            created_by=created_by,
        )
        db.session.add(project)
        db.session.commit()
        return project

    @staticmethod
    def update(
        project_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        customer_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        expected_completion_date: Optional[date] = None,
        status: Optional[str] = None,
        project_type: Optional[str] = None,
        total_contract_value: Optional[Decimal] = None,
        completion_percentage: Optional[Decimal] = None,
        manager_id: Optional[int] = None,
        cost_center_id: Optional[int] = None,
        is_active: Optional[bool] = None,
    ) -> Optional[Project]:
        """Update project."""
        project = db.session.get(Project, project_id)
        if not project:
            return None

        if name is not None:
            project.name = name
        if description is not None:
            project.description = description
        if customer_id is not None:
            project.customer_id = customer_id
        if start_date is not None:
            project.start_date = start_date
        if end_date is not None:
            project.end_date = end_date
        if expected_completion_date is not None:
            project.expected_completion_date = expected_completion_date
        if status is not None:
            project.status = status
        if project_type is not None:
            project.project_type = project_type
        if total_contract_value is not None:
            project.total_contract_value = total_contract_value
        if completion_percentage is not None:
            project.completion_percentage = completion_percentage
        if manager_id is not None:
            project.manager_id = manager_id
        if cost_center_id is not None:
            project.cost_center_id = cost_center_id
        if is_active is not None:
            project.is_active = is_active

        db.session.commit()
        return project

    @staticmethod
    def delete(project_id: int) -> bool:
        """Delete project (soft delete by setting inactive)."""
        project = db.session.get(Project, project_id)
        if not project:
            return False

        project.is_active = False
        db.session.commit()
        return True

    @staticmethod
    def get_active() -> List[Project]:
        """Get all active projects."""
        return Project.query.filter_by(is_active=True).order_by(Project.code).all()

    @staticmethod
    def get_by_status(status: str) -> List[Project]:
        """Get projects by status."""
        return Project.query.filter_by(status=status, is_active=True).order_by(Project.code).all()

    @staticmethod
    def get_summary() -> dict:
        """Get project summary statistics."""
        total = Project.query.count()
        active = Project.query.filter_by(is_active=True).count()
        by_status = {}
        for status_choice, _ in Project.Status:
            count = Project.query.filter_by(status=status_choice, is_active=True).count()
            by_status[status_choice] = count

        total_contract = db.session.query(db.func.sum(Project.total_contract_value)).scalar() or Decimal("0.00")
        total_revenue = db.session.query(db.func.sum(Project.total_revenue)).scalar() or Decimal("0.00")
        total_expense = db.session.query(db.func.sum(Project.total_expense)).scalar() or Decimal("0.00")

        return {
            "total_projects": total,
            "active_projects": active,
            "by_status": by_status,
            "total_contract_value": total_contract,
            "total_revenue": total_revenue,
            "total_expense": total_expense,
            "total_profit": total_revenue - total_expense,
        }
