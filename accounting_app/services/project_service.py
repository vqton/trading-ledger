from datetime import date
from decimal import Decimal
from typing import List, Optional, Tuple

from repositories.project_repository import ProjectRepository
from models.project import Project
from core.logging import log_audit


class ProjectService:
    """Service for Project business logic."""

    @staticmethod
    def get_projects(
        page: int = 1,
        per_page: int = 20,
        is_active: Optional[bool] = None,
        status: Optional[str] = None,
        project_type: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[Project], int]:
        """Get paginated projects."""
        return ProjectRepository.get_all(page, per_page, is_active, status, project_type, search)

    @staticmethod
    def get_project(project_id: int) -> Optional[Project]:
        """Get project by ID."""
        return ProjectRepository.get_by_id(project_id)

    @staticmethod
    def get_project_by_code(code: str) -> Optional[Project]:
        """Get project by code."""
        return ProjectRepository.get_by_code(code)

    @staticmethod
    def create_project(
        name: str,
        created_by: int,
        code: Optional[str] = None,
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
    ) -> Tuple[Optional[Project], Optional[str]]:
        """Create a new project with validation."""
        if code is None:
            code = Project.generate_code()
        else:
            if ProjectRepository.get_by_code(code):
                return None, f"Mã dự án '{code}' đã tồn tại"

        if len(name) < 3:
            return None, "Tên dự án phải có ít nhất 3 ký tự"

        if total_contract_value < 0:
            return None, "Giá trị hợp đồng không được âm"

        if start_date and end_date and start_date > end_date:
            return None, "Ngày bắt đầu phải trước ngày kết thúc"

        project = ProjectRepository.create(
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

        log_audit(
            user_id=created_by,
            action="create",
            entity="project",
            entity_id=project.id,
            new_value=project.to_dict(),
        )

        return project, None

    @staticmethod
    def update_project(
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
    ) -> Tuple[Optional[Project], Optional[str]]:
        """Update project with validation."""
        old_project = ProjectRepository.get_by_id(project_id)
        if not old_project:
            return None, "Dự án không tồn tại"

        if name is not None and len(name) < 3:
            return None, "Tên dự án phải có ít nhất 3 ký tự"

        if total_contract_value is not None and total_contract_value < 0:
            return None, "Giá trị hợp đồng không được âm"

        if completion_percentage is not None:
            if completion_percentage < 0 or completion_percentage > 100:
                return None, "Phần trăm hoàn thành phải từ 0 đến 100"

        project = ProjectRepository.update(
            project_id=project_id,
            name=name,
            description=description,
            customer_id=customer_id,
            start_date=start_date,
            end_date=end_date,
            expected_completion_date=expected_completion_date,
            status=status,
            project_type=project_type,
            total_contract_value=total_contract_value,
            completion_percentage=completion_percentage,
            manager_id=manager_id,
            cost_center_id=cost_center_id,
            is_active=is_active,
        )

        log_audit(
            user_id=old_project.created_by,
            action="update",
            entity="project",
            entity_id=project.id,
            old_value=old_project.to_dict(),
            new_value=project.to_dict(),
        )

        return project, None

    @staticmethod
    def delete_project(project_id: int, user_id: int) -> Tuple[bool, Optional[str]]:
        """Soft delete project."""
        project = ProjectRepository.get_by_id(project_id)
        if not project:
            return False, "Dự án không tồn tại"

        success = ProjectRepository.delete(project_id)
        if success:
            log_audit(
                user_id=user_id,
                action="delete",
                entity="project",
                entity_id=project_id,
                old_value=project.to_dict(),
            )
        return success, None

    @staticmethod
    def complete_project(project_id: int, user_id: int) -> Tuple[Optional[Project], Optional[str]]:
        """Mark project as completed."""
        project = ProjectRepository.get_by_id(project_id)
        if not project:
            return None, "Dự án không tồn tại"

        if project.status == "completed":
            return None, "Dự án đã hoàn thành"

        project.update_totals()

        return ProjectService.update_project(
            project_id=project_id,
            status="completed",
            completion_percentage=Decimal("100.00"),
        )

    @staticmethod
    def refresh_project_totals(project_id: int) -> Optional[Project]:
        """Refresh project revenue and expense from journal entries."""
        project = ProjectRepository.get_by_id(project_id)
        if project:
            project.update_totals()
        return project

    @staticmethod
    def get_active_projects() -> List[Project]:
        """Get all active projects."""
        return ProjectRepository.get_active()

    @staticmethod
    def get_projects_by_status(status: str) -> List[Project]:
        """Get projects by status."""
        return ProjectRepository.get_by_status(status)

    @staticmethod
    def get_project_summary() -> dict:
        """Get project summary statistics."""
        return ProjectRepository.get_summary()

    @staticmethod
    def get_projects_by_customer(customer_id: int) -> List[Project]:
        """Get projects for a customer."""
        return Project.query.filter_by(customer_id=customer_id, is_active=True).order_by(Project.code).all()
