import logging
import logging.handlers
import sys
import json
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

from flask import has_request_context, request, g


# ANSI color codes for console output
COLORS = {
    'DEBUG': '\033[36m',      # Cyan
    'INFO': '\033[32m',       # Green
    'WARNING': '\033[33m',    # Yellow
    'ERROR': '\033[31m',      # Red
    'CRITICAL': '\033[35m',   # Magenta
    'RESET': '\033[0m',       # Reset
    'BOLD': '\033[1m',        # Bold
    'DIM': '\033[2m',         # Dim
    'TIMESTAMP': '\033[90m',  # Gray for timestamps
    'MODULE': '\033[34m',     # Blue for module names
}

# Check if terminal supports colors
def supports_color() -> bool:
    """Check if the terminal supports ANSI colors."""
    return (
        hasattr(sys.stdout, 'isatty') and sys.stdout.isatty() and
        os.environ.get('TERM') != 'dumb' and
        os.environ.get('NO_COLOR') is None
    )


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
        except Exception:
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
    
    def __init__(self, pretty_print: bool = False):
        """Initialize JSON formatter.
        
        Args:
            pretty_print: If True, format JSON with indentation for readability
        """
        super().__init__()
        self.pretty_print = pretty_print
    
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
        
        if self.pretty_print:
            return json.dumps(log_data, indent=2, ensure_ascii=False)
        return json.dumps(log_data, ensure_ascii=False)


class ColoredConsoleFormatter(logging.Formatter):
    """Colorized console formatter for development."""
    
    def __init__(self, fmt: str = None, datefmt: str = None):
        """Initialize colored console formatter.
        
        Args:
            fmt: Log format string (ignored, using custom format)
            datefmt: Date format string
        """
        super().__init__(datefmt='%Y-%m-%d %H:%M:%S')
        self.use_colors = supports_color()
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors and icons."""
        timestamp = datetime.fromtimestamp(record.created).strftime(self.datefmt)
        
        # Get level-specific formatting
        level = record.levelname
        if self.use_colors:
            level_color = COLORS.get(level, '')
            level_display = f"{level_color}{COLORS['BOLD']}{level:8}{COLORS['RESET']}"
        else:
            level_display = f"{level:8}"
        
        # Get module name
        module = record.module
        if self.use_colors:
            module_display = f"{COLORS['MODULE']}{module:15}{COLORS['RESET']}"
        else:
            module_display = f"{module:15}"
        
        # Get message
        message = record.getMessage()
        
        # Format timestamp
        if self.use_colors:
            timestamp_display = f"{COLORS['TIMESTAMP']}{timestamp}{COLORS['RESET']}"
        else:
            timestamp_display = timestamp
        
        # Build the log line
        line = f"{timestamp_display} {level_display} {module_display} │ {message}"
        
        # Add exception info if present
        if record.exc_info and record.exc_info[0] is not None:
            exception_text = self.formatException(record.exc_info)
            if self.use_colors:
                line += f"\n{COLORS['ERROR']}{exception_text}{COLORS['RESET']}"
            else:
                line += f"\n{exception_text}"
        
        return line


def setup_logging(app) -> None:
    """Configure application logging with rotation."""
    log_file = app.config.get("LOG_FILE")
    log_level = app.config.get("LOG_LEVEL", "INFO")
    is_debug = app.config.get("DEBUG", False)
    
    # Create logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler (colorized for development)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level))
    console_handler.setFormatter(ColoredConsoleFormatter())
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
        # Use pretty_print in development for easier debugging
        file_handler.setFormatter(JsonFormatter(pretty_print=is_debug))
        root_logger.addHandler(file_handler)
    
    # Reduce noise from libraries
    library_loggers = {
        "sqlalchemy": logging.WARNING,
        "werkzeug": logging.WARNING,
        "flask_sqlalchemy": logging.WARNING,
        "urllib3": logging.WARNING,
        "requests": logging.WARNING,
    }
    
    for logger_name, level in library_loggers.items():
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)
    
    # In development, allow SQLAlchemy INFO for query timing but filter noise
    if is_debug:
        sqlalchemy_logger = logging.getLogger("sqlalchemy.engine")
        sqlalchemy_logger.setLevel(logging.WARNING)  # Disable SQL echo
        # Only log slow queries (>100ms) at INFO level
        sqlalchemy_logger = logging.getLogger("sqlalchemy.engine.Engine")
        sqlalchemy_logger.setLevel(logging.WARNING)
    
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


def log_accounting_event(
    event_type: str,
    description: str,
    account_code: str = None,
    amount: float = None,
    voucher_id: int = None,
    user_id: int = None,
):
    """Log accounting-specific events with structured data.
    
    Args:
        event_type: Type of event (voucher_created, account_updated, etc.)
        description: Human-readable description
        account_code: Account code involved (e.g., '111', '511')
        amount: Monetary amount if applicable
        voucher_id: Journal voucher ID if applicable
        user_id: User performing the action
    """
    logger = logging.getLogger('accounting')
    
    log_data = {
        "event_type": event_type,
        "description": description,
    }
    
    if account_code:
        log_data['account_code'] = account_code
    if amount is not None:
        log_data['amount'] = amount
    if voucher_id:
        log_data['voucher_id'] = voucher_id
    if user_id:
        log_data['user_id'] = user_id
    
    # Add request context if available
    if has_request_context():
        log_data['ip_address'] = request.remote_addr
        log_data['method'] = request.method
        log_data['path'] = request.path
    
    logger.info(f"ACCOUNTING: {json.dumps(log_data)}")


def log_performance(
    operation: str,
    duration_ms: float,
    details: dict = None,
):
    """Log performance metrics for monitoring.
    
    Args:
        operation: Operation name (e.g., 'report_generation', 'db_query')
        duration_ms: Duration in milliseconds
        details: Additional details about the operation
    """
    logger = logging.getLogger('performance')
    
    log_data = {
        "operation": operation,
        "duration_ms": round(duration_ms, 2),
    }
    
    if details:
        log_data.update(details)
    
    # Log at different levels based on duration
    if duration_ms > 5000:  # >5 seconds
        logger.warning(f"SLOW: {json.dumps(log_data)}")
    elif duration_ms > 1000:  # >1 second
        logger.info(f"PERFORMANCE: {json.dumps(log_data)}")
    else:
        logger.debug(f"PERFORMANCE: {json.dumps(log_data)}")
