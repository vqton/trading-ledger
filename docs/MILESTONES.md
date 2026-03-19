# VAS Accounting WebApp - Milestones

**Version:** 2.0  
**Circular:** 99/2025/TT-BTC  
**Last Updated:** 2026-03-19

---

## Overview

This document tracks all milestones achieved in the VAS Accounting WebApp project. Each milestone represents a significant phase of development.

---

## Milestone Status Summary

```
┌────────────────────────────────────────┬─────────────────────────────┐
│ Milestone                              │ Status                      │
├────────────────────────────────────────┼─────────────────────────────┤
│ M1: Project Foundation                 │ ✅ COMPLETE                 │
│ M2: Authentication & Security          │ ✅ COMPLETE                 │
│ M3: Core Accounting Engine (COA+JV)    │ ✅ COMPLETE                 │
│ M4: Partner Management (Customer/Vendor)│ ✅ COMPLETE                │
│ M5: Tax Engine                         │ ✅ COMPLETE                 │
│ M6: Cost Center & Project Management   │ ✅ COMPLETE                 │
│ M7: Tax Payment Management             │ ✅ COMPLETE                 │
│ M8: Financial Reports Engine           │ ✅ COMPLETE                 │
│ M9: Supporting Document Management     │ ✅ COMPLETE                 │
│ M10: Opening Balance Management        │ ✅ COMPLETE                 │
│ M11: Biological Asset Management       │ ✅ COMPLETE                 │
│ M12: Dividend Payable Management       │ ✅ COMPLETE                 │
│ M13: Advanced Models (Phase 1)         │ ✅ COMPLETE                 │
│ M14: Advanced Repositories             │ ✅ COMPLETE                 │
│ M15: Advanced Services                 │ 🔄 IN PROGRESS             │
│ M16: Advanced Routes & Templates       │ 📋 PENDING                 │
│ M17: Advanced Features (Notifications, Settings, Backup) │ 📋 PENDING │
│ M18: Testing & QA                      │ 📋 PENDING                 │
│ M19: Documentation & Deployment        │ 📋 PENDING                 │
└────────────────────────────────────────┴─────────────────────────────┘
```

---

## ✅ M1: Project Foundation

**Completed:** 2026-03-17  
**Duration:** 1 day

### Objectives Achieved

- [x] Flask application factory pattern
- [x] SQLAlchemy ORM setup with SQLite
- [x] Core configuration management
- [x] Basic folder structure
- [x] Git repository initialization

### Deliverables

```
accounting_app/
├── app.py              # Flask application factory
├── config.py           # Configuration management
├── requirements.txt    # Python dependencies
├── core/
│   ├── database.py     # SQLAlchemy setup
│   ├── security.py     # User authentication
│   └── logging.py      # Logging configuration
└── tests/              # Test infrastructure
```

### Git Commit

```
e6f3777 first commit
```

---

## ✅ M2: Authentication & Security

**Completed:** 2026-03-17  
**Duration:** 1 day

### Objectives Achieved

- [x] User model with password hashing (Werkzeug)
- [x] Role-based access control (RBAC)
- [x] Permission system
- [x] Session management
- [x] CSRF protection
- [x] Login/Logout functionality
- [x] Default admin user creation

### Models Implemented

| Model | Description | Status |
|-------|-------------|--------|
| User | User accounts with hashed passwords | ✅ |
| Role | User roles (Admin, Accountant, Auditor, Viewer) | ✅ |
| Permission | Granular permissions per module | ✅ |

### Routes Implemented

| Route | Function | Status |
|-------|----------|--------|
| /auth/login | User login | ✅ |
| /auth/logout | User logout | ✅ |
| /auth/register | User registration | ✅ |
| /auth/profile | User profile | ✅ |
| /auth/users | User management (Admin) | ✅ |

### Git Commits

```
6abcd83 feat: Implement Priority 1 models - Partner, Tax Engine, CostCenter
```

---

## ✅ M3: Core Accounting Engine (COA + Journal Voucher)

**Completed:** 2026-03-17 - 2026-03-18  
**Duration:** 2 days

### Objectives Achieved

- [x] Chart of Accounts (COA) with 71 accounts per TT99
- [x] Journal Voucher system with double-entry validation
- [x] Account types (Asset, Liability, Equity, Revenue, Expense)
- [x] Normal balance tracking
- [x] Hierarchical account structure
- [x] Voucher numbering service
- [x] Voucher templates
- [x] Accounting period management
- [x] Audit logging for all operations

### Models Implemented

| Model | Description | Tables |
|-------|-------------|--------|
| Account | Chart of accounts with TT99 codes | accounts |
| JournalVoucher | Header for voucher transactions | journal_vouchers |
| JournalEntry | Individual debit/credit lines | journal_entries |
| AccountingPeriod | Fiscal year and periods | accounting_periods |
| AuditLog | All changes tracked | audit_logs |

### Key Features

- **Double-Entry Validation**: `SUM(debits) == SUM(credits)`
- **Account Balance Calculation**: Real-time balance updates
- **Voucher Workflow**: Draft → Posted → Approved
- **Circular 99/TT-BTC Compliance**: 71 Level 1 accounts

### Test Coverage

| Test Suite | Tests | Status |
|------------|-------|--------|
| Account Tests | 79 | ✅ PASS |
| Journal Tests | 27 | ✅ PASS |
| Ledger Tests | 7 | ✅ PASS |

### Git Commits

```
5d1e820 feat: Implement COA Engine - centralized Chart of Accounts validation
8eb3b94 feat: Add SupportingDocument model for voucher attachments
5b28bb5 feat: Add OpeningBalance model for fiscal year opening balances
```

---

## ✅ M4: Partner Management (Customer/Vendor)

**Completed:** 2026-03-18  
**Duration:** 1 day

### Objectives Achieved

- [x] Customer master data management
- [x] Vendor master data management
- [x] Employee management
- [x] Partner relationship with journal entries
- [x] AR/AP aging reports
- [x] Credit limit tracking
- [x] Payment terms management

### Models Implemented

| Model | Description | Tables |
|-------|-------------|--------|
| Customer | Customer master for AR (TK 131) | customers |
| Vendor | Vendor master for AP (TK 331) | vendors |
| Employee | Employee for advances (TK 141, 334) | employees |

### Features

- **Customer/Vendor Classification**: Individual, Business, Government
- **Banking Integration**: Multiple bank accounts per partner
- **Contact Management**: Multiple contacts per partner
- **Address Management**: Multiple addresses per partner
- **Tax Information**: TIN tracking for VAT compliance

### Routes Implemented

| Module | Routes | Templates |
|--------|--------|-----------|
| Customer | 4 | 4 |
| Vendor | 4 | 4 |
| Employee | 4 | 4 |

### Git Commits

```
6abcd83 feat: Implement Priority 1 models - Partner, Tax Engine, CostCenter
```

---

## ✅ M5: Tax Engine

**Completed:** 2026-03-18  
**Duration:** 1 day

### Objectives Achieved

- [x] Tax policy configuration
- [x] VAT calculation (0%, 5%, 8%, 10%)
- [x] Corporate income tax tracking
- [x] Personal income tax (PIT) calculation
- [x] Import/Export tax tracking
- [x] Tax deduction rules
- [x] Tax reporting

### Models Implemented

| Model | Description | Tables |
|-------|-------------|--------|
| TaxPolicy | Tax rates and rules | tax_policies |

### Key Features

- **VAT Rates**: 0%, 5%, 8%, 10% (Standard)
- **PIT Brackets**: Progressive rates per Vietnamese law
- **Corporate Tax**: Standard 20%, Pillar 2 (15%)
- **Input/Output Tax Tracking**: TK 1331, TK 1332

### Routes Implemented

| Route | Description |
|-------|-------------|
| /tax/policies | Tax policy CRUD |
| /tax/calculate | VAT/PIT calculation |
| /tax/reports | Tax reports |

### Git Commits

```
6abcd83 feat: Implement Priority 1 models - Partner, Tax Engine, CostCenter
```

---

## ✅ M6: Cost Center & Project Management

**Completed:** 2026-03-18  
**Duration:** 1 day

### Objectives Achieved

- [x] Cost center hierarchy
- [x] Project lifecycle management
- [x] Cost allocation tracking
- [x] Budget integration
- [x] Revenue/Expense attribution

### Models Implemented

| Model | Description | Tables |
|-------|-------------|--------|
| CostCenter | Department/division tracking | cost_centers |
| Project | Project-based accounting | projects |

### Features

- **Cost Center Types**: Department, Division, Product Line
- **Project Types**: Consulting, Product, Research
- **Project Status**: Planning, Active, On Hold, Completed, Cancelled
- **Hierarchical Structure**: Parent-child relationships

### Routes Implemented

| Module | Routes | Templates |
|--------|--------|-----------|
| CostCenter | 7 | 6 |
| Project | 9 | 5 |

### Git Commits

```
1261aff feat: Implement CostCenter, Project, TaxPayment engines with repositories, services, routes, templates, and tests
```

---

## ✅ M7: Tax Payment Management

**Completed:** 2026-03-18  
**Duration:** 1 day

### Objectives Achieved

- [x] Tax obligation tracking
- [x] Payment scheduling
- [x] Deadline monitoring
- [x] Payment history
- [x] Late payment penalty calculation

### Models Implemented

| Model | Description | Tables |
|-------|-------------|--------|
| TaxPayment | Tax payment tracking | tax_payments |

### Tax Types Supported

| Tax Type | Account | Description |
|----------|---------|-------------|
| VAT | TK 3331 | Value Added Tax |
| CIT | TK 3332 | Corporate Income Tax |
| PIT | TK 3335 | Personal Income Tax |
| Import Duty | TK 3333 | Import/Export Tax |
| Other Tax | TK 3339 | Other taxes and fees |

### Payment Status

| Status | Description |
|--------|-------------|
| PENDING | Obligation created |
| DUE_SOON | Within 7 days of deadline |
| OVERDUE | Past deadline |
| PARTIAL | Partially paid |
| PAID | Fully paid |

### Git Commits

```
1261aff feat: Implement CostCenter, Project, TaxPayment engines with repositories, services, routes, templates, and tests
```

---

## ✅ M8: Financial Reports Engine

**Completed:** 2026-03-19  
**Duration:** 1 day

### Objectives Achieved

- [x] Balance Sheet (B01-DN)
- [x] Income Statement (B02-DN)
- [x] Cash Flow Statement (B03-DN) - Indirect Method
- [x] Notes to Financial Statements (B05-DN)
- [x] Trial Balance
- [x] Account Statement
- [x] PDF/Excel export

### Reports Implemented

| Report | Form | Method | Status |
|--------|------|--------|--------|
| Balance Sheet | B01-DN | Account-based | ✅ |
| Income Statement | B02-DN | Multi-step | ✅ |
| Cash Flow | B03-DN | Indirect Method | ✅ |
| Trial Balance | - | - | ✅ |
| Account Statement | - | - | ✅ |
| Notes to FS | B05-DN | Template | ✅ |

### Export Formats

| Format | Extension | Status |
|--------|-----------|--------|
| PDF | .pdf | ✅ |
| Excel | .xlsx | ✅ |

### Key Features

- **VAS Compliance**: All reports follow Circular 99/2025/TT-BTC
- **Multi-period**: Support for monthly, quarterly, annual
- **Comparative**: Current vs Previous period
- **Currency**: VND with thousand separators

### Git Commits

```
f80f273 feat: Implement Financial Reports Engine (B01-B05) with Balance Sheet, Income Statement, Cash Flow
```

---

## ✅ M9: Supporting Document Management

**Completed:** 2026-03-18  
**Duration:** 1 day

### Objectives Achieved

- [x] Document attachment to vouchers
- [x] Multiple file support
- [x] Document type classification
- [x] File metadata tracking

### Models Implemented

| Model | Description | Tables |
|-------|-------------|--------|
| SupportingDocument | Document attachments | supporting_documents |

### Document Types

| Type | Code | Description |
|------|------|-------------|
| Invoice | HD | Sales/Purchase invoices |
| Contract | HDTD | Sales/Purchase contracts |
| Receipt | PT | Payment receipts |
| Payment | PC | Payment vouchers |
| Bank | GBN/GBC | Bank notifications |
| Other | Khác | Other documents |

### Git Commits

```
8eb3b94 feat: Add SupportingDocument model for voucher attachments
```

---

## ✅ M10: Opening Balance Management

**Completed:** 2026-03-18  
**Duration:** 1 day

### Objectives Achieved

- [x] Opening balance entry per fiscal year
- [x] Balance verification
- [x] Prior year carry-forward
- [x] Balance type (Debit/Credit) validation

### Models Implemented

| Model | Description | Tables |
|-------|-------------|--------|
| OpeningBalance | Opening balances per period | opening_balances |

### Features

- **Period Type**: Annual, Quarterly, Monthly
- **Balance Source**: Manual, Imported, Carried Forward
- **Validation**: Debit/Credit matches account normal balance

### Git Commits

```
5b28bb5 feat: Add OpeningBalance model for fiscal year opening balances
```

---

## ✅ M11: Biological Asset Management

**Completed:** 2026-03-18  
**Duration:** 1 day

### Objectives Achieved

- [x] Biological asset tracking (NEW TK 215 per TT99)
- [x] Asset categorization
- [x] Fair value measurement
- [x] Growth/decline tracking

### Models Implemented

| Model | Description | Tables |
|-------|-------------|--------|
| BiologicalAsset | TK 215 - Biological Assets | biological_assets |

### Account Reference

| Code | Name | Description |
|------|------|-------------|
| TK 215 | Tài sản sinh học | NEW in Circular 99/2025/TT-BTC |
| TK 711 | Thu nhập khác | Related revenue |
| TK 811 | Chi phí khác | Related expense |

### Asset Categories

- Consumable biological assets
- Bearer biological assets
- Standing timber (if applicable)

### Git Commits

```
2a27533 feat: Add BiologicalAsset model (TK 215 - NEW in Circular 99/2025)
```

---

## ✅ M12: Dividend Payable Management

**Completed:** 2026-03-18  
**Duration:** 1 day

### Objectives Achieved

- [x] Dividend obligation tracking (NEW TK 332 per TT99)
- [x] Shareholder management
- [x] Payment scheduling
- [x] Tax withholding (5% on dividends)

### Models Implemented

| Model | Description | Tables |
|-------|-------------|--------|
| DividendPayable | TK 332 - Dividends | dividend_payables |

### Account Reference

| Code | Name | Description |
|------|------|-------------|
| TK 332 | Phải trả cổ tức | NEW in Circular 99/2025/TT-BTC |
| TK 421 | Lợi nhuận sau thuế | Source of dividends |
| TK 3335 | Thuế thu nhập cá nhân | 5% withholding tax |

### Shareholder Types

| Type | Description |
|------|-------------|
| INDIVIDUAL | Individual shareholder |
| CORPORATE | Corporate shareholder |
| FOREIGN | Foreign investor |

### Payment Methods

| Method | Description |
|--------|-------------|
| CASH | Cash payment |
| BANK_TRANSFER | Bank transfer |
| STOCK_DIVIDEND | Stock dividend |

### Git Commits

```
5ca356a feat: Add DividendPayable model (TK 332 - NEW in Circular 99/2025)
```

---

## ✅ M13: Advanced Models (Phase 1)

**Completed:** 2026-03-19  
**Duration:** 1 day

### Objectives Achieved

- [x] Approval workflow models
- [x] Document management models
- [x] Notification models
- [x] System settings models
- [x] Backup management models

### Models Implemented

#### Approval Workflow (`models/approval_workflow.py`)

| Model | Description | Tables |
|-------|-------------|--------|
| ApprovalWorkflow | Workflow definitions | approval_workflows |
| ApprovalStep | Workflow steps | approval_steps |
| ApprovalRequest | Approval requests | approval_requests |
| ApprovalAction | Approval actions | approval_actions |

#### Document Management (`models/document.py`)

| Model | Description | Tables |
|-------|-------------|--------|
| Document | Document records | documents |
| DocumentAttachment | File attachments | document_attachments |
| DocumentTemplate | Document templates | document_templates |

#### Notification (`models/notification.py`)

| Model | Description | Tables |
|-------|-------------|--------|
| Notification | User notifications | notifications |

#### System Settings (`models/system_setting.py`)

| Model | Description | Tables |
|-------|-------------|--------|
| SystemSetting | App configuration | system_settings |

#### Backup Management (`models/backup.py`)

| Model | Description | Tables |
|-------|-------------|--------|
| Backup | Backup records | backups |
| BackupSchedule | Backup schedules | backup_schedules |

### Total New Models

```
Phase 1: 11 new models
├── Approval Workflow: 4 models
├── Document Management: 3 models
├── Notification: 1 model
├── System Settings: 1 model
└── Backup Management: 2 models
```

---

## ✅ M14: Advanced Repositories

**Completed:** 2026-03-19  
**Duration:** 1 day

### Objectives Achieved

- [x] Approval repository
- [x] Document repository
- [x] Notification repository
- [x] System setting repository
- [x] Backup repository

### Repositories Implemented

| Repository | Description | Status |
|------------|-------------|--------|
| ApprovalRepository | Approval workflow CRUD | ✅ |
| DocumentRepository | Document CRUD | ✅ |
| NotificationRepository | Notification CRUD | ✅ |
| SystemSettingRepository | Settings CRUD | ✅ |
| BackupRepository | Backup CRUD | ✅ |

### Repository Pattern

All repositories follow the standard pattern:

```python
class Repository:
    def create(self, entity) -> Entity
    def get_by_id(self, id) -> Optional[Entity]
    def get_all(self) -> List[Entity]
    def update(self, entity) -> Entity
    def delete(self, id) -> bool
    def paginate(self, page, per_page) -> Pagination
```

---

## 🔄 M15: Advanced Services (IN PROGRESS)

**Started:** 2026-03-19  
**Status:** In Progress

### Objectives

- [ ] Approval service
- [ ] Document service
- [ ] Notification service
- [ ] System setting service
- [ ] Backup service

### Services to Implement

| Service | Description | Status |
|---------|-------------|--------|
| ApprovalService | Workflow processing | 📋 Pending |
| DocumentService | Document operations | 📋 Pending |
| NotificationService | User notifications | 📋 Pending |
| SystemSettingService | Settings management | 📋 Pending |
| BackupService | Backup operations | 📋 Pending |

---

## 📋 M16: Advanced Routes & Templates

**Status:** Pending

### Routes to Create

| Module | Routes |
|--------|--------|
| Approval | 8 routes |
| Document | 6 routes |
| Notification | 3 routes |
| Settings | 3 routes |
| Backup | 5 routes |

### Templates to Create

| Module | Templates |
|--------|-----------|
| Approval | workflow_list.html, workflow_detail.html, request_form.html, ... |
| Document | document_list.html, document_detail.html, upload.html, ... |
| Notification | notification_list.html, notification_detail.html |
| Settings | settings.html |
| Backup | backup_list.html, schedule.html |

---

## 📋 M17: Advanced Features

**Status:** Pending

### Features Planned

| Feature | Description |
|---------|-------------|
| Notification Triggers | Auto-notify on approvals, deadlines |
| Email Integration | Email notifications |
| Backup Automation | Scheduled backups |
| Data Export | Export system data |
| Audit Trail | Full audit logging |

---

## 📋 M18: Testing & QA

**Status:** Pending

### Test Coverage Target

| Module | Current | Target |
|--------|---------|--------|
| Models | 60% | 80% |
| Services | 50% | 70% |
| Routes | 40% | 60% |
| Overall | ~55% | 70% |

### Tests to Add

| Test Suite | Tests |
|------------|-------|
| Approval Tests | 10 |
| Document Tests | 8 |
| Notification Tests | 5 |
| Backup Tests | 5 |

---

## 📋 M19: Documentation & Deployment

**Status:** Pending

### Documentation Required

| Document | Status |
|----------|--------|
| README.md | 📋 Pending |
| API_DOCS.md | 📋 Pending |
| USER_GUIDE.md | 📋 Pending |
| DEPLOYMENT.md | 📋 Pending |
| CHANGELOG.md | 📋 Pending |

### Deployment Checklist

- [ ] Production configuration
- [ ] gunicorn setup
- [ ] nginx configuration
- [ ] Backup automation
- [ ] Monitoring setup

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-03-19 | System | Initial milestones document |
| 2.0 | 2026-03-19 | System | Added M13-M19 phases |

---

**Document Status:** Active  
**Next Update:** Upon completion of M15-M19
