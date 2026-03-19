# VAS Accounting WebApp - User Guide

**Version:** 2.3  
**Circular:** 99/2025/TT-BTC  
**Last Updated:** 2026-03-19

---

## Table of Contents

1. [Getting Started](#1-getting-started)
2. [Dashboard](#2-dashboard)
3. [Chart of Accounts](#3-chart-of-accounts)
4. [Journal Vouchers](#4-journal-vouchers)
5. [General Ledger](#5-general-ledger)
6. [Financial Reports](#6-financial-reports)
7. [Customer Management](#7-customer-management)
8. [Vendor Management](#8-vendor-management)
9. [Employee Management](#9-employee-management)
10. [Cost Centers](#10-cost-centers)
11. [Projects](#11-projects)
12. [Tax Management](#12-tax-management)
13. [Settings](#13-settings)

---

## 1. Getting Started

### 1.1 Login

Navigate to the application URL and enter your credentials:

```
Username: admin
Password: admin123
```

### 1.2 Navigation

The main navigation is located in the header and sidebar:

**Header (Sticky):**
- KPIs: Tổng Nợ, Tổng Có, Chênh lệch (always visible)
- Global Search: Click or press `Ctrl+K`
- Notifications: Bell icon with badge count
- User Menu: Shows username and role

**Sidebar (Left):**
```
┌─────────────────────────┐
│ THƯỜNG DÙNG             │
│  + Tạo chứng từ    [1] │
│  ≡ Bảng cân đối   [2] │
│  ☰ Sổ NKCT         [3] │
├─────────────────────────┤
│ DANH MỤC                │
│  ⊢ Danh mục TK         │
│  ⊢ Đối tác             │
├─────────────────────────┤
│ SỔ SÁCH                 │
│  ⊢ Sổ cái              │
│  ⊢ Sổ NKCT             │
└─────────────────────────┘
```

### 1.3 Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+K` | Global search |
| `1` | Tạo chứng từ mới |
| `2` | Bảng cân đối |
| `3` | Sổ NKCT |
| `Esc` | Close search modal |

---

## 2. Dashboard

The dashboard provides an overview of your accounting data with real-time KPIs.

### 2.1 Header KPIs (Always Visible)

These KPIs are visible on every page in the header:

- **Tổng Nợ**: Sum of all debit entries for current period
- **Tổng Có**: Sum of all credit entries for current period
- **Chênh lệch**: Difference (should be 0 for balanced books)

### 2.2 Recent Vouchers

View the 5 most recent draft vouchers pending approval.

### 2.3 Quick Actions

- Create new voucher (`1`)
- View trial balance (`2`)
- Access journal (`3`)
- Global search (`Ctrl+K`)

---

## 3. Chart of Accounts

### 3.1 Access

Navigate to **Accounting → Accounts**

### 3.2 Account List

The account list shows all accounts organized by type:

| Code | Name | Type | Normal Balance | Status |
|------|------|------|----------------|--------|
| 111 | Tiền mặt | Asset | Debit | Active |
| 112 | Tiền gửi ngân hàng | Asset | Debit | Active |
| 131 | Phải thu khách hàng | Asset | Debit | Active |

### 3.3 Filter Accounts

Use filters to narrow down accounts:

- **Account Type**: Asset, Liability, Equity, Revenue, Expense
- **Status**: Active, Inactive
- **Search**: Search by code or name

### 3.4 Create Account

1. Click **"New Account"** button
2. Fill in the form:
   - Account Code (e.g., 1111)
   - Account Name (Vietnamese)
   - Account Name (English)
   - Parent Account (optional)
   - Account Type
   - Normal Balance
   - Postable (can have transactions)
3. Click **Save**

### 3.5 Circular 99/2025 TT99 Accounts

The system comes pre-seeded with 71 Level 1 accounts per Circular 99/2025/TT-BTC:

| Group | Accounts |
|-------|----------|
| 1xx | Assets (11 accounts) |
| 2xx | Liabilities (13 accounts) |
| 3xx | Equity (7 accounts) |
| 4xx | Revenue (5 accounts) |
| 5xx | Cost of Goods Sold (5 accounts) |
| 6xx | Expenses (16 accounts) |
| 7xx | Other Income/Expenses (5 accounts) |
| 8xx | Taxes & Finance Costs (6 accounts) |
| 9xx | Manufacturing Costs (5 accounts) |

---

## 4. Journal Vouchers

### 4.1 Access

Navigate to **Accounting → Vouchers**

### 4.2 Voucher List

View all journal vouchers with status:

| Voucher No | Date | Type | Description | Status | Amount |
|------------|------|------|-------------|--------|--------|
| JV-2026-00001 | 2026-03-19 | General | Sales Invoice | Posted | 110,000,000 |

### 4.3 Create Voucher

1. Click **"New Voucher"** button
2. Enter voucher details:
   - Voucher Date
   - Voucher Type (General, Cash Receipt, etc.)
   - Reference Number
   - Description
3. Add journal entries:
   - Select Account
   - Enter Debit OR Credit amount
   - Enter Description
   - Optional: Cost Center, Customer, Vendor
4. Click **Save as Draft** or **Post**

### 4.4 Double-Entry Validation

The system validates that total debits equal total credits:

```
Total Debit:  110,000,000
Total Credit: 110,000,000
Status: ✓ Balanced
```

### 4.5 Voucher Types

| Type | Code | Description |
|------|------|-------------|
| General | general | General journal entry |
| Cash Receipt | cash_receipt | Cash incoming |
| Cash Payment | cash_payment | Cash outgoing |
| Bank Receipt | bank_receipt | Bank deposit |
| Bank Payment | bank_payment | Bank withdrawal |
| Purchase | purchase | Purchase invoice |
| Sales | sales | Sales invoice |

### 4.6 Voucher Status

| Status | Color | Description |
|--------|-------|-------------|
| Draft | Gray | Not yet posted |
| Posted | Green | Posted to ledger |
| Locked | Yellow | Locked for period |
| Cancelled | Red | Cancelled voucher |

### 4.7 Post Voucher

1. Open voucher in draft status
2. Click **Post** button
3. Confirm posting

### 4.8 Cancel Voucher

1. Open posted voucher
2. Click **Cancel** button
3. Enter cancellation reason
4. A reversal voucher will be created

---

## 5. General Ledger

### 5.1 Access

Navigate to **Accounting → Ledger**

### 5.2 View Account Ledger

1. Select an account from the dropdown
2. Set date range (start and end date)
3. Optional: Select cost center
4. Click **View**

### 5.3 Ledger Display

The ledger shows:

```
Account: 111 - Tiền mặt

┌─────────────┬────────────┬─────────┬─────────┬─────────┐
│ Date        │ Voucher    │ Debit   │ Credit  │ Balance │
├─────────────┼────────────┼─────────┼─────────┼─────────┤
│ 2026-01-01  │ Opening    │         │         │ 0.00    │
│ 2026-03-19  │ JV-00001   │ 100M    │         │ 100M    │
│ 2026-03-20  │ JV-00002   │         │ 50M     │ 50M     │
└─────────────┴────────────┴─────────┴─────────┴─────────┘
```

### 5.4 Trial Balance

Navigate to **Reports → Trial Balance**

Shows all accounts with debit/credit totals:

| Account Code | Account Name | Debit | Credit |
|--------------|--------------|-------|--------|
| 111 | Tiền mặt | 50,000,000 | |
| 112 | Tiền gửi NH | 100,000,000 | |
| ... | ... | ... | ... |
| | **Total** | **500,000,000** | **500,000,000** |

---

## 6. Financial Reports

### 6.1 Access

Navigate to **Reports**

### 6.2 Balance Sheet (B01-DN)

**Báo cáo tình hình tài chính**

Report structure per Circular 99:

```
A. ASSETS (TÀI SẢN)
   I. Current Assets (Tài sản ngắn hạn)
      1. Cash (Tiền)
      2. Short-term investments
      3. Accounts receivable
      ...
   II. Fixed Assets (Tài sản dài hạn)
      1. Fixed assets
      2. Biological assets (TK 215 - NEW TT99)
      ...

B. LIABILITIES (NỢ PHẢI TRẢ)
   I. Current liabilities
   II. Long-term liabilities

C. EQUITY (VỐN CHỦ SỞ HỮU)
```

### 6.3 Income Statement (B02-DN)

**Kết quả hoạt động kinh doanh**

```
1. Revenue (Doanh thu)
2. Cost of goods sold (Giá vốn)
3. Gross profit (Lợi nhuận gộp)
4. Financial income
5. Financial expenses
6. Selling expenses
7. Admin expenses
8. Net profit
```

### 6.4 Cash Flow Statement (B03-DN)

**Lưu chuyển tiền tệ (Indirect Method)**

```
I. Cash from operating activities
II. Cash from investing activities
III. Cash from financing activities
IV. Net cash flow
```

### 6.5 Export Reports

Each report can be exported to:

- **Excel (.xlsx)**: Click Export → Excel
- **PDF (.pdf)**: Click Export → PDF

---

## 7. Customer Management

### 7.1 Access

Navigate to **Partners → Customers**

### 7.2 Customer List

| Code | Name | Tax ID | Balance | Status |
|------|------|--------|---------|--------|
| CUS-2026-0001 | ABC Corp | 0123456789 | 50,000,000 | Active |

### 7.3 Create Customer

1. Click **"New Customer"**
2. Fill in details:
   - Name (required)
   - Tax ID
   - Email, Phone
   - Address
   - Contact Person
   - Credit Limit
   - Payment Terms (days)
   - Customer Type (Corporate/Individual/Government)
3. Click **Save**

### 7.4 Customer Detail

View customer information and:

- **Outstanding Balance**: Current AR balance
- **AR Aging**: Breakdown by age
  - Current
  - 1-30 days
  - 31-60 days
  - 61-90 days
  - Over 90 days

### 7.5 AR Aging Report

Navigate to **Partners → AR Aging**

Shows outstanding receivables by aging bucket.

---

## 8. Vendor Management

### 8.1 Access

Navigate to **Partners → Vendors**

### 8.2 Vendor List

Similar to customer list.

### 8.3 Create Vendor

1. Click **"New Vendor"**
2. Fill in details (similar to customer)
3. Additional fields:
   - Bank Account
   - Bank Name
4. Click **Save**

### 8.4 AP Aging Report

Navigate to **Partners → AP Aging**

Shows outstanding payables by aging bucket.

---

## 9. Employee Management

### 9.1 Access

Navigate to **Partners → Employees**

### 9.2 Employee List

| Code | Name | Department | Position | Status |
|------|------|-----------|----------|--------|
| EMP-2026-0001 | Nguyen Van A | Sales | Manager | Active |

### 9.3 Create Employee

1. Click **"New Employee"**
2. Fill in details:
   - Employee ID (company ID)
   - Full Name (required)
   - Date of Birth
   - Gender
   - Department
   - Position
   - Employee Type (Full-time/Part-time/Contract)
   - Join Date
   - ID Card Number
   - Tax ID
   - Social Insurance Number
   - Bank Account for salary
3. Click **Save**

### 9.4 Advance Tracking

Employee advances are tracked via TK 141 in journal vouchers.

---

## 10. Cost Centers

### 10.1 Access

Navigate to **Accounting → Cost Centers**

### 10.2 Cost Center List

| Code | Name | Department | Budget | Used | Remaining |
|------|------|-----------|--------|------|-----------|
| CC-2026-0001 | Sales Dept | Sales | 100M | 50M | 50M |

### 10.3 Create Cost Center

1. Click **"New Cost Center"**
2. Fill in details:
   - Code
   - Name
   - Parent (for hierarchy)
   - Department
   - Budget Allocated
3. Click **Save**

### 10.4 Budget Tracking

Cost center shows:
- Budget Allocated
- Budget Used (from journal entries)
- Budget Remaining

---

## 11. Projects

### 11.1 Access

Navigate to **Projects**

### 11.2 Project List

| Code | Name | Status | Contract | Revenue | Expense | Profit |
|------|------|--------|----------|---------|---------|--------|
| PRJ-2026-0001 | Project A | Active | 500M | 250M | 150M | 100M |

### 11.3 Create Project

1. Click **"New Project"**
2. Fill in details:
   - Code
   - Name
   - Customer (optional)
   - Start Date
   - End Date
   - Status (Planning/Active/On Hold/Completed/Cancelled)
   - Project Type (Service/Construction/Manufacturing)
   - Total Contract Value
3. Click **Save**

### 11.4 Project Tracking

- **Revenue**: From journal entries referencing project code
- **Expense**: From journal entries referencing project code
- **Profit**: Revenue - Expense
- **Completion %**: Manual or automatic

---

## 12. Tax Management

### 12.1 Access

Navigate to **Tax**

### 12.2 Tax Policies

Configure tax rates:

| Policy | Type | Rate | Status |
|--------|------|------|--------|
| VAT Standard | VAT | 10% | Active |
| VAT Reduced | VAT | 5% | Active |

### 12.3 VAT Calculation

The system calculates VAT automatically when creating vouchers:

| Amount | Rate | VAT | Total |
|--------|------|-----|-------|
| 100,000,000 | 10% | 10,000,000 | 110,000,000 |

### 12.4 Tax Payments

Track tax obligations:

| Payment No | Type | Period | Amount | Status | Due Date |
|------------|------|--------|--------|--------|----------|
| TVA-2026-0001 | VAT | Mar 2026 | 10M | Pending | 2026-04-20 |

### 12.5 Tax Types Supported

| Tax | Account | Description |
|-----|---------|-------------|
| VAT | TK 3331 | Value Added Tax |
| CIT | TK 3332 | Corporate Income Tax |
| PIT | TK 3335 | Personal Income Tax |
| Import Duty | TK 3333 | Import/Export Tax |
| Pillar 2 | TK 82112 | Global Minimum Tax (NEW TT99) |

---

## 13. Settings

### 13.1 Access

Navigate to **Settings**

### 13.2 System Settings

| Setting | Description |
|---------|-------------|
| Company Name | Your company name |
| Tax ID | Company tax identification |
| Address | Company address |
| Fiscal Year Start | Beginning of fiscal year |
| Currency | Default currency (VND) |

### 13.3 User Management

**Admin only**

- Create new users
- Assign roles
- Reset passwords

### 13.4 Roles

| Role | Permissions |
|------|-------------|
| Administrator | Full access |
| Accountant | CRUD vouchers, reports, limited settings |
| Auditor | Read-only access |
| Viewer | Reports only |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-03-17 | Initial user guide |
| 2.0 | 2026-03-19 | Added TT99 features |

---

**Document Status:** Active  
**Last Updated:** 2026-03-19
