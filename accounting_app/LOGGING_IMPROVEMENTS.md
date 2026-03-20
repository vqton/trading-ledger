# Logging System Improvements

## Overview
The logging system has been upgraded to provide better readability, reduced noise, and enhanced debugging capabilities.

## Key Improvements

### 1. **Reduced SQLAlchemy Noise**
- Disabled `SQLALCHEMY_ECHO` in development config
- Set SQLAlchemy loggers to WARNING level
- Only important queries are now logged

### 2. **Colorized Console Output**
- ANSI color support for terminals
- Color-coded log levels:
  - **DEBUG**: Cyan
  - **INFO**: Green
  - **WARNING**: Yellow
  - **ERROR**: Red
  - **CRITICAL**: Magenta
- Timestamps in gray, module names in blue
- Automatic color detection (respects `NO_COLOR` env var)

### 3. **Improved JSON Logging**
- Pretty-printed JSON in development mode
- Compact JSON in production
- Structured data for easy parsing

### 4. **New Logging Functions**

#### `log_accounting_event()`
Logs accounting-specific events with structured data:
```python
log_accounting_event(
    event_type='voucher_created',
    description='Created journal voucher #123',
    account_code='111',
    amount=1000000.0,
    voucher_id=123,
    user_id=1
)
```

#### `log_performance()`
Logs performance metrics with automatic level selection:
```python
log_performance(
    operation='report_generation',
    duration_ms=1250.5,
    details={'report_type': 'balance_sheet'}
)
```
- <1 second: DEBUG level
- 1-5 seconds: INFO level
- \>5 seconds: WARNING level

### 5. **Better Request Logging**
- Cleaner format with status icons (✓, →,✗)
- Duration in milliseconds
- Only logged in DEBUG mode

## Console Output Format
```
2026-03-20 16:24:24 INFO     logging         │ ACCOUNTING: {"event_type": "voucher_created", ...}
2026-03-20 16:24:24 WARNING  logging         │ SLOW: {"operation": "db_query", "duration_ms": 6500.0}
```

## JSON Log Format (Development)
```json
{
  "timestamp": "2026-03-20T09:24:24.879781+00:00",
  "level": "INFO",
  "module": "logging",
  "function": "log_accounting_event",
  "message": "ACCOUNTING: {\"event_type\": \"voucher_created\", ...}"
}
```

## Configuration
- **Development**: Pretty-printed JSON, colorized console
- **Production**: Compact JSON, plain console (no colors)
- **Log rotation**: 10MB per file, keep 10 backups

## Usage Examples

### Basic Logging
```python
from core.logging import get_logger

logger = get_logger(__name__)
logger.info("User logged in", user_id=123)
logger.error("Failed to save voucher", voucher_id=456)
```

### Accounting Events
```python
from core.logging import log_accounting_event

log_accounting_event(
    event_type='account_updated',
    description='Updated account 111 - Cash',
    account_code='111',
    user_id=current_user.id
)
```

### Performance Monitoring
```python
from core.logging import log_performance
import time

start = time.time()
# ... operation ...
duration = (time.time() - start) * 1000

log_performance(
    operation='balance_sheet_generation',
    duration_ms=duration,
    details={'period': '2026-Q1'}
)
```

## Environment Variables
- `NO_COLOR=1`: Disable colored output
- `TERM=dumb`: Disable colored output
- `FLASK_ENV=development`: Enable pretty JSON logging

## Files Modified
- `core/logging.py`: New formatters, helper functions
- `config.py`: Disabled SQLALCHEMY_ECHO
- `app.py`: Improved request logging format
