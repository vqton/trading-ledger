Dưới đây là **file `AGENTS.md` hoàn chỉnh dạng Markdown** để bạn có thể **copy–paste trực tiếp vào project** (dùng cho OpenCode / Cursor / Copilot Agents / Devin style workflows).

---

```markdown
# AGENTS.md

This document defines the conventions, commands, and expectations for coding agents working in this repository. It is intended to be read by humans and by automated agents that participate in the development workflow.

The goal is to keep changes safe, auditable, and aligned with the project’s architectural guidance (see AGENTS.md for project context embedded in this repository).

---

## 1) Build, lint, and test commands
### Frontend/Template tooling
- Plan to upgrade frontend with a stable local asset stack:
  - Add a minimal frontend package.json with build scripts (see project frontend patch).
  - Introduce assets/scss/main.scss and variables/_base.scss for design tokens.
  - Generate static/css/app.css from SCSS and reference in templates.
  - Keep Bootstrap 5 as a stable dependency (local vendor or build step).
  - Optional: add a small design-system macro layer for templates.
- Environment setup (one-time):
  - Create a virtual environment and install deps:
    - ``python3 -m venv venv``
    - ``source venv/bin/activate``
    - ``pip install -r requirements.txt``
  - Optional: install dev tools for linting/testing as needed (black, isort, flake8, mypy, pytest).

- Run unit/integration tests (pytest):
  - Run all tests in the repository: ``pytest -q``
  - Run tests with verbose output: ``pytest -q -v``
  - Run tests with a concise summary: ``pytest -q --disable-warnings``
  - Run a single test function: ``pytest path/to/test_file.py::TestClassName::test_method_name -q``
  - Run a single test function (no class): ``pytest path/to/test_file.py::test_function_name -q``
  - Run tests matching a name pattern: ``pytest -k "pattern" -q`` (use carefully to avoid false positives)
  - Run tests for a specific module/file: ``pytest path/to/test_file.py -q``
  - Run tests with coverage: ``pytest --maxfail=1 --disable-warnings -q --cov=accounting_app --cov-report=term-missing``
  - Run only tests marked with a label: ``pytest -m unit`` or ``pytest -m integration``

- Flask app manual run (for dev/debug):
  - ``export FLASK_APP=accounting_app.app:app``
  - ``export FLASK_ENV=development``
  - ``flask run`` or ``python -m flask run``

- Linting and formatting:
  - Black (format): ``black .``
  - Isort (imports): ``isort .``
  - Flake8 (lint): ``flake8``
  - Type checking (optional, if configured): ``mypy accounting_app``

- Quick quick-check script (optional helper):
  - Create and run a tiny script that imports modules and runs a few bootstrap checks; e.g., import app factory, initialize DB

- Pre-commit hooks (optional):
  - Install: ``pre-commit install``
  - Run all checks on all files: ``pre-commit run --all-files``

> Note: Use the above commands in the project root. If the repo uses a different test layout, adjust paths accordingly.

---
## 2) Code style guidelines
### A. Imports
- Group order: standard library imports, third-party imports, local imports.
- Use absolute imports where possible; avoid circular imports.
- Separate groups with a blank line; avoid wildcard imports.
- Prefer explicit imports over ``from module import *``.

### B. Formatting
- Follow PEP 8 where feasible; wrap long lines to 120 chars when necessary (team preference may vary; prefer readability).
- Use 4 spaces per indentation level; no tabs.
- Keep functions small; aim for 15-40 lines per function where possible.
- Place type hints on parameters and return types; use typing.Optional/List/Dict as needed.

### C. Typing and docstrings
- Every public function, method, and class should have a docstring describing intent, inputs, and outputs.
- Use type hints for all public interfaces; include Optional when a value may be None.
- Use from __future__ import annotations if needed to reduce forward references (optional).

### D. Naming conventions
- Variables and functions: snake_case.
- Classes and exceptions: CamelCase.
- Constants: ALL_CAPS with underscores.
- File and module names: snake_case; package layout should reflect domain boundaries.

### E. Error handling
- Do not swallow exceptions; catch specific exceptions where needed.
- Prefer raising ValueError/TypeError for validation/math errors; avoid generic Exception.
- Propagate errors to caller when appropriate; include meaningful messages for users and logs.

### F. Logging and observability
- Use structured logging where possible (JSON payloads with context). See core/logging.py.
- Include request metadata (IP, path, method) and user context in logs when available.
- Avoid logging sensitive data.

### G. Architecture and safety
- Do not place business logic in routes; use services/repositories.
- Interact with DB via repositories/ORM, not raw SQL in routes.
- Ensure data validation happens before persistence; mirror domain rules in tests.

### H. Testing and determinism
- Tests should be isolated and deterministic; avoid time-dependent flakiness where possible.
- Provide fixtures for common objects; aim for at least 70% coverage as per project guidance.
- Name tests clearly: test_<function>_<scenario>, and provide docstrings for complex tests.

### I. Security practices
- Never store secrets in code; use environment vars or config files with proper access.
- CSRF protection enabled; sessions secure where applicable.
- Validate user input and sanitize outputs to prevent injection vulnerabilities.

---
## 3) Cursor and Copilot rules
- Cursor rules can be found at .cursor/rules/ and .cursorrules (if present). Follow those constraints when applying code edits or generating patches.
- Copilot guidance is documented in .github/copilot-instructions.md; respect those instructions when drafting code proposals or patches.
- Always verify changes by running unit tests and lint, and adjust patches before merging.

---
## 4) General workflow guidance
- When in doubt, prefer explicit, well-typed, well-documented code.
- Keep patches small and focused; propose one or two changes per PR to ease review.
- Document architectural decisions in code via docstrings and in a lightweight README if needed.
- If you modify core contracts (interfaces, models, or APIs), update related tests and API docs accordingly.


# VAS Accounting WebApp AI Agent Guide

## Project Overview

Build a **Vietnamese Accounting Web Application** that:

- Complies with **Vietnamese Accounting Standards (VAS)**
- Compatible with **Thông tư 99/2025/BTC**
- Runs **on-premise**
- Uses **Flask + SQLite**
- Supports **double-entry accounting**
- Includes **audit logs, reports, and financial statements**

The application must be designed with **enterprise-grade architecture and code quality**.

---

# 1. Technology Stack

Agents must strictly use the following technologies.

## Backend

- Python 3.12
- Flask
- SQLAlchemy ORM
- SQLite database
- Alembic migrations

## Frontend

- Jinja2 templates
- Bootstrap 5
- HTMX (optional)

## Reporting

- Pandas
- OpenPyXL
- PDF export

## Security

- Flask-Login
- Flask-WTF
- Werkzeug security

---

# 2. Deployment Model

The system must run **fully on-premise**.

Supported modes:

Development:

```

flask run

```

Production:

```

gunicorn app:app
nginx reverse proxy

```

Database:

```

SQLite

```

Future upgrade must support:

- PostgreSQL
- SQL Server
- Oracle

via SQLAlchemy.

---

# 3. Architecture Principles

Agents must follow **Clean Architecture**.

Layer structure:

```

Presentation Layer (Flask Routes)
↓
Application Services
↓
Domain Logic
↓
Repositories
↓
Database

```

Rules:

- No business logic inside routes
- Database access only via repositories
- Services implement business rules

---

# 4. Project Folder Structure

Agents must generate this structure.

```

accounting_app/
│
├── app.py
├── config.py
├── requirements.txt
│
├── core/
│   ├── database.py
│   ├── security.py
│   ├── logging.py
│
├── models/
│   ├── user.py
│   ├── account.py
│   ├── journal.py
│   ├── inventory.py
│
├── repositories/
│
├── services/
│
├── routes/
│   ├── auth_routes.py
│   ├── accounting_routes.py
│
├── templates/
│
├── static/
│
├── reports/
│
├── migrations/
│
└── tests/

```

---

# 5. Code Quality Requirements

Agents must enforce strict code quality.

Mandatory tools:

```

black
flake8
isort
mypy
pytest

````

Rules:

- Use **type hints**
- Follow **PEP8**
- Write **docstrings**
- Avoid duplicated code
- Keep functions small and readable

Example function style:

```python
def create_account(account_data: AccountCreateDTO) -> Account:
    """
    Create a new chart of account entry.
    """
````

---

# 6. Authentication Module

Implement secure authentication.

Features:

* Login
* Logout
* Session management
* Role-based access control

Roles:

```
Admin
Accountant
Auditor
Viewer
```

Tables:

```
users
roles
permissions
```

Security requirements:

* password hashing
* CSRF protection
* session expiration

---

# 7. Chart of Accounts Module

Implement Vietnamese standard **Chart of Accounts**.

Fields:

```
account_code
account_name
account_type
parent_account
normal_balance
is_active
```

Example accounts:

```
111 Cash
112 Bank
131 Accounts receivable
331 Accounts payable
511 Revenue
632 Cost of goods sold
642 Operating expense
911 Profit determination
```

Must support hierarchical structure.

---

# 8. Journal Voucher Module

Implement **double-entry accounting**.

Tables:

```
journal_vouchers
journal_entries
```

Voucher fields:

```
voucher_no
voucher_date
description
created_by
status
```

Journal entry fields:

```
account_id
debit
credit
cost_center
reference
```

Validation rule:

```
SUM(debit) == SUM(credit)
```

Agents must enforce this rule before saving.

---

# 9. General Ledger

Automatically generate ledger from journal entries.

Reports:

* General Ledger
* Trial Balance
* Account Statement

Queries must be optimized with indexes.

---

# 10. Financial Statements

Generate VAS-compliant reports.

## Balance Sheet

Sections:

```
Assets
Liabilities
Equity
```

## Income Statement

Sections:

```
Revenue
Expenses
Profit
```

## Cash Flow

Method:

```
Indirect Method
```

---

# 11. Inventory Module (Optional)

Support inventory tracking.

Tables:

```
items
warehouses
stock_transactions
```

Valuation methods:

```
FIFO
Weighted Average
```

---

# 12. Tax Reports

Basic Vietnamese tax reporting.

Reports:

```
VAT Input
VAT Output
VAT Declaration
```

---

# 13. Audit Logging

All important actions must be logged.

Table:

```
audit_logs
```

Fields:

```
user_id
action
entity
entity_id
timestamp
old_value
new_value
ip_address
```

Examples of logged events:

* login
* voucher creation
* voucher modification
* account creation

---

# 14. Logging System

Agents must implement structured logging.

Log levels:

```
INFO
WARNING
ERROR
CRITICAL
```

Log data must include:

```
timestamp
user
action
module
message
```

Logs must be written to:

```
logs/app.log
```

---

# 15. REST API Design

Even though the system uses server rendering, agents must expose REST APIs.

Example endpoints:

```
/api/v1/accounts
/api/v1/journal
/api/v1/reports
```

Standard API response format:

```json
{
  "status": "success",
  "data": {},
  "message": ""
}
```

---

# 16. Database Design Rules

Naming conventions:

* snake_case
* singular table names

Example tables:

```
users
accounts
journal_vouchers
journal_entries
items
stock_transactions
audit_logs
```

Requirements:

* primary keys
* foreign keys
* indexes

---

# 17. Testing Strategy

Agents must implement tests using **pytest**.

Minimum coverage:

```
70%
```

Test categories:

```
unit tests
integration tests
validation tests
```

Example test cases:

* journal balancing validation
* login authentication
* account creation
* financial report accuracy

---

# 18. Performance Guidelines

Even with SQLite, agents must optimize queries.

Best practices:

* use indexes
* avoid N+1 queries
* implement pagination
* cache heavy reports

---

# 19. Backup Strategy

Database backup must be supported.

Methods:

```
daily sqlite backup
manual export
scheduled cron backup
```

Backup file example:

```
backup/accounting_YYYYMMDD.db
```

---

# 20. AI Agent Rules

Agents must follow these rules.

## Allowed

* generate modular code
* add type hints
* add docstrings
* write unit tests
* validate accounting rules

## Forbidden

* hardcoded credentials
* skipping accounting validation
* mixing business logic with routes
* direct SQL in route handlers

---

# 21. Development Order

Agents must implement the system in this order.

Step 1

```
project skeleton
```

Step 2

```
database models
```

Step 3

```
authentication
```

Step 4

```
chart of accounts
```

Step 5

```
journal vouchers
```

Step 6

```
general ledger
```

Step 7

```
financial statements
```

Step 8

```
report export
```

---

# 22. Documentation

Agents must generate documentation.

Files required:

```
README.md
DATABASE_SCHEMA.md
API_DOCS.md
```

Documentation must include:

* system architecture
* database design
* API specification

---

# 23. Future Roadmap

The architecture must support future modules.

Possible upgrades:

* multi-company accounting
* ERP integration
* POS integration
* bank API integration
* e-invoice integration
* BI dashboards

```
# Deprecation Policy

- Deprecation warnings MUST NOT be ignored
- High-risk warnings MUST be fixed immediately
- All warnings must be tracked and resolved
```

