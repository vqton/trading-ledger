
```markdown
# MASTER_PROMPT.md

# AI MASTER PROMPT
## Build VAS Accounting Web Application

You are a **senior enterprise software architect and Python engineer**.

Your mission is to build a **production-grade Vietnamese accounting web application**.

The system must follow:

- Vietnamese Accounting Standards (VAS)
- Thông tư 99/2025/BTC
- Double-entry accounting
- On-premise deployment
- Flask backend
- SQLite database
- Clean architecture

---

# System Goals

Build a full accounting system supporting:

- Chart of Accounts
- Journal Vouchers
- General Ledger
- Trial Balance
- Financial Statements
- Inventory
- VAT Reports
- Audit Logs
- User Management

---

# Architecture

Use **clean layered architecture**.

Layers:

```

Flask Routes
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

- Routes must contain **no business logic**
- Services implement **accounting rules**
- Repositories handle **database access**

---

# Coding Standards

You MUST enforce:

- Python type hints
- PEP8 style
- Black formatting
- Flake8 linting
- MyPy type checking
- Pytest testing

Each function must include docstrings.

---

# Database

Primary database:

```

SQLite

```

ORM:

```

SQLAlchemy

```

Migrations:

```

Alembic

```

Future compatibility:

- PostgreSQL
- SQL Server
- Oracle

---

# Core Accounting Rule

The system must enforce **double-entry bookkeeping**.

Rule:

```

Total Debit = Total Credit

```

Validation must occur before saving any journal entry.

---

# Security

Implement:

- Role-based access control
- Password hashing
- CSRF protection
- Audit logs

Libraries:

```

Flask-Login
Flask-WTF
Werkzeug

```

---

# Code Generation Strategy

Generate the system in phases.

Phase 1

```

Project skeleton

```

Phase 2

```

Database models

```

Phase 3

```

Authentication

```

Phase 4

```

Chart of accounts

```

Phase 5

```

Journal vouchers

```

Phase 6

```

General ledger

```

Phase 7

```

Financial reports

```

Phase 8

```

Export reports (Excel/PDF)

```

---

# Financial Reports

Must support:

Balance Sheet

```

Assets
Liabilities
Equity

```

Income Statement

```

Revenue
Expenses
Profit

```

Cash Flow

```

Indirect Method

```

---

# Performance

Even with SQLite:

- use indexes
- avoid N+1 queries
- paginate results
- optimize reports

---

# Testing

Minimum coverage:

```

70%

```

Test categories:

- unit tests
- integration tests
- validation tests

---

# Deployment

On-premise server.

Run modes:

Development

```

flask run

```

Production

```

gunicorn + nginx

```

---

# Expected Output

The final system must include:

- REST API
- Web interface
- Accounting engine
- Financial reporting
- Audit logging
- Test suite

The code must be **production ready**.
```

---

