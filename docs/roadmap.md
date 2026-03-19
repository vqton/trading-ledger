# VAS Accounting WebApp - Implementation Roadmap

**Version:** 2.0  
**Circular:** 99/2025/TT-BTC  
**Last Updated:** 2026-03-19

---

## Executive Summary

This roadmap outlines the implementation phases for the Vietnamese Accounting WebApp following Circular 99/2025/TT-BTC. The application is built with Flask + SQLAlchemy + SQLite following Clean Architecture principles.

### Circular 99/2025/TT-BTC Key Changes from Circular 200

| Change | Description |
|--------|-------------|
| **71 TK cấp 1** | Reduced from 76 accounts |
| **New Account TK 215** | Tài sản sinh học (Biological Assets) |
| **New Account TK 332** | Phải trả cổ tức, lợi nhuận (Dividends Payable) |
| **New Account TK 82112** | Thuế TNDN bổ sung (Pillar 2 - Global Minimum Tax) |
| **Renamed TK 155** | Thành phẩm → Sản phẩm |
| **Renamed TK 112** | Tiền gửi Ngân hàng → Tiền gửi không kỳ hạn |
| **Removed TK 461, 466** | Nguồn kinh phí |
| **Report Rename** | "Bảng cân đối kế toán" → "Báo cáo tình hình tài chính" |

### Current Status

| Component | Status | Coverage |
|-----------|--------|----------|
| Project Skeleton | ✅ Complete | 100% |
| Database Models | ✅ Complete | 100% (30+ models) |
| COA Engine | ✅ Complete | 79/79 tests |
| Journal Service | ✅ Complete | Core functionality |
| Ledger Service | ✅ Complete | Core functionality |
| Financial Report Service | ✅ Complete | B01, B02, B03 |
| Tax Engine | ✅ Complete | Full implementation |
| Partner Management | ✅ Complete | Customer/Vendor/Employee |
| Cost Center | ✅ Complete | Full CRUD + budget |
| Project | ✅ Complete | Full CRUD + tracking |
| Tax Payment | ✅ Complete | Full implementation |
| Biological Asset (TK 215) | ✅ Model Complete | Services pending |
| Dividend Payable (TK 332) | ✅ Model Complete | Services pending |
| Approval Workflow | ✅ Model Complete | Services pending |
| Document Management | ✅ Model Complete | Services pending |
| Notification | ✅ Model Complete | Services pending |
| System Settings | ✅ Model Complete | Services pending |
| Backup Management | ✅ Model Complete | Services pending |

---

## Part 1: Model Analysis

### Circular 99/2025/TT-BTC Subledger Requirements

TT99 accounts requiring subledger/detail tracking:

| TK | Name | Subledger Type | Model Required |
|----|------|----------------|----------------|
| 131 | Phải thu của khách hàng | Customer | `Customer` |
| 331 | Phải trả cho người bán | Vendor | `Vendor` |
| 141 | Tạm ứng | Employee | `Employee` |
| 334 | Phải trả người lao động | Employee | `Employee` |
| 151-158 | Hàng tồn kho | Inventory | `InventoryItem` ✅ |
| 211-214 | Tài sản cố định | Fixed Asset | `FixedAsset` ✅ |
| 333 | Thuế và các khoản phải nộp | Tax | `TaxPolicy` ✅ |
| 112 | Tiền gửi ngân hàng | Bank | `BankAccount` ✅ |
| 341 | Vay và nợ thuê tài chính | Bank | `BankAccount` ✅ |

---

### Existing Models (25 total)

#### Core/Auth (`core/security.py`)
| Model | Status | Tables |
|-------|--------|--------|
| `User` | ✅ | users |
| `Role` | ✅ | roles |
| `Permission` | ✅ | permissions |

#### Accounting (`models/`)
| Model | Status | Tables |
|-------|--------|--------|
| `Account` | ✅ | accounts |
| `JournalVoucher` | ✅ | journal_vouchers |
| `JournalEntry` | ✅ | journal_entries |
| `AccountingPeriod` | ✅ | accounting_periods |
| `AuditLog` | ✅ | audit_logs |
| `TaxPolicy` | ✅ | tax_policies |

#### Inventory (`models/inventory.py`)
| Model | Status | Tables |
|-------|--------|--------|
| `Warehouse` | ✅ | warehouses |
| `InventoryItem` | ✅ | inventory_items |
| `StockTransaction` | ✅ | stock_transactions |
| `InventoryBatch` | ✅ | inventory_batches |

#### Fixed Assets (`models/fixed_asset.py`)
| Model | Status | Tables |
|-------|--------|--------|
| `FixedAssetCategory` | ✅ | fixed_asset_categories |
| `FixedAsset` | ✅ | fixed_assets |
| `DepreciationEntry` | ✅ | depreciation_entries |

#### Banking (`models/bank.py`)
| Model | Status | Tables |
|-------|--------|--------|
| `BankAccount` | ✅ | bank_accounts |
| `BankStatement` | ✅ | bank_statements |
| `BankReconciliation` | ✅ | bank_reconciliations |

#### Budget & Currency (`models/`)
| Model | Status | Tables |
|-------|--------|--------|
| `Budget` | ✅ | budgets |
| `BudgetDetail` | ✅ | budget_details |
| `BudgetActual` | ✅ | budget_actuals |
| `Currency` | ✅ | currencies |
| `ExchangeRate` | ✅ | exchange_rates |
| `ForeignCurrencyTransaction` | ✅ | fc_transactions |
| `UnrealizedExchangeDiff` | ✅ | unrealized_exchange_diff |

---

### Missing Models (11 required)

#### Priority 1 - Core Subledgers (Required for TT99)

| Model | File | Description | TK Reference |
|-------|------|-------------|--------------|
| `Customer` | `models/customer.py` | Customer master for AR | TK 131 |
| `Vendor` | `models/vendor.py` | Vendor/supplier master for AP | TK 331 |
| `Employee` | `models/employee.py` | Employee for advances & payroll | TK 141, 334 |

#### Priority 2 - Cost & Project Allocation

| Model | File | Description | TK Reference |
|-------|------|-------------|--------------|
| `CostCenter` | `models/cost_center.py` | Cost allocation center | TK 627, 641, 642 |
| `Project` | `models/project.py` | Project tracking | Various |

#### Priority 3 - Document Engine (Phụ lục I)

| Model | File | Description | Reference |
|-------|------|-------------|-----------|
| `Document` | `models/document.py` | Document/voucher templates | Phụ lục I |
| `DocumentAttachment` | `models/document.py` | Attached files | Phụ lục I |
| `DocumentTemplate` | `models/document.py` | Template definitions | Phụ lục I |

#### Priority 4 - Internal Control (Điều 3)

| Model | File | Description | Reference |
|-------|------|-------------|-----------|
| `ApprovalWorkflow` | `models/approval.py` | Workflow definitions | Điều 3 |
| `ApprovalRequest` | `models/approval.py` | Individual requests | Điều 3 |
| `ApprovalStep` | `models/approval.py` | Workflow steps | Điều 3 |

#### Priority 5 - Supporting Entities

| Model | File | Description |
|-------|------|-------------|
| `VATTransaction` | `models/vat_transaction.py` | VAT transaction detail |
| `Notification` | `models/notification.py` | User notifications |
| `SystemSettings` | `models/settings.py` | Application configuration |
| `Backup` | `models/backup.py` | Backup metadata |

---

### Summary: Models Status

```
┌─────────────────────────────────────┬────────────────────┐
│ Category                            │ Status             │
├─────────────────────────────────────┼────────────────────┤
│ Authentication & Security            │ ✅ Complete (3)    │
│ Chart of Accounts & Journal         │ ✅ Complete (3)    │
│ Inventory Management                │ ✅ Complete (4)    │
│ Fixed Assets                        │ ✅ Complete (3)    │
│ Banking & Reconciliation           │ ✅ Complete (3)    │
│ Budget & Currency                  │ ✅ Complete (7)    │
│ Tax Policy                          │ ✅ Complete (1)    │
├─────────────────────────────────────┼────────────────────┤
│ Customer/Vendor/Employee Subledgers │ ❌ Missing (3)    │
│ Cost Center & Project               │ ❌ Missing (2)    │
│ Document Engine                     │ ❌ Missing (3)    │
│ Approval Workflow                   │ ❌ Missing (3)    │
│ Supporting Entities                │ ❌ Missing (4)    │
├─────────────────────────────────────┼────────────────────┤
│ TOTAL                               │ 25 existing        │
│                                     │ 15 missing         │
└─────────────────────────────────────┴────────────────────┘
```

---

## Part 2: Implementation Plan

### Phase 1: Core Subledger Models (Week 1-2)

**Objective:** Implement Customer, Vendor, Employee models for TT99 subledger compliance.

#### 1.1 Customer Model (`models/customer.py`)

```python
# Fields:
# - id, code, name, tax_code, address, email, phone
# - contact_person, bank_account, bank_name
# - credit_limit, payment_terms
# - is_active, created_at, updated_at

# Relationships:
# - journal_entries (FK via customer_id)
# - addresses (one-to-many)
# - contacts (one-to-many)
```

#### 1.2 Vendor Model (`models/vendor.py`)

```python
# Fields:
# - id, code, name, tax_code, address, email, phone
# - contact_person, bank_account, bank_name
# - payment_terms, is_active
# - created_at, updated_at

# Relationships:
# - journal_entries (FK via vendor_id)
# - purchases (one-to-many)
```

#### 1.3 Employee Model (`models/employee.py`)

```python
# Fields:
# - id, code, name, department, position
# - email, phone, address
# - hire_date, termination_date
# - is_active, created_at, updated_at

# Relationships:
# - advances (TK 141 via journal_entries)
# - payroll_entries (TK 334)
```

---

### Phase 2: Cost & Project Allocation (Week 3)

**Objective:** Support cost allocation and project accounting per Circular 99.

#### 2.1 CostCenter Model (`models/cost_center.py`)

```python
# Fields:
# - id, code, name, description
# - parent_id (hierarchy)
# - manager_id (FK to Employee)
# - budget_allocated, is_active

# Relationships:
# - journal_entries (via cost_center field)
# - budget_details
```

#### 2.2 Project Model (`models/project.py`)

```python
# Fields:
# - id, code, name, description
# - start_date, end_date, status
# - customer_id (FK)
# - budget, is_active

# Relationships:
# - journal_entries
# - cost_centers
# - milestones
```

---

### Phase 3: Document Engine Models (Week 4)

**Objective:** Support 33 document templates per Phụ lục I.

#### 3.1 Document Model (`models/document.py`)

```python
# Fields:
# - id, document_no, document_type
# - document_date, reference
# - description, attachments
# - journal_voucher_id (FK)
# - status, created_by

# Document Types:
# - PT (Phiếu thu), PC (Phiếu chi)
# - PXK (Phiếu xuất kho), PNK (Phiếu nhập kho)
# - HD (Hóa đơn), BB (Biên bản)
# - GBN (Giấy báo Nợ), GBC (Giấy báo Có)
```

#### 3.2 DocumentTemplate Model (`models/document.py`)

```python
# Fields:
# - id, code, name, document_type
# - required_fields (JSON)
# - optional_fields (JSON)
# - validation_rules (JSON)
# - print_template (HTML)
```

---

### Phase 4: Internal Control Models (Week 5)

**Objective:** Implement approval workflows per Điều 3.

#### 4.1 ApprovalWorkflow Model (`models/approval.py`)

```python
# Fields:
# - id, name, description
# - entity_type (voucher, payment, etc.)
# - approval_levels, is_active

# Relationships:
# - steps (ApprovalStep)
# - requests (ApprovalRequest)
```

#### 4.2 ApprovalStep Model (`models/approval.py`)

```python
# Fields:
# - id, workflow_id, sequence
# - approver_role_id, approver_user_id
# - approval_limit, timeout_hours
```

#### 4.3 ApprovalRequest Model (`models/approval.py`)

```python
# Fields:
# - id, workflow_id, entity_id
# - requester_id, status
# - requested_at, decided_at
# - comments, is_approved
```

---

## Part 3: Service Implementation Plan

### Service Building Order

```
Week 1: CustomerService, VendorService
Week 2: EmployeeService
Week 3: CostCenterService, ProjectService
Week 4: DocumentService, DocumentTemplateService
Week 5: ApprovalService, ApprovalWorkflowService
Week 6: NotificationService, SettingsService
```

### Service Responsibilities

#### CustomerService
- CRUD operations for customers
- AR aging reports
- Customer balance calculation
- Credit limit validation

#### VendorService
- CRUD operations for vendors
- AP aging reports
- Vendor balance calculation
- Payment scheduling

#### EmployeeService
- CRUD operations for employees
- Advance tracking (TK 141)
- Payroll integration (TK 334)

#### CostCenterService
- Cost center hierarchy management
- Budget allocation
- Expense allocation reporting

#### ProjectService
- Project lifecycle management
- Project accounting
- Milestone tracking

#### DocumentService
- Document creation and numbering
- Template rendering
- Print formatting
- Attachment management

#### ApprovalService
- Workflow initiation
- Approval routing
- Multi-level approval
- Delegation support

---

## Part 4: Testing Requirements

### Unit Tests Required

| Model | Test Coverage |
|-------|---------------|
| Customer | 10 tests |
| Vendor | 10 tests |
| Employee | 8 tests |
| CostCenter | 6 tests |
| Project | 6 tests |
| Document | 8 tests |
| Approval | 10 tests |

### Integration Tests

| Scenario | Tests |
|----------|-------|
| Customer → Journal Entry | 3 tests |
| Vendor → Journal Entry | 3 tests |
| Employee → Advance (141) | 3 tests |
| Approval Workflow | 5 tests |

---

## Implementation Checklist

### Week 1-2: Core Subledgers
- [ ] Create `models/customer.py`
- [ ] Create `repositories/customer_repository.py`
- [ ] Create `services/customer_service.py`
- [ ] Create `routes/customer_routes.py`
- [ ] Create `templates/accounting/customers/`
- [ ] Create `models/vendor.py`
- [ ] Create `repositories/vendor_repository.py`
- [ ] Create `services/vendor_service.py`
- [ ] Create `routes/vendor_routes.py`
- [ ] Create `templates/accounting/vendors/`
- [ ] Update JournalEntry to link to Customer/Vendor
- [ ] Write 20 unit tests

### Week 3: Cost & Project
- [ ] Create `models/cost_center.py`
- [ ] Create `models/project.py`
- [ ] Create repositories and services
- [ ] Create routes and templates
- [ ] Write 12 unit tests

### Week 4: Document Engine
- [ ] Create `models/document.py`
- [ ] Create `models/document_template.py`
- [ ] Create repositories and services
- [ ] Create routes and templates
- [ ] Implement document numbering per TT99
- [ ] Write 8 unit tests

### Week 5: Internal Control
- [ ] Create `models/approval.py`
- [ ] Create repositories and services
- [ ] Create routes and templates
- [ ] Implement workflow engine
- [ ] Write 10 unit tests

### Week 6: Supporting Services
- [ ] Create `models/notification.py`
- [ ] Create notification service
- [ ] Create system settings service
- [ ] Write 5 unit tests

---

## Technical Notes

### Database Migrations

When implementing new models, delete and recreate database:

```bash
rm accounting_app/instance/accounting.db
pytest -q
```

### Model Relationships

```
Customer (1) ─────< JournalEntry (M)
Vendor (1) ───────< JournalEntry (M)
Employee (1) ─────< JournalEntry (M)
CostCenter (1) ───< JournalEntry (M)
Project (1) ──────< JournalEntry (M)
Document (1) ─────< DocumentAttachment (M)
ApprovalWorkflow (1) ──< ApprovalRequest (M)
ApprovalStep (1) ──< ApprovalWorkflow (M)
```

### Circular 99 Compliance

All models must support:
- Vietnamese language fields (name_vi)
- English translation fields (name_en) optional
- Proper indexing for performance
- Audit trail integration

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-03-17 | System | Initial roadmap |
| 2.0 | 2026-03-19 | System | Added missing model analysis |
| 3.0 | 2026-03-19 | System | Updated status - all core modules complete |
| 4.0 | 2026-03-19 | System | Added comprehensive documentation |

---

**Document Status:** Draft  
**Next Review:** Weekly during active development
