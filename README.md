# VAS Accounting WebApp

**Vietnamese Accounting System compliant with Circular 99/2025/TT-BTC**

![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## Overview

VAS Accounting WebApp is a comprehensive Vietnamese accounting system designed for small and medium enterprises (SMEs). It follows the Vietnamese Accounting Standards (VAS) as specified in **Circular 99/2025/TT-BTC**, effective January 1, 2026.

### Key Features

- ✅ **Double-Entry Accounting**: Strict double-entry bookkeeping with validation
- ✅ **Chart of Accounts**: 71 accounts per Circular 99/2025/TT-BTC
- ✅ **Financial Reports**: Balance Sheet (B01), Income Statement (B02), Cash Flow (B03)
- ✅ **Tax Compliance**: VAT, CIT, PIT, Pillar 2 (TK 82112)
- ✅ **Partner Management**: Customer, Vendor, Employee subledgers
- ✅ **Cost Centers & Projects**: Budget tracking and allocation
- ✅ **On-Premise Deployment**: Secure, self-hosted solution

### New in Circular 99/2025/TT-BTC

| Account | Description |
|---------|-------------|
| TK 215 | Tài sản sinh học (Biological Assets) |
| TK 332 | Phải trả cổ tức (Dividend Payable) |
| TK 82112 | Thuế TNDN bổ sung (Pillar 2 - Global Minimum Tax) |

---

## Quick Start

### Prerequisites

- Python 3.12+
- pip
- git

### Installation

```bash
# Clone repository
git clone <repository-url>
cd /mnt/e/acct

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r accounting_app/requirements.txt

# Run tests
cd accounting_app && pytest -q

# Start application
flask run
```

### Default Login

```
Username: admin
Password: admin123
```

---

## Project Structure

```
accounting_app/
├── app.py                 # Application factory
├── config.py              # Configuration
├── requirements.txt       # Dependencies
│
├── core/                  # Core utilities
│   ├── database.py        # SQLAlchemy setup
│   ├── security.py        # Authentication
│   ├── logging.py         # Logging
│   └── rbac.py            # RBAC
│
├── models/                # Domain models (30+)
├── repositories/          # Data access layer
├── services/              # Business logic layer
├── routes/                # API routes
├── forms/                 # Form validation
├── templates/             # Jinja2 templates
├── static/                # Static files
├── reports/               # Report generation
│
└── tests/                 # Test suite
```

---

## Features

### Core Accounting

| Module | Status | Description |
|--------|--------|-------------|
| Chart of Accounts | ✅ | 71 accounts per TT99 |
| Journal Vouchers | ✅ | Double-entry with validation |
| General Ledger | ✅ | Real-time ledger generation |
| Trial Balance | ✅ | Period-end balancing |

### Financial Reports

| Report | Form | Status |
|--------|------|--------|
| Balance Sheet | B01-DN | ✅ |
| Income Statement | B02-DN | ✅ |
| Cash Flow | B03-DN | ✅ |
| Trial Balance | - | ✅ |
| Notes to FS | B05-DN | ✅ |

### Subledger Management

| Module | Account | Status |
|--------|---------|--------|
| Customer | TK 131 | ✅ |
| Vendor | TK 331 | ✅ |
| Employee | TK 141, 334 | ✅ |

### Tax Management

| Tax Type | Account | Status |
|----------|---------|--------|
| VAT | TK 3331 | ✅ |
| CIT | TK 3332 | ✅ |
| PIT | TK 3335 | ✅ |
| Pillar 2 | TK 82112 | ✅ |

---

## Documentation

| Document | Description |
|----------|-------------|
| [MILESTONES.md](docs/MILESTONES.md) | Project milestones |
| [PROJECT_OVERVIEW.md](docs/PROJECT_OVERVIEW.md) | Architecture and tech stack |
| [DATABASE_SCHEMA.md](docs/DATABASE_SCHEMA.md) | Database schema |
| [API_DOCS.md](docs/API_DOCS.md) | API documentation |
| [USER_GUIDE.md](docs/USER_GUIDE.md) | User guide |
| [IMPLEMENTATION_STATUS.md](docs/IMPLEMENTATION_STATUS.md) | Implementation status |
| [roadmap.md](docs/roadmap.md) | Project roadmap |

---

## Technology Stack

### Backend

- **Python 3.12+**: Core language
- **Flask 3.0+**: Web framework
- **SQLAlchemy 2.0+**: ORM
- **SQLite**: Database

### Frontend

- **Bootstrap 5**: UI framework
- **Jinja2**: Template engine
- **Font Awesome 6**: Icons

### Development

- **pytest**: Testing
- **black**: Code formatting
- **flake8**: Linting
- **mypy**: Type checking

---

## Testing

```bash
# Run all tests
pytest -q

# Run with coverage
pytest --cov=accounting_app --cov-report=term-missing

# Run specific test
pytest tests/test_accounts.py -q
```

---

## Configuration

### Environment Variables

```bash
export FLASK_ENV=development
export FLASK_APP=accounting_app.app:app
export SECRET_KEY=your-secret-key
```

### Database

The database is located at:
```
accounting_app/instance/accounting.db
```

To reset:
```bash
rm accounting_app/instance/accounting.db
pytest -q
```

---

## Development

### Code Quality

```bash
# Format code
black accounting_app

# Sort imports
isort accounting_app

# Lint
flake8 accounting_app

# Type check
mypy accounting_app
```

### Adding New Models

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
```

---

## Compliance

### Circular 99/2025/TT-BTC

This application is designed to comply with Circular 99/2025/TT-BTC, which:
- Updates the Chart of Accounts from 76 to 71 accounts
- Adds new accounts: TK 215, TK 332, TK 82112
- Updates financial statement formats
- Effective date: January 1, 2026

### VAS Compliance

All features follow Vietnamese Accounting Standards (VAS):
- Double-entry bookkeeping
- Accrual accounting
- Historical cost principle
- Going concern assumption

---

## License

MIT License

---

## Support

For issues and questions:
- Open an issue on GitHub
- Email: support@example.com

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0 | 2026-03-19 | Added TT99 accounts, advanced models |
| 1.0 | 2026-03-17 | Initial release |

---

**Maintained by:** VAS Accounting Team  
**Documentation:** [docs/](docs/)
