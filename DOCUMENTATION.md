# VAS Accounting Web Application - Documentation

## Project Overview

A Vietnamese Accounting Web Application complying with:
- Vietnamese Accounting Standards (VAS)
- Thông tư 99/2025/BTC
- Double-entry bookkeeping
- On-premise deployment

**Technology Stack:**
- Python 3.12
- Flask + SQLAlchemy
- SQLite database
- Jinja2 + Bootstrap 5

---

## Development Phases

### Phase 1: Project Skeleton

**Purpose:** Create project foundation and folder structure.

**Files Created:**
```
accounting_app/
├── app.py                 # Flask application factory
├── config.py              # Configuration management
├── requirements.txt       # Dependencies
├── core/
│   ├── database.py       # SQLAlchemy initialization
│   ├── security.py      # User, Role, Permission models
│   └── logging.py        # Structured logging
├── models/              # Database models (empty)
├── repositories/        # Data access layer
├── services/           # Business logic
├── routes/             # Flask blueprints
├── templates/          # Jinja2 templates
├── static/            # CSS, JS, images
├── reports/           # Export utilities
├── migrations/        # Alembic migrations
├── tests/             # Pytest tests
├── logs/              # Application logs
└── backup/            # Database backups
```

---

### Phase 2: Database Models

**Purpose:** Define all database models with relationships.

**Models Created:**
| Model | File | Description |
|-------|------|-------------|
| `Account` | `models/account.py` | Chart of Accounts |
| `JournalVoucher` | `models/journal.py` | Voucher header |
| `JournalEntry` | `models/journal.py` | Debit/Credit lines |
| `AuditLog` | `models/audit_log.py` | System audit trail |
| `Warehouse` | `models/inventory.py` | Inventory locations |
| `InventoryItem` | `models/inventory.py` | Stock items |
| `StockTransaction` | `models/inventory.py` | Stock movements |
| `InventoryBatch` | `models/inventory.py` | FIFO/Specific batches |

**Inventory Valuation Methods:**
- FIFO (First In, First Out)
- Weighted Average
- Specific Identification

**Seed Data:**
- Vietnamese Standard Chart of Accounts (60+ accounts)
- Account types: Asset, Liability, Equity, Revenue, Expense

---

### Phase 3: Authentication

**Purpose:** User authentication and role-based access control.

**Files Created:**
```
forms/
├── auth_forms.py       # LoginForm, ChangePasswordForm, UserForm

core/
└── rbac.py            # permission_required, admin_required decorators
```

**Features:**
- Login/Logout with session management
- Remember me functionality
- CSRF protection via Flask-WTF
- Password hashing with Werkzeug

**Roles:**
| Role | Permissions |
|------|-------------|
| Admin | Full access (create, read, update, delete) |
| Accountant | account, journal, report, inventory (CRU) |
| Auditor | account, journal, report (read only) |
| Viewer | account, journal, report (read only) |

**Default Login:** `admin` / `admin123`

---

### Phase 4: Chart of Accounts

**Purpose:** Manage Vietnamese standard chart of accounts.

**Files Created:**
```
repositories/
└── account_repository.py   # Account CRUD operations

services/
└── account_service.py     # Business logic, validation

forms/
└── account_forms.py       # AccountForm WTForms
```

**Features:**
- Hierarchical account structure (parent-child)
- Account types: Asset, Liability, Equity, Revenue, Expense
- Normal balance (Debit/Credit)
- Soft delete with validation
- Audit logging

**Routes:**
- `GET /accounting/accounts` - List accounts
- `GET/POST /accounting/accounts/create` - Create account
- `GET/POST /accounting/accounts/<id>/edit` - Edit account
- `POST /accounting/accounts/<id>/delete` - Delete account

**Validation Rules:**
- Account code must be unique
- Parent account must be summary (not detail)
- Cannot change code/type if has transactions
- Cannot delete with children or transactions

---

### Phase 5: Journal Vouchers

**Purpose:** Double-entry accounting with voucher management.

**Files Created:**
```
repositories/
└── journal_repository.py   # Journal CRUD

services/
└── journal_service.py      # Double-entry validation

forms/
└── journal_forms.py        # VoucherForm
```

**Core Validation Rule:**
```
SUM(debit) == SUM(credit)
```

**Voucher Lifecycle:**
```
Draft → Posted → Locked
```

**Voucher Types:**
- General (Chứng từ chung)
- Cash Receipt (Thu tiền)
- Cash Payment (Chi tiền)
- Bank Receipt (Thu ngân hàng)
- Bank Payment (Chi ngân hàng)
- Purchase (Mua hàng)
- Sales (Bán hàng)

**Routes:**
- `GET /accounting/journal` - List vouchers
- `GET/POST /accounting/journal/create` - Create voucher
- `GET /accounting/journal/<id>` - View voucher
- `GET/POST /accounting/journal/<id>/edit` - Edit draft
- `POST /accounting/journal/<id>/post` - Post to ledger
- `POST /accounting/journal/<id>/unpost` - Unpost voucher

---

### Phase 6: General Ledger

**Purpose:** Generate ledger reports from posted entries.

**Files Created:**
```
repositories/
└── ledger_repository.py   # Optimized ledger queries

services/
└── ledger_service.py      # Balance calculation
```

**Features:**
- Account-specific ledger with running balance
- Trial Balance report
- General Ledger (all accounts)
- Opening/Closing balance calculation

**Balance Calculation:**
```
If normal_balance = debit:
  Balance = Opening + Debit - Credit
  
If normal_balance = credit:
  Balance = Opening + Credit - Debit
```

**Routes:**
- `GET /accounting/ledger` - Ledger home
- `GET /accounting/ledger/account/<id>` - Account detail
- `GET /accounting/ledger/trial-balance` - Trial Balance
- `GET /accounting/ledger/general` - General Ledger

---

### Phase 7: Financial Statements

**Purpose:** Generate VAS-compliant financial reports.

**Files Created:**
```
repositories/
└── financial_report_repository.py   # Report queries

services/
└── financial_report_service.py      # Report generation
```

**Reports:**
| Report | Formula |
|--------|---------|
| Balance Sheet | Assets = Liabilities + Equity |
| Income Statement | Revenue - Expenses = Profit |
| Cash Flow | Indirect Method |

**Routes:**
- `GET /accounting/reports` - Reports home
- `GET /accounting/reports/balance-sheet` - Balance Sheet
- `GET /accounting/reports/income-statement` - Income Statement
- `GET /accounting/reports/cash-flow` - Cash Flow

---

### Phase 8: Export Reports

**Purpose:** Export reports to Excel and PDF.

**Files Created:**
```
reports/
├── excel_exporter.py   # Excel export (openpyxl)
└── pdf_exporter.py     # PDF export (reportlab)
```

**Export Routes:**

| Report | Excel | PDF |
|--------|-------|-----|
| Trial Balance | `/reports/trial-balance/export/excel` | `/reports/trial-balance/export/pdf` |
| Balance Sheet | `/reports/balance-sheet/export/excel` | `/reports/balance-sheet/export/pdf` |
| Income Statement | `/reports/income-statement/export/excel` | `/reports/income-statement/export/pdf` |
| Journal Voucher | `/journal/<id>/export/excel` | `/journal/<id>/export/pdf` |

**Export Features:**
- Vietnamese number formatting (#,##0)
- Professional styling
- Automatic filename with date

---

## Project Structure

```
accounting_app/
├── app.py
├── config.py
├── requirements.txt
│
├── core/
│   ├── __init__.py
│   ├── database.py
│   ├── security.py
│   ├── logging.py
│   └── rbac.py
│
├── models/
│   ├── __init__.py
│   ├── account.py
│   ├── journal.py
│   ├── audit_log.py
│   ├── inventory.py
│   └── seed_data.py
│
├── repositories/
│   ├── __init__.py
│   ├── account_repository.py
│   ├── journal_repository.py
│   ├── ledger_repository.py
│   └── financial_report_repository.py
│
├── services/
│   ├── __init__.py
│   ├── account_service.py
│   ├── journal_service.py
│   ├── ledger_service.py
│   └── financial_report_service.py
│
├── forms/
│   ├── __init__.py
│   ├── auth_forms.py
│   ├── account_forms.py
│   └── journal_forms.py
│
├── routes/
│   ├── __init__.py
│   ├── auth_routes.py
│   └── accounting_routes.py
│
├── reports/
│   ├── __init__.py
│   ├── excel_exporter.py
│   └── pdf_exporter.py
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── auth/
│   │   ├── login.html
│   │   ├── change_password.html
│   │   ├── users.html
│   │   ├── user_form.html
│   │   └── roles.html
│   └── accounting/
│       ├── accounts.html
│       ├── account_form.html
│       ├── journal.html
│       ├── voucher_form.html
│       ├── voucher_view.html
│       ├── ledger.html
│       ├── ledger_detail.html
│       ├── trial_balance.html
│       ├── general_ledger.html
│       ├── balance_sheet.html
│       ├── income_statement.html
│       ├── cash_flow.html
│       └── reports.html
│
├── migrations/
├── tests/
├── logs/
└── backup/
```

---

## Running the Application

### Development
```bash
cd accounting_app
pip install -r requirements.txt
flask run
```

### Production
```bash
gunicorn app:app
```

### Default Login
- Username: `admin`
- Password: `admin123`

---

## Code Quality

**Tools Required:**
- black (formatting)
- flake8 (linting)
- isort (imports)
- mypy (type checking)
- pytest (testing)

**Coverage Target:** 70%

---

## Future Enhancements

- Multi-company accounting
- PostgreSQL/SQL Server support
- REST API endpoints
- E-invoice integration
- BI Dashboards
