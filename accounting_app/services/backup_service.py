"""
Backup Service - Business logic for database backup management.
Handles backup creation, scheduling, and restoration.
"""

import os
import shutil
import sqlite3
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple

from core.database import db
from core.utils import utc_now


class BackupService:
    """Service for managing database backups."""

    DEFAULT_BACKUP_DIR = "backups"

    @staticmethod
    def create_backup(
        backup_type: str = "manual",
        created_by: int = None,
        backup_dir: str = None,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Create a database backup.

        Args:
            backup_type: Type of backup (manual, auto, full)
            created_by: User creating backup
            backup_dir: Directory to save backup

        Returns:
            Tuple of (success, result)
        """
        try:
            from models.backup import Backup, BackupSchedule

            db_path = db.engine.url.database
            if not os.path.exists(db_path):
                return False, {"error": "Database file not found"}

            backup_dir = backup_dir or BackupService.DEFAULT_BACKUP_DIR
            os.makedirs(backup_dir, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_no = f"BK-{timestamp}"
            backup_filename = f"accounting_{timestamp}.db"
            backup_path = os.path.join(backup_dir, backup_filename)

            shutil.copy2(db_path, backup_path)
            file_size = os.path.getsize(backup_path)

            backup = Backup(
                backup_no=backup_no,
                backup_type=backup_type,
                file_path=backup_path,
                file_size=file_size,
                status="completed",
                started_at=utc_now(),
                completed_at=utc_now(),
                created_by=created_by,
            )
            db.session.add(backup)
            db.session.commit()

            BackupService.cleanup_old_backups(backup_dir)

            return True, backup.to_dict()
        except Exception as e:
            db.session.rollback()
            return False, {"error": str(e)}

    @staticmethod
    def restore_backup(
        backup_id: int,
        restore_dir: str = None,
    ) -> Tuple[bool, str]:
        """
        Restore database from backup.

        Args:
            backup_id: Backup ID to restore
            restore_dir: Directory to restore to

        Returns:
            Tuple of (success, message)
        """
        try:
            from models.backup import Backup

            backup = db.session.get(Backup, backup_id)
            if not backup:
                return False, "Backup not found"

            if not os.path.exists(backup.file_path):
                return False, "Backup file not found"

            db_path = db.engine.url.database

            if restore_dir:
                os.makedirs(restore_dir, exist_ok=True)
                restore_path = os.path.join(restore_dir, "accounting.db")
            else:
                restore_path = db_path + ".restored"

            shutil.copy2(backup.file_path, restore_path)

            return True, f"Database restored to {restore_path}"
        except Exception as e:
            return False, str(e)

    @staticmethod
    def delete_backup(backup_id: int) -> Tuple[bool, str]:
        """
        Delete a backup.

        Args:
            backup_id: Backup ID to delete

        Returns:
            Tuple of (success, message)
        """
        try:
            from models.backup import Backup

            backup = db.session.get(Backup, backup_id)
            if not backup:
                return False, "Backup not found"

            if os.path.exists(backup.file_path):
                os.remove(backup.file_path)

            db.session.delete(backup)
            db.session.commit()

            return True, "Backup deleted successfully"
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def get_backups(
        backup_type: str = None,
        status: str = None,
        start_date: datetime = None,
        end_date: datetime = None,
    ) -> List[Dict[str, Any]]:
        """
        Get backups with filters.

        Args:
            backup_type: Filter by type
            status: Filter by status
            start_date: Filter start date
            end_date: Filter end date

        Returns:
            List of backups
        """
        from models.backup import Backup

        query = Backup.query

        if backup_type:
            query = query.filter_by(backup_type=backup_type)
        if status:
            query = query.filter_by(status=status)
        if start_date:
            query = query.filter(Backup.started_at >= start_date)
        if end_date:
            query = query.filter(Backup.started_at <= end_date)

        backups = query.order_by(Backup.started_at.desc()).all()
        return [b.to_dict() for b in backups]

    @staticmethod
    def get_backup_by_id(backup_id: int) -> Optional[Dict[str, Any]]:
        """
        Get backup by ID.

        Args:
            backup_id: Backup ID

        Returns:
            Backup dictionary or None
        """
        from models.backup import Backup

        backup = db.session.get(Backup, backup_id)
        return backup.to_dict() if backup else None

    @staticmethod
    def cleanup_old_backups(backup_dir: str = None) -> int:
        """
        Delete backups older than retention period.

        Args:
            backup_dir: Directory to clean

        Returns:
            Number of backups deleted
        """
        from models.backup import Backup
        from models.system_setting import SystemSetting

        backup_dir = backup_dir or BackupService.DEFAULT_BACKUP_DIR
        retention_days = SystemSettingService.get_setting(
            "backup_retention_days", 30
        )

        cutoff_date = datetime.now() - timedelta(days=retention_days)

        old_backups = Backup.query.filter(
            Backup.started_at < cutoff_date
        ).all()

        count = 0
        for backup in old_backups:
            try:
                if os.path.exists(backup.file_path):
                    os.remove(backup.file_path)
                db.session.delete(backup)
                count += 1
            except Exception:
                pass

        db.session.commit()
        return count

    @staticmethod
    def create_schedule(
        name: str,
        backup_type: str,
        frequency: str,
        time_str: str,
        day_of_week: int = None,
        day_of_month: int = None,
        retention_days: int = 30,
        created_by: int = None,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Create a backup schedule.

        Args:
            name: Schedule name
            backup_type: Type of backup
            frequency: Frequency (daily, weekly, monthly)
            time_str: Time to run (HH:MM)
            day_of_week: Day of week (0-6) for weekly
            day_of_month: Day of month (1-31) for monthly
            retention_days: Days to retain backups
            created_by: Creator user ID

        Returns:
            Tuple of (success, result)
        """
        try:
            from models.backup import BackupSchedule

            time_obj = datetime.strptime(time_str, "%H:%M").time()

            next_run = BackupService.calculate_next_run(
                frequency, time_obj, day_of_week, day_of_month
            )

            schedule = BackupSchedule(
                name=name,
                backup_type=backup_type,
                frequency=frequency,
                time=time_obj,
                day_of_week=day_of_week,
                day_of_month=day_of_month,
                retention_days=retention_days,
                is_active=True,
                next_run=next_run,
                created_by=created_by,
            )
            db.session.add(schedule)
            db.session.commit()
            return True, schedule.to_dict()
        except Exception as e:
            db.session.rollback()
            return False, {"error": str(e)}

    @staticmethod
    def calculate_next_run(
        frequency: str,
        time_obj,
        day_of_week: int = None,
        day_of_month: int = None,
    ) -> datetime:
        """Calculate next run time for schedule."""
        now = datetime.now()
        time_str = time_obj.strftime("%H:%M")

        if frequency == "daily":
            next_run = datetime.strptime(
                now.strftime("%Y-%m-%d") + " " + time_str,
                "%Y-%m-%d %H:%M"
            )
            if next_run <= now:
                next_run += timedelta(days=1)

        elif frequency == "weekly":
            days_ahead = day_of_week - now.weekday()
            if days_ahead < 0:
                days_ahead += 7
            next_run = datetime.strptime(
                (now + timedelta(days=days_ahead)).strftime("%Y-%m-%d") + " " + time_str,
                "%Y-%m-%d %H:%M"
            )

        elif frequency == "monthly":
            if day_of_month is None:
                day_of_month = 1
            if now.day >= day_of_month:
                next_month = now.replace(day=1) + timedelta(days=32)
                next_month = next_month.replace(day=day_of_month)
            else:
                next_month = now.replace(day=day_of_month)
            next_run = datetime.strptime(
                next_month.strftime("%Y-%m-%d") + " " + time_str,
                "%Y-%m-%d %H:%M"
            )

        else:
            next_run = now + timedelta(days=1)

        return next_run

    @staticmethod
    def get_schedules(is_active: bool = None) -> List[Dict[str, Any]]:
        """
        Get backup schedules.

        Args:
            is_active: Filter by active status

        Returns:
            List of schedules
        """
        from models.backup import BackupSchedule

        query = BackupSchedule.query
        if is_active is not None:
            query = query.filter_by(is_active=is_active)

        schedules = query.order_by(BackupSchedule.time).all()
        return [s.to_dict() for s in schedules]

    @staticmethod
    def update_schedule(
        schedule_id: int,
        **kwargs,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Update a backup schedule.

        Args:
            schedule_id: Schedule ID
            **kwargs: Fields to update

        Returns:
            Tuple of (success, result)
        """
        try:
            from models.backup import BackupSchedule

            schedule = db.session.get(BackupSchedule, schedule_id)
            if not schedule:
                return False, {"error": "Schedule not found"}

            for key, value in kwargs.items():
                if hasattr(schedule, key):
                    setattr(schedule, key, value)

            schedule.next_run = BackupService.calculate_next_run(
                schedule.frequency,
                schedule.time,
                schedule.day_of_week,
                schedule.day_of_month,
            )

            db.session.commit()
            return True, schedule.to_dict()
        except Exception as e:
            db.session.rollback()
            return False, {"error": str(e)}

    @staticmethod
    def delete_schedule(schedule_id: int) -> Tuple[bool, str]:
        """
        Delete a backup schedule.

        Args:
            schedule_id: Schedule ID

        Returns:
            Tuple of (success, message)
        """
        try:
            from models.backup import BackupSchedule

            schedule = db.session.get(BackupSchedule, schedule_id)
            if not schedule:
                return False, "Schedule not found"

            db.session.delete(schedule)
            db.session.commit()

            return True, "Schedule deleted successfully"
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def get_backup_statistics() -> Dict[str, Any]:
        """
        Get backup statistics.

        Returns:
            Dictionary of statistics
        """
        from models.backup import Backup

        total = Backup.query.count()
        total_size = sum(b.file_size or 0 for b in Backup.query.all())
        completed = Backup.query.filter_by(status="completed").count()
        failed = Backup.query.filter_by(status="failed").count()

        latest = Backup.query.order_by(Backup.started_at.desc()).first()
        last_backup = latest.to_dict() if latest else None

        return {
            "total_backups": total,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "completed": completed,
            "failed": failed,
            "last_backup": last_backup,
        }
