# VAS Accounting WebApp - Database Schema

**Version:** 2.0  
**Circular:** 99/2025/TT-BTC  
**Last Updated:** 2026-03-19

---

## Table of Contents

1. [Schema Overview](#1-schema-overview)
2. [Core Tables](#2-core-tables)
3. [Accounting Tables](#3-accounting-tables)
4. [Partner Management Tables](#4-partner-management-tables)
5. [Cost & Project Tables](#5-cost--project-tables)
6. [Tax Tables](#6-tax-tables)
7. [Financial Tables](#7-financial-tables)
8. [Workflow Tables](#8-workflow-tables)
9. [Document Tables](#9-document-tables)
10. [System Tables](#10-system-tables)
11. [ER Diagram](#11-er-diagram)
12. [Indexes](#12-indexes)

---

## 1. Schema Overview

### 1.1 Database Information

```
Database: SQLite
Location: accounting_app/instance/accounting.db
WAL Mode: Enabled
UTF-8: Enabled
```

### 1.2 Total Tables

```
Total Models: 30+
Total Tables: 45+
```

### 1.3 Table Categories

| Category | Tables |
|----------|--------|
| Core/Auth | 4 |
| Accounting | 6 |
| Partner Management | 3 |
| Cost & Project | 2 |
| Tax | 2 |
| Financial | 4 |
| Workflow | 4 |
| Document | 3 |
| System | 3 |

---

## 2. Core Tables

### 2.1 users

User accounts for authentication and authorization.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | User ID |
| username | VARCHAR(80) | UNIQUE, NOT NULL | Username |
| email | VARCHAR(120) | UNIQUE, NOT NULL | Email address |
| password_hash | VARCHAR(255) | NOT NULL | Hashed password |
| full_name | VARCHAR(200) | | Full name |
| role_id | INTEGER | FK → roles.id | User role |
| is_active | BOOLEAN | DEFAULT TRUE | Active status |
| last_login | DATETIME | | Last login time |
| created_at | DATETIME | NOT NULL | Creation time |
| updated_at | DATETIME | | Update time |

**Indexes:**
- `ix_users_username` (username)
- `ix_users_email` (email)
- `ix_users_role_id` (role_id)

---

### 2.2 roles

User roles for RBAC.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Role ID |
| name | VARCHAR(50) | UNIQUE, NOT NULL | Role name |
| description | VARCHAR(200) | | Role description |
| permissions | JSON | | Permission list |
| created_at | DATETIME | NOT NULL | Creation time |

**Default Roles:**
- Administrator
- Accountant
- Auditor
- Viewer

---

### 2.3 permissions

Granular permissions for access control.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Permission ID |
| name | VARCHAR(100) | UNIQUE, NOT NULL | Permission name |
| resource | VARCHAR(50) | NOT NULL | Resource type |
| action | VARCHAR(20) | NOT NULL | Action type |
| description | VARCHAR(200) | | Description |

---

### 2.4 audit_logs

Audit trail for all changes.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Log ID |
| user_id | INTEGER | FK → users.id | Acting user |
| action | VARCHAR(50) | NOT NULL | Action performed |
| entity | VARCHAR(50) | | Entity type |
| entity_id | INTEGER | | Entity ID |
| old_value | JSON | | Previous value |
| new_value | JSON | | New value |
| ip_address | VARCHAR(45) | | Client IP |
| user_agent | VARCHAR(500) | | Client user agent |
| timestamp | DATETIME | NOT NULL | Action time |

**Indexes:**
- `ix_audit_user_entity` (user_id, entity)
- `ix_audit_entity_id` (entity, entity_id)
- `ix_audit_timestamp` (timestamp)

---

## 3. Accounting Tables

### 3.1 accounts

Chart of Accounts per Circular 99/2025/TT-BTC.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Account ID |
| code | VARCHAR(10) | UNIQUE, NOT NULL | Account code (71 TT99) |
| name_vi | VARCHAR(200) | NOT NULL | Vietnamese name |
| name_en | VARCHAR(200) | | English name |
| parent_id | INTEGER | FK → accounts.id | Parent account |
| level | INTEGER | NOT NULL | Account level |
| account_type | VARCHAR(50) | NOT NULL | Type (asset, liability, etc.) |
| normal_balance | VARCHAR(10) | NOT NULL | Normal balance (debit/credit) |
| is_postable | BOOLEAN | DEFAULT FALSE | Can have transactions |
| is_active | BOOLEAN | DEFAULT TRUE | Active status |
| created_at | DATETIME | NOT NULL | Creation time |
| updated_at | DATETIME | | Update time |

**Account Types:**
- asset (Tài sản)
- liability (Nợ phải trả)
- equity (Vốn chủ sở hữu)
- revenue (Doanh thu)
- expense (Chi phí)

**Indexes:**
- `ix_accounts_code` (code)
- `ix_accounts_code_type` (code, account_type)
- `ix_accounts_parent_active` (parent_id, is_active)
- `ix_accounts_level` (level)
- `ix_accounts_account_type` (account_type)
- `ix_accounts_is_postable` (is_postable)
- `ix_accounts_is_active` (is_active)

---

### 3.2 journal_vouchers

Journal Voucher headers (double-entry).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Voucher ID |
| voucher_no | VARCHAR(50) | UNIQUE, NOT NULL | Voucher number |
| voucher_date | DATE | NOT NULL | Voucher date |
| voucher_type | VARCHAR(50) | NOT NULL | Voucher type |
| description | VARCHAR(500) | | Description |
| reference | VARCHAR(100) | | Reference number |
| status | VARCHAR(20) | NOT NULL | Status (draft/posted/locked/cancelled) |
| created_by | INTEGER | FK → users.id, NOT NULL | Creator |
| posted_by | INTEGER | FK → users.id | Poster |
| created_at | DATETIME | NOT NULL | Creation time |
| posted_at | DATETIME | | Posting time |
| updated_at | DATETIME | | Update time |

**Statuses:**
- draft (Nháp)
- posted (Đã ghi sổ)
- locked (Khóa)
- cancelled (Hủy)

**Indexes:**
- `ix_voucher_voucher_no` (voucher_no)
- `ix_voucher_date_status` (voucher_date, status)
- `ix_voucher_created_by` (created_by)
- `ix_voucher_posted_by` (posted_by)
- `ix_voucher_voucher_type` (voucher_type)

---

### 3.3 journal_entries

Journal Entry lines (debit/credit).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Entry ID |
| voucher_id | INTEGER | FK → journal_vouchers.id, NOT NULL | Parent voucher |
| account_id | INTEGER | FK → accounts.id, NOT NULL | Account |
| line_number | INTEGER | NOT NULL | Line number |
| debit | NUMERIC(18,2) | DEFAULT 0 | Debit amount |
| credit | NUMERIC(18,2) | DEFAULT 0 | Credit amount |
| description | VARCHAR(200) | | Line description |
| reference | VARCHAR(100) | | Reference |
| cost_center | VARCHAR(50) | | Cost center code |
| customer_id | INTEGER | | Customer reference |
| vendor_id | INTEGER | | Vendor reference |
| bank_account_id | INTEGER | | Bank account reference |
| inventory_item_id | INTEGER | | Inventory item reference |
| created_at | DATETIME | NOT NULL | Creation time |

**Validation Rule:**
```
SUM(debit) == SUM(credit)
```

**Indexes:**
- `ix_entry_voucher_account` (voucher_id, account_id)
- `ix_entry_voucher_id` (voucher_id)
- `ix_entry_account_id` (account_id)
- `ix_entry_customer_id` (customer_id)
- `ix_entry_vendor_id` (vendor_id)

---

### 3.4 accounting_periods

Fiscal year and accounting periods.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Period ID |
| fiscal_year | INTEGER | NOT NULL | Fiscal year |
| period_type | VARCHAR(20) | NOT NULL | Type (monthly/quarterly/annual) |
| period_start | INTEGER | | Start month/quarter |
| period_end | INTEGER | | End month/quarter |
| start_date | DATE | NOT NULL | Period start date |
| end_date | DATE | NOT NULL | Period end date |
| status | VARCHAR(20) | NOT NULL | Status |
| is_locked | BOOLEAN | DEFAULT FALSE | Locked status |
| created_at | DATETIME | NOT NULL | Creation time |

---

### 3.5 opening_balances

Opening balances per fiscal year.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Balance ID |
| account_id | INTEGER | FK → accounts.id, NOT NULL | Account |
| fiscal_year | INTEGER | NOT NULL | Fiscal year |
| period_type | VARCHAR(20) | NOT NULL | Period type |
| debit | NUMERIC(18,2) | DEFAULT 0 | Opening debit |
| credit | NUMERIC(18,2) | DEFAULT 0 | Opening credit |
| source | VARCHAR(20) | | Source type |
| notes | TEXT | | Notes |
| created_by | INTEGER | FK → users.id, NOT NULL | Creator |
| created_at | DATETIME | NOT NULL | Creation time |

**Indexes:**
- `ix_ob_account_year` (account_id, fiscal_year)

---

### 3.6 supporting_documents

Supporting document attachments.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Document ID |
| voucher_id | INTEGER | FK → journal_vouchers.id | Parent voucher |
| document_type | VARCHAR(20) | NOT NULL | Document type |
| document_no | VARCHAR(100) | | Document number |
| document_date | DATE | | Document date |
| filename | VARCHAR(255) | | Stored filename |
| original_filename | VARCHAR(255) | | Original filename |
| file_path | VARCHAR(500) | | File path |
| file_size | INTEGER | | File size in bytes |
| mime_type | VARCHAR(100) | | MIME type |
| uploaded_by | INTEGER | FK → users.id, NOT NULL | Uploader |
| uploaded_at | DATETIME | NOT NULL | Upload time |

---

## 4. Partner Management Tables

### 4.1 customers

Customer master for AR (TK 131).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Customer ID |
| code | VARCHAR(20) | UNIQUE, NOT NULL | Customer code |
| name | VARCHAR(200) | NOT NULL | Customer name |
| tax_id | VARCHAR(20) | | Tax identification number |
| email | VARCHAR(120) | | Email address |
| phone | VARCHAR(20) | | Phone number |
| address | VARCHAR(500) | | Address |
| city | VARCHAR(100) | | City |
| country | VARCHAR(100) | | Country |
| contact_person | VARCHAR(100) | | Contact person |
| credit_limit | NUMERIC(18,2) | DEFAULT 0 | Credit limit |
| payment_terms | INTEGER | DEFAULT 30 | Payment terms (days) |
| is_active | BOOLEAN | DEFAULT TRUE | Active status |
| customer_type | VARCHAR(20) | | Type (corporate/individual/government) |
| notes | TEXT | | Notes |
| created_by | INTEGER | FK → users.id, NOT NULL | Creator |
| created_at | DATETIME | NOT NULL | Creation time |
| updated_at | DATETIME | | Update time |

**Indexes:**
- `ix_customer_code` (code)
- `ix_customer_name` (name)
- `ix_customer_tax_id` (tax_id)
- `ix_customer_active_type` (is_active, customer_type)

---

### 4.2 vendors

Vendor master for AP (TK 331).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Vendor ID |
| code | VARCHAR(20) | UNIQUE, NOT NULL | Vendor code |
| name | VARCHAR(200) | NOT NULL | Vendor name |
| tax_id | VARCHAR(20) | | Tax identification number |
| email | VARCHAR(120) | | Email address |
| phone | VARCHAR(20) | | Phone number |
| address | VARCHAR(500) | | Address |
| city | VARCHAR(100) | | City |
| country | VARCHAR(100) | | Country |
| contact_person | VARCHAR(100) | | Contact person |
| credit_limit | NUMERIC(18,2) | DEFAULT 0 | Credit limit |
| payment_terms | INTEGER | DEFAULT 30 | Payment terms (days) |
| is_active | BOOLEAN | DEFAULT TRUE | Active status |
| vendor_type | VARCHAR(20) | | Type (supplier/service/contractor) |
| bank_account | VARCHAR(50) | | Bank account |
| bank_name | VARCHAR(100) | | Bank name |
| notes | TEXT | | Notes |
| created_by | INTEGER | FK → users.id, NOT NULL | Creator |
| created_at | DATETIME | NOT NULL | Creation time |
| updated_at | DATETIME | | Update time |

**Indexes:**
- `ix_vendor_code` (code)
- `ix_vendor_name` (name)
- `ix_vendor_tax_id` (tax_id)
- `ix_vendor_active_type` (is_active, vendor_type)

---

### 4.3 employees

Employee master for advances (TK 141) and payroll (TK 334).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Employee ID |
| code | VARCHAR(20) | UNIQUE, NOT NULL | Employee code |
| employee_id | VARCHAR(20) | | Employee ID number |
| name | VARCHAR(200) | NOT NULL | Full name |
| date_of_birth | DATE | | Date of birth |
| gender | VARCHAR(10) | | Gender |
| email | VARCHAR(120) | | Email address |
| phone | VARCHAR(20) | | Phone number |
| address | VARCHAR(500) | | Address |
| city | VARCHAR(100) | | City |
| department | VARCHAR(100) | | Department |
| position | VARCHAR(100) | | Position |
| employee_type | VARCHAR(20) | | Type (fulltime/parttime/contractor) |
| join_date | DATE | | Join date |
| leave_date | DATE | | Leave date |
| id_card | VARCHAR(20) | | ID card number |
| tax_id | VARCHAR(20) | | Tax ID |
| social_insurance_no | VARCHAR(20) | | Social insurance number |
| bank_account | VARCHAR(50) | | Bank account |
| bank_name | VARCHAR(100) | | Bank name |
| is_active | BOOLEAN | DEFAULT TRUE | Active status |
| notes | TEXT | | Notes |
| created_by | INTEGER | FK → users.id, NOT NULL | Creator |
| created_at | DATETIME | NOT NULL | Creation time |
| updated_at | DATETIME | | Update time |

**Indexes:**
- `ix_employee_code` (code)
- `ix_employee_name` (name)
- `ix_employee_dept_active` (department, is_active)
- `ix_employee_employee_id` (employee_id)

---

## 5. Cost & Project Tables

### 5.1 cost_centers

Cost centers for expense allocation (TK 641, 642).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Cost Center ID |
| code | VARCHAR(20) | UNIQUE, NOT NULL | CC code |
| name | VARCHAR(200) | NOT NULL | CC name |
| description | VARCHAR(500) | | Description |
| parent_id | INTEGER | FK → cost_centers.id | Parent CC |
| manager_id | INTEGER | | Manager user ID |
| department | VARCHAR(100) | | Department |
| budget_allocated | NUMERIC(18,2) | DEFAULT 0 | Budget |
| is_active | BOOLEAN | DEFAULT TRUE | Active status |
| created_by | INTEGER | FK → users.id, NOT NULL | Creator |
| created_at | DATETIME | NOT NULL | Creation time |
| updated_at | DATETIME | | Update time |

**Indexes:**
- `ix_cc_code` (code)
- `ix_cc_name` (name)
- `ix_cc_dept_active` (department, is_active)

---

### 5.2 projects

Projects for project-based accounting.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Project ID |
| code | VARCHAR(20) | UNIQUE, NOT NULL | Project code |
| name | VARCHAR(200) | NOT NULL | Project name |
| description | VARCHAR(500) | | Description |
| customer_id | INTEGER | | Customer ID |
| start_date | DATE | | Start date |
| end_date | DATE | | End date |
| expected_completion_date | DATE | | Expected completion |
| status | VARCHAR(20) | | Status |
| project_type | VARCHAR(50) | | Type (service/construction/etc.) |
| total_contract_value | NUMERIC(18,2) | DEFAULT 0 | Contract value |
| total_revenue | NUMERIC(18,2) | DEFAULT 0 | Total revenue |
| total_expense | NUMERIC(18,2) | DEFAULT 0 | Total expense |
| completion_percentage | NUMERIC(5,2) | DEFAULT 0 | Completion % |
| manager_id | INTEGER | | Manager user ID |
| cost_center_id | INTEGER | FK → cost_centers.id | Cost center |
| is_active | BOOLEAN | DEFAULT TRUE | Active status |
| created_by | INTEGER | FK → users.id, NOT NULL | Creator |
| created_at | DATETIME | NOT NULL | Creation time |
| updated_at | DATETIME | | Update time |

**Statuses:**
- planning (Lập kế hoạch)
- active (Đang thực hiện)
- on_hold (Tạm dừng)
- completed (Hoàn thành)
- cancelled (Hủy bỏ)

**Indexes:**
- `ix_project_code` (code)
- `ix_project_name` (name)
- `ix_project_status_active` (status, is_active)

---

## 6. Tax Tables

### 6.1 tax_policies

Tax policy configuration.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Policy ID |
| code | VARCHAR(20) | UNIQUE, NOT NULL | Policy code |
| name | VARCHAR(200) | NOT NULL | Policy name |
| tax_type | VARCHAR(20) | NOT NULL | Tax type |
| rate | NUMERIC(5,4) | | Tax rate |
| description | VARCHAR(500) | | Description |
| effective_date | DATE | | Effective date |
| end_date | DATE | | End date |
| is_active | BOOLEAN | DEFAULT TRUE | Active status |
| created_at | DATETIME | NOT NULL | Creation time |

**Tax Types:**
- vat (Thuế GTGT)
- cit (Thuế TNDN)
- pit (Thuế TNCN)
- wht (Thuế khấu trừ)

---

### 6.2 tax_payments

Tax payment tracking.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Payment ID |
| payment_no | VARCHAR(50) | UNIQUE, NOT NULL | Payment number |
| tax_type | VARCHAR(20) | NOT NULL | Tax type |
| declaration_no | VARCHAR(50) | | Declaration number |
| declaration_date | DATE | | Declaration date |
| period_year | INTEGER | NOT NULL | Period year |
| period_month | INTEGER | | Period month |
| period_quarter | INTEGER | | Period quarter |
| taxable_amount | NUMERIC(18,2) | DEFAULT 0 | Taxable amount |
| tax_rate | NUMERIC(5,4) | DEFAULT 0 | Tax rate |
| tax_amount | NUMERIC(18,2) | DEFAULT 0 | Tax amount |
| interest_amount | NUMERIC(18,2) | DEFAULT 0 | Interest |
| penalty_amount | NUMERIC(18,2) | DEFAULT 0 | Penalty |
| total_amount | NUMERIC(18,2) | DEFAULT 0 | Total amount |
| payment_date | DATE | | Payment date |
| due_date | DATE | | Due date |
| payment_status | VARCHAR(20) | | Status |
| payment_method | VARCHAR(20) | | Payment method |
| bank_payment_date | DATE | | Bank payment date |
| bank_transaction_no | VARCHAR(100) | | Bank reference |
| tax_authority | VARCHAR(200) | | Tax authority |
| tax_office_code | VARCHAR(20) | | Tax office code |
| notes | TEXT | | Notes |
| voucher_id | INTEGER | | Related voucher |
| created_by | INTEGER | FK → users.id, NOT NULL | Creator |
| created_at | DATETIME | NOT NULL | Creation time |
| updated_at | DATETIME | | Update time |

**Indexes:**
- `ix_tax_payment_no` (payment_no)
- `ix_tax_payment_year_type` (period_year, tax_type)
- `ix_tax_payment_status_date` (payment_status, payment_date)
- `ix_tax_payment_due_date` (due_date)

---

## 7. Financial Tables

### 7.1 biological_assets (TK 215 - NEW TT99)

Biological assets per Circular 99/2025.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Asset ID |
| code | VARCHAR(20) | UNIQUE, NOT NULL | Asset code |
| name | VARCHAR(200) | NOT NULL | Asset name |
| category | VARCHAR(50) | | Category |
| asset_type | VARCHAR(20) | | Type |
| quantity | DECIMAL | | Quantity |
| unit | VARCHAR(20) | | Unit |
| initial_value | NUMERIC(18,2) | | Initial value |
| current_value | NUMERIC(18,2) | | Current value |
| fair_value | NUMERIC(18,2) | | Fair value |
| location | VARCHAR(200) | | Location |
| acquisition_date | DATE | | Acquisition date |
| status | VARCHAR(20) | | Status |
| notes | TEXT | | Notes |
| created_by | INTEGER | FK → users.id | Creator |
| created_at | DATETIME | | Creation time |

---

### 7.2 dividend_payables (TK 332 - NEW TT99)

Dividend payable per Circular 99/2025.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Dividend ID |
| payment_no | VARCHAR(50) | UNIQUE, NOT NULL | Payment number |
| shareholder_name | VARCHAR(200) | NOT NULL | Shareholder name |
| shareholder_type | VARCHAR(20) | | Type |
| share_quantity | DECIMAL | | Number of shares |
| dividend_per_share | NUMERIC(18,2) | | Dividend per share |
| total_amount | NUMERIC(18,2) | | Total dividend |
| withholding_tax | NUMERIC(18,2) | | WHT amount |
| net_amount | NUMERIC(18,2) | | Net amount |
| declaration_date | DATE | | Declaration date |
| payment_date | DATE | | Payment date |
| due_date | DATE | | Due date |
| status | VARCHAR(20) | | Status |
| payment_method | VARCHAR(20) | | Payment method |
| bank_account | VARCHAR(50) | | Bank account |
| notes | TEXT | | Notes |
| created_by | INTEGER | FK → users.id | Creator |
| created_at | DATETIME | | Creation time |

---

## 8. Workflow Tables

### 8.1 approval_workflows

Approval workflow definitions (Điều 3 TT99).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Workflow ID |
| code | VARCHAR(20) | UNIQUE, NOT NULL | Workflow code |
| name | VARCHAR(200) | NOT NULL | Workflow name |
| description | VARCHAR(500) | | Description |
| entity_type | VARCHAR(50) | NOT NULL | Entity type |
| approval_levels | INTEGER | DEFAULT 1 | Number of levels |
| is_active | BOOLEAN | DEFAULT TRUE | Active status |
| auto_approve_below | NUMERIC(18,2) | | Auto-approve limit |
| created_by | INTEGER | FK → users.id, NOT NULL | Creator |
| created_at | DATETIME | NOT NULL | Creation time |
| updated_at | DATETIME | | Update time |

**Indexes:**
- `ix_workflow_code` (code)
- `ix_workflow_entity_active` (entity_type, is_active)

---

### 8.2 approval_steps

Workflow step definitions.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Step ID |
| workflow_id | INTEGER | FK → approval_workflows.id, NOT NULL | Parent workflow |
| sequence | INTEGER | NOT NULL | Step sequence |
| name | VARCHAR(200) | NOT NULL | Step name |
| description | VARCHAR(500) | | Description |
| approver_role_id | INTEGER | FK → roles.id | Approver role |
| approver_user_id | INTEGER | FK → users.id | Specific approver |
| approval_limit | NUMERIC(18,2) | | Approval limit |
| timeout_hours | INTEGER | | Timeout |
| is_required | BOOLEAN | DEFAULT TRUE | Required step |
| can_delegate | BOOLEAN | DEFAULT FALSE | Can delegate |
| created_at | DATETIME | NOT NULL | Creation time |

---

### 8.3 approval_requests

Individual approval requests.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Request ID |
| request_no | VARCHAR(50) | UNIQUE, NOT NULL | Request number |
| workflow_id | INTEGER | FK → approval_workflows.id, NOT NULL | Workflow |
| entity_type | VARCHAR(50) | NOT NULL | Entity type |
| entity_id | INTEGER | NOT NULL | Entity ID |
| amount | NUMERIC(18,2) | | Amount |
| description | VARCHAR(500) | | Description |
| requester_id | INTEGER | FK → users.id, NOT NULL | Requester |
| current_step_sequence | INTEGER | DEFAULT 1 | Current step |
| status | VARCHAR(20) | NOT NULL | Status |
| requested_at | DATETIME | NOT NULL | Request time |
| completed_at | DATETIME | | Completion time |
| comments | TEXT | | Comments |
| created_at | DATETIME | NOT NULL | Creation time |
| updated_at | DATETIME | | Update time |

**Indexes:**
- `ix_request_no` (request_no)
- `ix_request_entity` (entity_type, entity_id)
- `ix_request_status_date` (status, requested_at)

---

### 8.4 approval_actions

Individual approval/rejection actions.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Action ID |
| request_id | INTEGER | FK → approval_requests.id, NOT NULL | Request |
| step_id | INTEGER | FK → approval_steps.id, NOT NULL | Step |
| approver_id | INTEGER | FK → users.id, NOT NULL | Approver |
| is_approved | BOOLEAN | NOT NULL | Approval status |
| comments | TEXT | | Comments |
| delegated_from_id | INTEGER | FK → users.id | Delegation source |
| action_at | DATETIME | NOT NULL | Action time |

---

## 9. Document Tables

### 9.1 documents

Document records per Phụ lục I TT99.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Document ID |
| document_no | VARCHAR(50) | UNIQUE, NOT NULL | Document number |
| document_type | VARCHAR(10) | NOT NULL | Document type |
| document_date | DATE | NOT NULL | Document date |
| reference_no | VARCHAR(100) | | Reference number |
| reference_date | DATE | | Reference date |
| entity_type | VARCHAR(50) | | Entity type |
| entity_id | INTEGER | | Entity ID |
| voucher_id | INTEGER | FK → journal_vouchers.id | Related voucher |
| amount | NUMERIC(18,2) | DEFAULT 0 | Amount |
| currency | VARCHAR(3) | DEFAULT 'VND' | Currency |
| exchange_rate | NUMERIC(18,4) | DEFAULT 1 | Exchange rate |
| description | VARCHAR(500) | | Description |
| attachment_count | INTEGER | DEFAULT 0 | Attachment count |
| status | VARCHAR(20) | DEFAULT 'draft' | Status |
| approval_status | VARCHAR(20) | DEFAULT 'pending' | Approval status |
| approval_request_id | INTEGER | | Approval request |
| signed_by | INTEGER | FK → users.id | Signer |
| signed_at | DATETIME | | Sign time |
| created_by | INTEGER | FK → users.id, NOT NULL | Creator |
| created_at | DATETIME | NOT NULL | Creation time |
| updated_at | DATETIME | | Update time |

**Document Types (per Phụ lục I):**
- pt (Phiếu thu)
- pc (Phiếu chi)
- pnk (Phiếu nhập kho)
- pxk (Phiếu xuất kho)
- hd (Hóa đơn)
- bb (Biên bản)
- gbn (Giấy báo Nợ)
- gbc (Giấy báo Có)

**Indexes:**
- `ix_document_no` (document_no)
- `ix_document_date_type` (document_date, document_type)
- `ix_document_entity` (entity_type, entity_id)

---

### 9.2 document_attachments

Document file attachments.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Attachment ID |
| document_id | INTEGER | FK → documents.id, NOT NULL | Parent document |
| filename | VARCHAR(255) | NOT NULL | Stored filename |
| original_filename | VARCHAR(255) | NOT NULL | Original filename |
| file_path | VARCHAR(500) | NOT NULL | File path |
| file_type | VARCHAR(50) | | File type |
| file_size | INTEGER | | File size in bytes |
| mime_type | VARCHAR(100) | | MIME type |
| description | VARCHAR(500) | | Description |
| uploaded_by | INTEGER | FK → users.id, NOT NULL | Uploader |
| uploaded_at | DATETIME | NOT NULL | Upload time |

---

### 9.3 document_templates

Document template definitions.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Template ID |
| code | VARCHAR(20) | UNIQUE, NOT NULL | Template code |
| name | VARCHAR(200) | NOT NULL | Template name |
| document_type | VARCHAR(10) | NOT NULL | Document type |
| description | VARCHAR(500) | | Description |
| template_content | TEXT | | Template HTML |
| required_fields | JSON | | Required fields |
| optional_fields | JSON | | Optional fields |
| validation_rules | JSON | | Validation rules |
| is_active | BOOLEAN | DEFAULT TRUE | Active status |
| created_by | INTEGER | FK → users.id, NOT NULL | Creator |
| created_at | DATETIME | NOT NULL | Creation time |
| updated_at | DATETIME | | Update time |

---

## 10. System Tables

### 10.1 notifications

User notifications.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Notification ID |
| user_id | INTEGER | FK → users.id, NOT NULL | Recipient |
| title | VARCHAR(200) | NOT NULL | Title |
| message | TEXT | NOT NULL | Message |
| notification_type | VARCHAR(50) | | Type |
| entity_type | VARCHAR(50) | | Related entity type |
| entity_id | INTEGER | | Related entity ID |
| is_read | BOOLEAN | DEFAULT FALSE | Read status |
| read_at | DATETIME | | Read time |
| created_at | DATETIME | NOT NULL | Creation time |

**Indexes:**
- `ix_notification_user_read` (user_id, is_read)

---

### 10.2 system_settings

Application configuration.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Setting ID |
| key | VARCHAR(100) | UNIQUE, NOT NULL | Setting key |
| value | TEXT | | Setting value |
| value_type | VARCHAR(20) | DEFAULT 'string' | Value type |
| category | VARCHAR(50) | | Category |
| description | VARCHAR(200) | | Description |
| is_encrypted | BOOLEAN | DEFAULT FALSE | Encrypted flag |
| is_system | BOOLEAN | DEFAULT FALSE | System setting |
| updated_by | INTEGER | FK → users.id | Last updater |
| updated_at | DATETIME | | Update time |

---

### 10.3 backups

Backup metadata.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Backup ID |
| backup_no | VARCHAR(50) | UNIQUE, NOT NULL | Backup number |
| backup_type | VARCHAR(20) | NOT NULL | Backup type |
| file_path | VARCHAR(500) | NOT NULL | File path |
| file_size | INTEGER | | File size in bytes |
| status | VARCHAR(20) | NOT NULL | Status |
| started_at | DATETIME | NOT NULL | Start time |
| completed_at | DATETIME | | Completion time |
| error_message | TEXT | | Error message |
| created_by | INTEGER | FK → users.id | Creator |

---

### 10.4 backup_schedules

Backup schedules.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Schedule ID |
| name | VARCHAR(200) | NOT NULL | Schedule name |
| backup_type | VARCHAR(20) | NOT NULL | Backup type |
| frequency | VARCHAR(20) | NOT NULL | Frequency |
| day_of_week | INTEGER | | Day of week |
| day_of_month | INTEGER | | Day of month |
| time | TIME | NOT NULL | Run time |
| retention_days | INTEGER | DEFAULT 30 | Retention period |
| is_active | BOOLEAN | DEFAULT TRUE | Active status |
| last_run | DATETIME | | Last run time |
| next_run | DATETIME | | Next run time |
| created_by | INTEGER | FK → users.id | Creator |
| created_at | DATETIME | NOT NULL | Creation time |

---

## 11. ER Diagram

### 11.1 Core Accounting Relationships

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  accounts   │────<│  journal_entries  │────>│ journal_vouchers│
└─────────────┘     └──────────────────┘     └─────────────────┘
                           │
                           ├────> customers (TK 131)
                           ├────> vendors (TK 331)
                           ├────> bank_accounts (TK 112)
                           └────> inventory_items
```

### 11.2 Partner Relationships

```
┌───────────┐     ┌───────────┐     ┌─────────────┐
│ customers │────<│ journals  │>────│  vendors    │
└───────────┘     └───────────┘     └─────────────┘
                       │
                       └────> employees (TK 141, 334)
```

### 11.3 Project & Cost Center Relationships

```
┌────────────────┐     ┌───────────────┐
│    projects    │────>│  cost_centers │
└────────────────┘     └───────────────┘
       │
       └────> journals (TK 5xx, 6xx)
```

---

## 12. Indexes

### 12.1 Composite Indexes

| Index Name | Columns | Purpose |
|------------|---------|---------|
| ix_accounts_code_type | code, account_type | Account lookup |
| ix_voucher_date_status | voucher_date, status | Voucher filtering |
| ix_entry_voucher_account | voucher_id, account_id | Entry lookup |
| ix_customer_active_type | is_active, customer_type | Customer filtering |
| ix_vendor_active_type | is_active, vendor_type | Vendor filtering |
| ix_project_status_active | status, is_active | Project filtering |
| ix_workflow_entity_active | entity_type, is_active | Workflow filtering |

### 12.2 Performance Indexes

| Table | Index | Columns |
|-------|-------|---------|
| journal_entries | ix_entry_account_id | account_id |
| journal_entries | ix_entry_customer_id | customer_id |
| journal_entries | ix_entry_vendor_id | vendor_id |
| tax_payments | ix_tax_payment_due_date | due_date |
| notifications | ix_notification_user_read | user_id, is_read |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-03-17 | Initial schema |
| 2.0 | 2026-03-19 | Added workflow, document, system tables |

---

**Document Status:** Active  
**Next Review:** Upon schema changes
