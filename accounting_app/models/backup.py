from datetime import datetime
from decimal import Decimal
from typing import Optional

from core.database import db
from core.utils import utc_now


class BackupStatus:
    """Backup status constants."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    VERIFIED = "verified"

    CHOICES = [
        (PENDING, "Chờ thực hiện"),
        (IN_PROGRESS, "Đang thực hiện"),
        (COMPLETED, "Hoàn thành"),
        (FAILED, "Thất bại"),
        (VERIFIED, "Đã xác minh"),
    ]


class BackupType:
    """Backup type constants."""

    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"

    CHOICES = [
        (FULL, "Toàn bộ"),
        (INCREMENTAL, "Gia tăng"),
        (DIFFERENTIAL, "Vi sai"),
    ]


class Backup(db.Model):
    """Backup model for tracking database backups."""

    __tablename__ = "backups"

    id = db.Column(db.Integer, primary_key=True)
    backup_no = db.Column(db.String(50), unique=True, nullable=False, index=True)
    backup_type = db.Column(db.String(20), default=BackupType.FULL, nullable=False)
    status = db.Column(db.String(20), default=BackupStatus.PENDING, nullable=False, index=True)
    file_path = db.Column(db.String(500), nullable=True)
    file_name = db.Column(db.String(255), nullable=True)
    file_size = db.Column(db.BigInteger, nullable=True)
    checksum = db.Column(db.String(64), nullable=True)
    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    duration_seconds = db.Column(db.Integer, nullable=True)
    error_message = db.Column(db.Text, nullable=True)
    verified_at = db.Column(db.DateTime, nullable=True)
    verified_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    restored_at = db.Column(db.DateTime, nullable=True)
    restored_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)

    creator = db.relationship("User", backref="created_backups", foreign_keys=[created_by])
    verifier = db.relationship("User", backref="verified_backups", foreign_keys=[verified_by])
    restorer = db.relationship("User", backref="restored_backups", foreign_keys=[restored_by])

    __table_args__ = (
        db.Index("ix_backup_date", "created_at"),
        db.Index("ix_backup_status", "status"),
    )

    def __repr__(self) -> str:
        return f"<Backup {self.backup_no} - {self.status}>"

    @property
    def is_completed(self) -> bool:
        """Check if backup is completed."""
        return self.status == BackupStatus.COMPLETED

    @property
    def is_failed(self) -> bool:
        """Check if backup failed."""
        return self.status == BackupStatus.FAILED

    @property
    def is_verified(self) -> bool:
        """Check if backup is verified."""
        return self.status == BackupStatus.VERIFIED

    def start(self) -> None:
        """Mark backup as started."""
        self.status = BackupStatus.IN_PROGRESS
        self.started_at = utc_now()
        db.session.commit()

    def complete(self, file_path: str, file_size: int = None, checksum: str = None) -> None:
        """Mark backup as completed."""
        self.status = BackupStatus.COMPLETED
        self.file_path = file_path
        self.file_name = file_path.split("/")[-1] if "/" in file_path else file_path
        self.file_size = file_size
        self.checksum = checksum
        self.completed_at = utc_now()
        if self.started_at:
            self.duration_seconds = int((self.completed_at - self.started_at).total_seconds())
        db.session.commit()

    def fail(self, error_message: str) -> None:
        """Mark backup as failed."""
        self.status = BackupStatus.FAILED
        self.error_message = error_message
        self.completed_at = utc_now()
        if self.started_at:
            self.duration_seconds = int((self.completed_at - self.started_at).total_seconds())
        db.session.commit()

    def verify(self, user_id: int) -> None:
        """Mark backup as verified."""
        self.status = BackupStatus.VERIFIED
        self.verified_at = utc_now()
        self.verified_by = user_id
        db.session.commit()

    def mark_restored(self, user_id: int) -> None:
        """Mark backup as restored."""
        self.restored_at = utc_now()
        self.restored_by = user_id
        db.session.commit()

    @classmethod
    def generate_backup_no(cls) -> str:
        """Generate backup number."""
        today = datetime.now()
        year = today.year
        month = today.month
        day = today.day

        last_backup = cls.query.filter(
            cls.backup_no.like(f"BCK-{year}{month:02d}{day:02d}%")
        ).order_by(cls.backup_no.desc()).first()

        if last_backup:
            last_num = int(last_backup.backup_no.split("-")[-1])
            new_num = last_num + 1
        else:
            new_num = 1

        return f"BCK-{year}{month:02d}{day:02d}-{new_num:04d}"

    def to_dict(self) -> dict:
        """Convert backup to dictionary."""
        return {
            "id": self.id,
            "backup_no": self.backup_no,
            "backup_type": self.backup_type,
            "status": self.status,
            "file_path": self.file_path,
            "file_name": self.file_name,
            "file_size": self.file_size,
            "checksum": self.checksum,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_seconds": self.duration_seconds,
            "error_message": self.error_message,
            "verified_at": self.verified_at.isoformat() if self.verified_at else None,
            "verified_by": self.verified_by,
            "restored_at": self.restored_at.isoformat() if self.restored_at else None,
            "restored_by": self.restored_by,
            "notes": self.notes,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class BackupSchedule(db.Model):
    """Backup Schedule model for automated backups."""

    __tablename__ = "backup_schedules"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    backup_type = db.Column(db.String(20), default=BackupType.FULL, nullable=False)
    schedule_type = db.Column(db.String(20), nullable=False)
    schedule_value = db.Column(db.String(50), nullable=True)
    retention_days = db.Column(db.Integer, default=30)
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    last_run_at = db.Column(db.DateTime, nullable=True)
    next_run_at = db.Column(db.DateTime, nullable=True)
    max_file_size_mb = db.Column(db.Integer, default=1024)
    compress = db.Column(db.Boolean, default=True)
    encrypt = db.Column(db.Boolean, default=False)
    destination_path = db.Column(db.String(500), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    creator = db.relationship("User", backref="backup_schedules")

    def __repr__(self) -> str:
        return f"<BackupSchedule {self.name}>"

    def to_dict(self) -> dict:
        """Convert schedule to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "backup_type": self.backup_type,
            "schedule_type": self.schedule_type,
            "schedule_value": self.schedule_value,
            "retention_days": self.retention_days,
            "is_active": self.is_active,
            "last_run_at": self.last_run_at.isoformat() if self.last_run_at else None,
            "next_run_at": self.next_run_at.isoformat() if self.next_run_at else None,
            "max_file_size_mb": self.max_file_size_mb,
            "compress": self.compress,
            "encrypt": self.encrypt,
            "destination_path": self.destination_path,
            "notes": self.notes,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ScheduleType:
    """Schedule type constants."""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

    CHOICES = [
        (DAILY, "Hàng ngày"),
        (WEEKLY, "Hàng tuần"),
        (MONTHLY, "Hàng tháng"),
    ]
