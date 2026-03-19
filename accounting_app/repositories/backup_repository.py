from datetime import datetime
from typing import List, Optional, Tuple

from core.database import db
from models.backup import Backup, BackupSchedule, BackupType, BackupStatus


class BackupRepository:
    """Repository for Backup and BackupSchedule."""

    @staticmethod
    def get_backup_by_id(backup_id: int) -> Optional[Backup]:
        """Get backup by ID."""
        return db.session.get(Backup, backup_id)

    @staticmethod
    def get_backups(page: int = 1, per_page: int = 20, status: str = None, backup_type: str = None) -> Tuple[List[Backup], int]:
        """Get paginated backups."""
        query = Backup.query

        if status:
            query = query.filter(Backup.status == status)
        if backup_type:
            query = query.filter(Backup.backup_type == backup_type)

        query = query.order_by(Backup.created_at.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        return pagination.items, pagination.total

    @staticmethod
    def create_backup(backup_type: str, created_by: int) -> Backup:
        """Create a new backup record."""
        backup_no = Backup.generate_backup_no()
        backup = Backup(
            backup_no=backup_no,
            backup_type=backup_type,
            created_by=created_by,
        )
        db.session.add(backup)
        db.session.commit()
        return backup

    @staticmethod
    def get_schedule_by_id(schedule_id: int) -> Optional[BackupSchedule]:
        """Get schedule by ID."""
        return db.session.get(BackupSchedule, schedule_id)

    @staticmethod
    def get_active_schedules() -> List[BackupSchedule]:
        """Get all active backup schedules."""
        return BackupSchedule.query.filter_by(is_active=True).order_by(BackupSchedule.name).all()

    @staticmethod
    def create_schedule(name: str, backup_type: str, schedule_type: str, created_by: int, schedule_value: str = None, retention_days: int = 30, destination_path: str = None, compress: bool = True, encrypt: bool = False) -> BackupSchedule:
        """Create a new backup schedule."""
        schedule = BackupSchedule(
            name=name,
            backup_type=backup_type,
            schedule_type=schedule_type,
            schedule_value=schedule_value,
            retention_days=retention_days,
            destination_path=destination_path,
            compress=compress,
            encrypt=encrypt,
            created_by=created_by,
        )
        db.session.add(schedule)
        db.session.commit()
        return schedule

    @staticmethod
    def update_schedule_next_run(schedule_id: int, next_run_at: datetime) -> Optional[BackupSchedule]:
        """Update schedule next run time."""
        schedule = db.session.get(BackupSchedule, schedule_id)
        if schedule:
            schedule.next_run_at = next_run_at
            db.session.commit()
        return schedule

    @staticmethod
    def cleanup_old_backups(retention_days: int = 30) -> int:
        """Delete backups older than retention days."""
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(days=retention_days)
        count = Backup.query.filter(
            Backup.created_at < cutoff,
            Backup.status.in_([BackupStatus.COMPLETED, BackupStatus.VERIFIED])
        ).delete()
        db.session.commit()
        return count
