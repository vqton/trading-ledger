# VAS Accounting WebApp - Project Overview

**Version:** 2.0  
**Circular:** 99/2025/TT-BTC  
**Last Updated:** 2026-03-19

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Technology Stack](#2-technology-stack)
3. [Architecture](#3-architecture)
4. [Project Structure](#4-project-structure)
5. [Key Features](#5-key-features)
6. [Compliance](#6-compliance)
7. [Getting Started](#7-getting-started)
8. [Development Workflow](#8-development-workflow)

---

## 1. Project Overview

### 1.1 Purpose

The VAS Accounting WebApp is a comprehensive Vietnamese accounting system designed for small and medium enterprises (SMEs). It follows the Vietnamese Accounting Standards (VAS) as specified in **Circular 99/2025/TT-BTC**, effective January 1, 2026.

### 1.2 Key Objectives

- **Compliance**: Full compliance with Vietnamese accounting regulations
- **Double-Entry Accounting**: Strict double-entry bookkeeping with validation
- **Financial Reporting**: VAS-compliant financial statements (B01-B05)
- **On-Premise Deployment**: Secure, self-hosted solution
- **User-Friendly Interface**: Modern web-based UI with Bootstrap 5

### 1.3 Target Users

| Role | Description | Permissions |
|------|-------------|-------------|
| Administrator | System administration | Full access |
| Accountant | Daily accounting operations | CRUD vouchers, reports |
| Auditor | Financial review | Read-only access |
| Viewer | Management reporting | Read-only reports |

### 1.4 Project Statistics

```
Total Lines of Code: ~15,000+
Models: 30+
Services: 15+
Routes: 50+
Templates: 40+
Test Coverage: ~60%
```

---

## 2. Technology Stack

### 2.1 Backend

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.12 | Core language |
| Flask | 3.0+ | Web framework |
| SQLAlchemy | 2.0+ | ORM |
| SQLite | 3.x | Database |

### 2.2 Frontend

| Technology | Version | Purpose |
|------------|---------|---------|
| Bootstrap | 5.x | UI framework |
| Jinja2 | - | Template engine |
| Font Awesome | 6.x | Icons |
| Chart.js | 4.x | Charts |

### 2.3 Development Tools

| Tool | Purpose |
|------|---------|
| pytest | Testing |
| black | Code formatting |
| flake8 | Linting |
| mypy | Type checking |

---

## 3. Architecture

### 3.1 Clean Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                       │
│  Routes (Flask Blueprints) → Templates (Jinja2) → HTML/CSS  │
├─────────────────────────────────────────────────────────────┤
│                   APPLICATION LAYER                         │
│  Services (Business Logic) → Forms (Validation)              │
├─────────────────────────────────────────────────────────────┤
│                      DOMAIN LAYER                            │
│  Models (Entities) → Enums → Value Objects                  │
├─────────────────────────────────────────────────────────────┤
│                 INFRASTRUCTURE LAYER                         │
│  Repositories (Data Access) → Database (SQLAlchemy)         │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Data Flow

```
User Request
    ↓
Route Handler
    ↓
Service (Business Logic)
    ↓
Repository (Data Access)
    ↓
Database (SQLite)
    ↓
Response (HTML/JSON)
```

### 3.3 Design Patterns

| Pattern | Usage |
|---------|-------|
| Factory Pattern | Application factory (`create_app`) |
| Repository Pattern | Data access abstraction |
| Service Layer | Business logic encapsulation |
| Dependency Injection | Flask extensions |

---

## 4. Project Structure

### 4.1 Directory Structure

```
accounting_app/
│
├── app.py                      # Application factory
├── config.py                   # Configuration
├── requirements.txt            # Dependencies
│
├── core/                       # Core utilities
│   ├── database.py            # SQLAlchemy setup
│   ├── security.py            # Authentication/Authorization
│   ├── logging.py             # Logging configuration
│   ├── rbac.py                # Role-based access control
│   └── utils.py               # Utility functions
│
├── models/                     # Domain models
│   ├── __init__.py            # Model exports
│   ├── account.py             # Chart of Accounts
│   ├── journal.py             # Journal Vouchers
│   ├── audit_log.py           # Audit Trail
│   ├── partner.py             # Customer/Vendor/Employee
│   ├── inventory.py           # Inventory Management
│   ├── fixed_asset.py          # Fixed Assets
│   ├── bank.py                # Banking
│   ├── budget.py               # Budget Management
│   ├── currency.py            # Currency/FX
│   ├── cost_center.py          # Cost Centers
│   ├── project.py             # Projects
│   ├── tax_policy.py          # Tax Policies
│   ├── tax_payment.py         # Tax Payments
│   ├── opening_balance.py      # Opening Balances
│   ├── biological_asset.py     # TK 215 - NEW TT99
│   ├── dividend_payable.py    # TK 332 - NEW TT99
│   ├── supporting_document.py  # Document Attachments
│   ├── approval_workflow.py    # Approval Workflows
│   ├── document.py            # Document Management
│   ├── notification.py        # Notifications
│   ├── system_setting.py      # System Settings
│   ├── backup.py              # Backup Management
│   └── seed_data.py           # Initial data
│
├── repositories/              # Data access layer
│   ├── __init__.py
│   ├── account_repository.py
│   ├── journal_repository.py
│   ├── ledger_repository.py
│   ├── financial_report_repository.py
│   ├── partner_repository.py
│   ├── cost_center_repository.py
│   ├── project_repository.py
│   ├── tax_repository.py
│   ├── tax_payment_repository.py
│   ├── approval_repository.py  # NEW
│   ├── document_repository.py  # NEW
│   ├── notification_repository.py  # NEW
│   ├── system_setting_repository.py  # NEW
│   └── backup_repository.py    # NEW
│
├── services/                   # Business logic layer
│   ├── __init__.py
│   ├── coa_engine.py          # Chart of Accounts
│   ├── account_service.py     # Account operations
│   ├── journal_service.py     # Journal processing
│   ├── ledger_service.py      # Ledger generation
│   ├── financial_report_service.py  # Financial reports
│   ├── partner_service.py     # Partner management
│   ├── tax_engine.py          # Tax calculation
│   ├── tax_service.py         # Tax operations
│   ├── cost_center_service.py  # Cost center management
│   ├── project_service.py     # Project management
│   ├── tax_payment_service.py # Tax payment tracking
│   ├── period_service.py      # Accounting periods
│   ├── voucher_numbering_service.py  # Voucher numbering
│   ├── voucher_template_service.py   # Voucher templates
│   ├── bank_service.py        # Banking operations
│   ├── budget_service.py       # Budget management
│   ├── currency_service.py    # Currency operations
│   ├── fixed_asset_service.py # Fixed asset management
│   └── inventory_service.py   # Inventory management
│
├── routes/                     # Presentation layer
│   ├── __init__.py
│   ├── auth_routes.py         # Authentication
│   ├── accounting_routes.py  # Journal/COA
│   ├── financial_routes.py    # Reports
│   ├── partner_routes.py      # Customer/Vendor
│   ├── tax_routes.py         # Tax
│   ├── cost_center_routes.py  # Cost Centers
│   ├── project_routes.py      # Projects
│   └── tax_payment_routes.py # Tax Payments
│
├── forms/                      # Form validation
│   ├── __init__.py
│   ├── auth_forms.py         # Auth forms
│   ├── account_forms.py      # Account forms
│   └── journal_forms.py      # Journal forms
│
├── templates/                  # Jinja2 templates
│   ├── base.html              # Base template
│   ├── index.html             # Dashboard
│   ├── auth/                  # Auth templates
│   │   ├── login.html
│   │   └── register.html
│   ├── accounting/           # Accounting templates
│   │   ├── accounts/
│   │   ├── journals/
│   │   ├── ledger/
│   │   └── reports/
│   ├── partners/             # Partner templates
│   │   ├── customers/
│   │   ├── vendors/
│   │   └── employees/
│   ├── tax/                  # Tax templates
│   ├── cost_centers/         # Cost center templates
│   ├── projects/             # Project templates
│   └── tax_payments/         # Tax payment templates
│
├── static/                    # Static files
│   ├── css/                  # Stylesheets
│   ├── js/                   # JavaScript
│   └── images/               # Images
│
├── reports/                   # Report generation
│   ├── pdf_exporter.py       # PDF export
│   └── excel_exporter.py     # Excel export
│
├── migrations/               # Database migrations
│
├── instance/                 # Instance-specific files
│   └── accounting.db         # SQLite database
│
└── tests/                    # Test suite
    ├── conftest.py          # Pytest fixtures
    ├── test_accounts.py     # Account tests
    ├── test_journal.py      # Journal tests
    ├── test_ledger.py       # Ledger tests
    ├── test_financial_reports.py  # Report tests
    ├── test_auth.py         # Auth tests
    ├── test_integration.py  # Integration tests
    └── ...
```

### 4.2 Key Files Description

| File | Purpose |
|------|---------|
| `app.py` | Flask application factory |
| `config.py` | Environment configuration |
| `models/__init__.py` | All model exports |
| `core/database.py` | SQLAlchemy engine/session |
| `core/security.py` | User auth and RBAC |
| `core/logging.py` | Structured logging |

---

## 5. Key Features

### 5.1 Core Accounting

| Feature | Description |
|---------|-------------|
| Chart of Accounts | 71 Level 1 accounts per TT99 |
| Journal Vouchers | Double-entry with validation |
| General Ledger | Real-time ledger generation |
| Trial Balance | Period-end balancing |
| Accounting Periods | Monthly/Quarterly/Annual |

### 5.2 Financial Reporting

| Report | Form | Status |
|--------|------|--------|
| Balance Sheet | B01-DN | ✅ |
| Income Statement | B02-DN | ✅ |
| Cash Flow | B03-DN | ✅ |
| Trial Balance | - | ✅ |
| Account Statement | - | ✅ |
| Notes to FS | B05-DN | ✅ |

### 5.3 Subledger Management

| Module | Account | Status |
|--------|---------|--------|
| Customer Management | TK 131 | ✅ |
| Vendor Management | TK 331 | ✅ |
| Employee Management | TK 141, 334 | ✅ |
| Inventory | TK 151-158 | ✅ |
| Fixed Assets | TK 211-214 | ✅ |
| Bank Accounts | TK 112, 341 | ✅ |

### 5.4 Tax Management

| Tax Type | Account | Status |
|----------|---------|--------|
| VAT | TK 3331 | ✅ |
| Corporate Income Tax | TK 3332 | ✅ |
| Personal Income Tax | TK 3335 | ✅ |
| Import Duty | TK 3333 | ✅ |
| Pillar 2 Tax | TK 82112 | ✅ |

### 5.5 New TT99 Accounts

| Code | Name | Status |
|------|------|--------|
| TK 215 | Tài sản sinh học | ✅ |
| TK 332 | Phải trả cổ tức | ✅ |
| TK 82112 | Thuế TNDN bổ sung | ✅ |

---

## 6. Compliance

### 6.1 Circular 99/2025/TT-BTC

| Requirement | Implementation |
|-------------|----------------|
| 71 TK Level 1 | ✅ 71 accounts seeded |
| New TK 215 | ✅ Biological Assets |
| New TK 332 | ✅ Dividend Payable |
| New TK 82112 | ✅ Pillar 2 Tax |
| Renamed TK 155 | ✅ "Thành phẩm" → "Sản phẩm" |
| B01-DN Format | ✅ Balance Sheet |
| B02-DN Format | ✅ Income Statement |
| B03-DN Format | ✅ Cash Flow (Indirect) |

### 6.2 Data Integrity

- **Double-Entry Validation**: `SUM(debits) == SUM(credits)`
- **Foreign Key Constraints**: Database-level referential integrity
- **Audit Trail**: All changes logged with user, timestamp, IP
- **ACID Transactions**: SQLite with WAL mode

---

## 7. Getting Started

### 7.1 Prerequisites

```bash
Python 3.12+
pip
git
```

### 7.2 Installation

```bash
# Clone repository
git clone <repository-url>
cd /mnt/e/acct

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest -q

# Start application
flask run
```

### 7.3 Default Credentials

| Username | Password | Role |
|----------|----------|------|
| admin | admin123 | Administrator |

### 7.4 Configuration

```bash
# Environment variables
export FLASK_ENV=development
export FLASK_APP=accounting_app.app:app
export SECRET_KEY=your-secret-key
```

---

## 8. Development Workflow

### 8.1 Adding a New Model

```
1. Create model in models/
2. Export in models/__init__.py
3. Create repository in repositories/
4. Create service in services/
5. Create routes in routes/
6. Create templates in templates/
7. Register blueprint in app.py
8. Add navigation in base.html
9. Write tests
10. Run linting and tests
```

### 8.2 Testing

```bash
# Run all tests
pytest -q

# Run with coverage
pytest --cov=accounting_app --cov-report=term-missing

# Run specific test
pytest tests/test_accounts.py -q
```

### 8.3 Code Quality

```bash
# Format code
black .

# Sort imports
isort .

# Lint
flake8

# Type check
mypy accounting_app
```

### 8.4 Database Management

```bash
# Delete and recreate database
rm accounting_app/instance/accounting.db

# Run tests (will recreate)
pytest -q
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-03-17 | Initial project structure |
| 2.0 | 2026-03-19 | Added advanced models (M13-M14) |

---

**Document Status:** Active  
**Next Review:** Weekly
