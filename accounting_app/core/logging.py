import logging
import logging.handlers
import sys
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

from flask import has_request_context, request, g


class StructuredLogger:
    """Structured logger with JSON formatting and user context."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
    
    def _get_user_id(self) -> Optional[int]:
        """Get current user ID if available."""
        try:
            if has_request_context() and hasattr(g, 'current_user'):
                return g.current_user.id
            from flask_login import current_user
            if current_user.is_authenticated:
                return current_user.id
        except:
            pass
        return None
    
    def _get_extra(self) -> dict:
        """Get extra context for log records."""
        extra = {}
        if has_request_context():
            extra['ip_address'] = request.remote_addr
            extra['method'] = request.method
            extra['path'] = request.path
            user_id = self._get_user_id()
            if user_id:
                extra['user_id'] = user_id
        return extra
    
    def info(self, message: str, **kwargs):
        """Log info with context."""
        extra = self._get_extra()
        extra.update(kwargs)
        self.logger.info(message, extra=extra)
    
    def warning(self, message: str, **kwargs):
        """Log warning with context."""
        extra = self._get_extra()
        extra.update(kwargs)
        self.logger.warning(message, extra=extra)
    
    def error(self, message: str, **kwargs):
        """Log error with context."""
        extra = self._get_extra()
        extra.update(kwargs)
        self.logger.error(message, extra=extra)
    
    def debug(self, message: str, **kwargs):
        """Log debug with context."""
        extra = self._get_extra()
        extra.update(kwargs)
        self.logger.debug(message, extra=extra)


class JsonFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "module": record.module,
            "function": record.funcName,
            "message": record.getMessage(),
        }
        
        # Add user context
        if hasattr(record, 'user_id') and record.user_id:
            log_data['user_id'] = record.user_id
        
        if hasattr(record, 'ip_address') and record.ip_address:
            log_data['ip_address'] = record.ip_address
        
        if hasattr(record, 'method') and record.method:
            log_data['method'] = record.method
        
        if hasattr(record, 'path') and record.path:
            log_data['path'] = record.path
        
        # Add extra fields
        for key in ['action', 'entity', 'entity_id', 'old_value', 'new_value']:
            if hasattr(record, key):
                val = getattr(record, key)
                if val is not None:
                    log_data[key] = val
        
        # Add exception info
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)


def setup_logging(app) -> None:
    """Configure application logging with rotation."""
    log_file = app.config.get("LOG_FILE")
    log_level = app.config.get("LOG_LEVEL", "INFO")
    
    # Create logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler (human readable)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler with rotation (JSON format)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Rotating file handler - 10MB per file, keep 10 files
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=10,
            encoding='utf-8'
        )
        file_handler.setLevel(getattr(logging, log_level))
        file_handler.setFormatter(JsonFormatter())
        root_logger.addHandler(file_handler)
    
    # Reduce noise from libraries
    for logger_name in ["sqlalchemy", "werkzeug", "flask_sqlalchemy"]:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.WARNING)
    
    app.logger.info("Logging system initialized")


def log_audit(
    action: str,
    entity: str,
    entity_id: int = None,
    old_value: str = None,
    new_value: str = None,
    user_id: int = None,
    request_obj = None,
):
    """Log audit action to both file and database.
    
    Args:
        action: create, read, update, delete, login, logout, etc.
        entity: account, journal, user, etc.
        entity_id: ID of affected entity
        old_value: Previous value (JSON string)
        new_value: New value (JSON string)
        user_id: User performing action
        request_obj: Flask request object for IP
    """
    from flask import has_request_context, request
    from core.database import db
    from models.audit_log import AuditLog
    
    logger = logging.getLogger(__name__)
    
    # Get IP address
    ip_address = None
    if request_obj:
        ip_address = request_obj.remote_addr
    elif has_request_context():
        ip_address = request.remote_addr
    
    # Get user agent
    user_agent = None
    if request_obj:
        user_agent = request_obj.headers.get('User-Agent')
    elif has_request_context():
        user_agent = request.headers.get('User-Agent')
    
    # Log to database
    try:
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            entity=entity,
            entity_id=entity_id,
            old_value=old_value,
            new_value=new_value,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        db.session.add(audit_log)
        db.session.commit()
    except Exception as e:
        logger.error(f"Failed to write audit log to database: {e}")
    
    # Log to file
    log_data = {
        "audit": True,
        "action": action,
        "entity": entity,
        "entity_id": entity_id,
        "user_id": user_id,
        "ip_address": ip_address,
    }
    logger.info(f"AUDIT: {json.dumps(log_data)}")


def get_logger(name: str) -> StructuredLogger:
    """Get a structured logger instance."""
    return StructuredLogger(name)
