# VAS Accounting WebApp - API Documentation

**Version:** 2.3  
**Circular:** 99/2025/TT-BTC  
**Last Updated:** 2026-03-19

---

## Table of Contents

1. [Overview](#1-overview)
2. [Authentication](#2-authentication)
3. [Account Endpoints](#3-account-endpoints)
4. [Journal Endpoints](#4-journal-endpoints)
5. [Ledger Endpoints](#5-ledger-endpoints)
6. [Financial Report Endpoints](#6-financial-report-endpoints)
7. [Partner Endpoints](#7-partner-endpoints)
8. [Tax Endpoints](#8-tax-endpoints)
9. [Cost Center Endpoints](#9-cost-center-endpoints)
10. [Project Endpoints](#10-project-endpoints)
11. [Tax Payment Endpoints](#11-tax-payment-endpoints)
12. [API Response Format](#12-api-response-format)

---

## 1. Overview

### 1.1 Base URL

```
Development: http://localhost:5000
Production: https://your-domain.com
```

### 1.2 API Prefix

All API endpoints are prefixed with `/api/v1/`

### 1.3 Content Type

All requests and responses use JSON format:
```
Content-Type: application/json
```

### 1.4 Authentication

API endpoints require authentication via session cookies (Flask-Login).

### 1.5 Rate Limiting

Not currently implemented (on-premise deployment).

---

## 2. Authentication

### 2.1 Login

**POST** `/auth/login`

Login user and create session.

**Request:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response (200):**
```json
{
  "status": "success",
  "message": "Login successful",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "role": "Administrator"
  }
}
```

**Response (401):**
```json
{
  "status": "error",
  "message": "Invalid username or password"
}
```

---

### 2.2 Logout

**POST** `/auth/logout`

Logout user and destroy session.

**Response (200):**
```json
{
  "status": "success",
  "message": "Logged out successfully"
}
```

---

### 2.3 Register

**POST** `/auth/register`

Register new user (Admin only).

**Request:**
```json
{
  "username": "newuser",
  "email": "newuser@example.com",
  "password": "securepassword",
  "full_name": "New User",
  "role_id": 2
}
```

**Response (201):**
```json
{
  "status": "success",
  "message": "User registered successfully",
  "user_id": 2
}
```

---

### 2.4 Get Current User

**GET** `/auth/me`

Get current authenticated user.

**Response (200):**
```json
{
  "status": "success",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "full_name": "Administrator",
    "role": "Administrator",
    "last_login": "2026-03-19T10:30:00Z"
  }
}
```

---

## 3. Account Endpoints

### 3.1 List Accounts

**GET** `/accounting/accounts`

List all accounts with optional filters.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| page | int | Page number (default: 1) |
| per_page | int | Items per page (default: 50) |
| account_type | string | Filter by type (asset/liability/equity/revenue/expense) |
| is_active | bool | Filter by active status |
| search | string | Search in code or name |
| parent_id | int | Filter by parent account |

**Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "code": "111",
      "name_vi": "Tiền mặt",
      "account_type": "asset",
      "normal_balance": "debit",
      "is_postable": true,
      "is_active": true,
      "level": 1
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 50,
    "total": 150,
    "pages": 3
  }
}
```

---

### 3.2 Get Account

**GET** `/accounting/accounts/{id}`

Get single account by ID.

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "code": "111",
    "name_vi": "Tiền mặt",
    "name_en": "Cash on Hand",
    "account_type": "asset",
    "normal_balance": "debit",
    "is_postable": true,
    "is_active": true,
    "level": 1,
    "parent_id": null,
    "balance": 50000000.00
  }
}
```

---

### 3.3 Create Account

**POST** `/accounting/accounts`

Create new account.

**Request:**
```json
{
  "code": "1111",
  "name_vi": "Tiền mặt VND",
  "name_en": "Cash VND",
  "parent_id": 1,
  "account_type": "asset",
  "normal_balance": "debit",
  "is_postable": true
}
```

**Response (201):**
```json
{
  "status": "success",
  "message": "Account created successfully",
  "data": {
    "id": 10,
    "code": "1111",
    "name_vi": "Tiền mặt VND"
  }
}
```

---

### 3.4 Update Account

**PUT** `/accounting/accounts/{id}`

Update account.

**Request:**
```json
{
  "name_vi": "Tiền mặt VNĐ",
  "is_active": false
}
```

**Response (200):**
```json
{
  "status": "success",
  "message": "Account updated successfully"
}
```

---

### 3.5 Delete Account

**DELETE** `/accounting/accounts/{id}`

Soft delete account (set is_active=False).

**Response (200):**
```json
{
  "status": "success",
  "message": "Account deactivated successfully"
}
```

---

### 3.6 Get Account Balance

**GET** `/accounting/accounts/{id}/balance`

Get account balance.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| as_of_date | date | Balance as of date (YYYY-MM-DD) |

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "account_id": 1,
    "account_code": "111",
    "account_name": "Tiền mặt",
    "as_of_date": "2026-03-19",
    "opening_debit": 0.00,
    "opening_credit": 0.00,
    "period_debit": 100000000.00,
    "period_credit": 50000000.00,
    "closing_debit": 50000000.00,
    "closing_credit": 0.00,
    "balance": 50000000.00,
    "normal_balance": "debit"
  }
}
```

---

## 4. Journal Endpoints

### 4.1 List Vouchers

**GET** `/accounting/vouchers`

List journal vouchers.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| page | int | Page number |
| per_page | int | Items per page |
| status | string | Filter by status |
| voucher_type | string | Filter by type |
| start_date | date | Filter from date |
| end_date | date | Filter to date |
| search | string | Search voucher no or description |

**Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "voucher_no": "JV-2026-00001",
      "voucher_date": "2026-03-19",
      "voucher_type": "general",
      "description": "Hoa don ban hang",
      "status": "posted",
      "total_debit": 110000000.00,
      "total_credit": 110000000.00,
      "created_by": "admin",
      "created_at": "2026-03-19T10:00:00Z"
    }
  ],
  "pagination": {...}
}
```

---

### 4.2 Get Voucher

**GET** `/accounting/vouchers/{id}`

Get voucher with entries.

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "voucher_no": "JV-2026-00001",
    "voucher_date": "2026-03-19",
    "voucher_type": "general",
    "description": "Hoa don ban hang",
    "reference": "HD-001",
    "status": "posted",
    "entries": [
      {
        "id": 1,
        "account_id": 1,
        "account_code": "111",
        "account_name": "Tiền mặt",
        "debit": 110000000.00,
        "credit": 0.00,
        "description": "Thu tien ban hang",
        "cost_center": null,
        "customer_id": 1
      },
      {
        "id": 2,
        "account_id": 5,
        "account_code": "511",
        "account_name": "Doanh thu ban hang",
        "debit": 0.00,
        "credit": 100000000.00,
        "description": "Doanh thu",
        "cost_center": null,
        "customer_id": 1
      }
    ],
    "total_debit": 110000000.00,
    "total_credit": 110000000.00,
    "is_balanced": true
  }
}
```

---

### 4.3 Create Voucher

**POST** `/accounting/vouchers`

Create journal voucher.

**Request:**
```json
{
  "voucher_date": "2026-03-19",
  "voucher_type": "general",
  "description": "Hoa don ban hang",
  "reference": "HD-001",
  "entries": [
    {
      "account_id": 1,
      "debit": 110000000.00,
      "credit": 0.00,
      "description": "Thu tien",
      "customer_id": 1
    },
    {
      "account_id": 5,
      "debit": 0.00,
      "credit": 100000000.00,
      "description": "Doanh thu"
    },
    {
      "account_id": 8,
      "debit": 0.00,
      "credit": 10000000.00,
      "description": "VAT 10%"
    }
  ]
}
```

**Response (201):**
```json
{
  "status": "success",
  "message": "Voucher created successfully",
  "data": {
    "id": 2,
    "voucher_no": "JV-2026-00002",
    "is_balanced": true
  }
}
```

**Response (400 - Unbalanced):**
```json
{
  "status": "error",
  "message": "Voucher is not balanced. Debit: 110000000.00, Credit: 120000000.00"
}
```

---

### 4.4 Update Voucher

**PUT** `/accounting/vouchers/{id}`

Update voucher (only draft vouchers).

**Request:**
```json
{
  "description": "Updated description",
  "entries": [...]
}
```

**Response (200):**
```json
{
  "status": "success",
  "message": "Voucher updated successfully"
}
```

---

### 4.5 Post Voucher

**POST** `/accounting/vouchers/{id}/post`

Post voucher to ledger.

**Response (200):**
```json
{
  "status": "success",
  "message": "Voucher posted successfully"
}
```

---

### 4.6 Cancel Voucher

**POST** `/accounting/vouchers/{id}/cancel`

Cancel voucher (reverse entries).

**Response (200):**
```json
{
  "status": "success",
  "message": "Voucher cancelled successfully"
}
```

---

## 5. Ledger Endpoints

### 5.1 Get Account Ledger

**GET** `/accounting/ledger/{account_id}`

Get ledger for specific account.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| start_date | date | Start date |
| end_date | date | End date |
| cost_center | string | Filter by cost center |
| page | int | Page number |
| per_page | int | Items per page |

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "account": {
      "id": 1,
      "code": "111",
      "name_vi": "Tiền mặt"
    },
    "opening_balance": 0.00,
    "opening_debit": 0.00,
    "opening_credit": 0.00,
    "entries": [
      {
        "id": 1,
        "voucher_no": "JV-2026-00001",
        "voucher_date": "2026-03-19",
        "description": "Thu tien",
        "debit": 100000000.00,
        "credit": 0.00,
        "balance": 100000000.00
      }
    ],
    "closing_balance": 50000000.00,
    "total_debit": 100000000.00,
    "total_credit": 50000000.00
  }
}
```

---

### 5.2 Get Trial Balance

**GET** `/accounting/ledger/trial-balance`

Get trial balance.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| end_date | date | Balance date |

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "as_of_date": "2026-03-19",
    "accounts": [
      {
        "account_code": "111",
        "account_name": "Tiền mặt",
        "debit": 50000000.00,
        "credit": 0.00
      }
    ],
    "totals": {
      "total_debit": 500000000.00,
      "total_credit": 500000000.00
    },
    "is_balanced": true
  }
}
```

---

## 6. Financial Report Endpoints

### 6.1 Balance Sheet (B01)

**GET** `/financial/api/balance-sheet`

Get Balance Sheet data.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| end_date | date | Report end date |

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "report_date": "2026-03-19",
    "assets": {
      "current_assets": {...},
      "fixed_assets": {...}
    },
    "liabilities": {...},
    "equity": {...},
    "total_liabilities_and_equity": 500000000.00
  }
}
```

---

### 6.2 Income Statement (B02)

**GET** `/financial/api/income-statement`

Get Income Statement data.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| start_date | date | Report start date |
| end_date | date | Report end date |

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "start_date": "2026-01-01",
    "end_date": "2026-03-19",
    "revenue": {...},
    "cost_of_goods_sold": {...},
    "gross_profit": 200000000.00,
    "operating_expenses": {...},
    "net_profit": 150000000.00
  }
}
```

---

### 6.3 Cash Flow Statement (B03)

**GET** `/financial/api/cash-flow`

Get Cash Flow Statement (Indirect Method).

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| start_date | date | Report start date |
| end_date | date | Report end date |

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "start_date": "2026-01-01",
    "end_date": "2026-03-19",
    "cash_from_operations": 100000000.00,
    "cash_from_investing": -50000000.00,
    "cash_from_financing": 0.00,
    "net_cash_flow": 50000000.00,
    "opening_cash": 0.00,
    "closing_cash": 50000000.00
  }
}
```

---

## 7. Partner Endpoints

### 7.1 List Customers

**GET** `/partner/api/customers`

List customers.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| search | string | Search name/code |
| customer_type | string | Filter by type |
| is_active | bool | Filter by status |

**Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "code": "CUS-2026-0001",
      "name": "Cong ty ABC",
      "tax_id": "0123456789",
      "email": "abc@example.com",
      "outstanding_balance": 50000000.00,
      "is_active": true
    }
  ]
}
```

---

### 7.2 Get Customer

**GET** `/partner/api/customers/{id}`

Get customer with AR aging.

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "code": "CUS-2026-0001",
    "name": "Cong ty ABC",
    "tax_id": "0123456789",
    "address": "123 Duong ABC, Quan 1",
    "credit_limit": 100000000.00,
    "payment_terms": 30,
    "outstanding_balance": 50000000.00,
    "ar_aging": {
      "current": 20000000.00,
      "1_30_days": 20000000.00,
      "31_60_days": 10000000.00,
      "61_90_days": 0.00,
      "over_90_days": 0.00
    }
  }
}
```

---

### 7.3 List Vendors

**GET** `/partner/api/vendors`

List vendors.

**Response:** Similar to customers.

---

### 7.4 List Employees

**GET** `/partner/api/employees`

List employees.

**Response:** Similar to customers with advance balance.

---

## 8. Tax Endpoints

### 8.1 Calculate VAT

**POST** `/tax/api/calculate-vat`

Calculate VAT amount.

**Request:**
```json
{
  "amount": 100000000.00,
  "vat_rate": 0.10,
  "vat_type": "output"
}
```

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "gross_amount": 100000000.00,
    "vat_rate": 0.10,
    "vat_amount": 10000000.00,
    "net_amount": 110000000.00
  }
}
```

---

### 8.2 Calculate PIT

**POST** `/tax/api/calculate-pit`

Calculate Personal Income Tax.

**Request:**
```json
{
  "gross_salary": 30000000.00,
  "dependents": 2,
  "insurance": 3000000.00
}
```

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "gross_salary": 30000000.00,
    "taxable_income": 25000000.00,
    "pit_amount": 2500000.00,
    "net_salary": 22500000.00
  }
}
```

---

## 9. Cost Center Endpoints

### 9.1 List Cost Centers

**GET** `/cost-center/api/cost-centers`

List cost centers.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| is_active | bool | Filter by status |
| department | string | Filter by department |

**Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "code": "CC-2026-0001",
      "name": "Phong kinh doanh",
      "department": "Kinh doanh",
      "budget_allocated": 100000000.00,
      "budget_used": 50000000.00,
      "budget_remaining": 50000000.00,
      "is_active": true
    }
  ]
}
```

---

## 10. Project Endpoints

### 10.1 List Projects

**GET** `/project/api/projects`

List projects.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| status | string | Filter by status |
| is_active | bool | Filter by status |

**Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "code": "PRJ-2026-0001",
      "name": "Du an A",
      "customer_id": 1,
      "status": "active",
      "total_contract_value": 500000000.00,
      "total_revenue": 250000000.00,
      "total_expense": 150000000.00,
      "profit": 100000000.00,
      "completion_percentage": 50.00,
      "is_active": true
    }
  ]
}
```

---

## 11. Tax Payment Endpoints

### 11.1 List Tax Payments

**GET** `/tax-payment/api/tax-payments`

List tax payments.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| tax_type | string | Filter by type (vat/cit/pit) |
| status | string | Filter by status |
| period_year | int | Filter by year |

**Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "payment_no": "TVA-2026-00001",
      "tax_type": "vat",
      "period_year": 2026,
      "period_month": 3,
      "taxable_amount": 100000000.00,
      "tax_amount": 10000000.00,
      "payment_status": "pending",
      "due_date": "2026-04-20",
      "is_overdue": false
    }
  ]
}
```

---

## 12. Dashboard & Utility Endpoints

### 12.1 KPI Summary

**GET** `/api/v1/kpi/summary`

Get real-time KPI summary for header display.

**Response (200):**
```json
{
  "total_debit": 500000000.00,
  "total_credit": 480000000.00,
  "difference": 20000000.00,
  "period": "03/2026"
}
```

---

### 12.2 Notification Count

**GET** `/api/v1/notifications/count`

Get unread notification count.

**Response (200):**
```json
{
  "count": 5
}
```

---

### 12.3 Global Search

**GET** `/api/v1/search?q={query}`

Search across vouchers, accounts, and partners.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| q | string | Search query (required) |

**Response (200):**
```json
{
  "results": [
    {
      "type": "CT",
      "title": "JV-2026-00001 - Thu tiền bán hàng",
      "meta": "19/03/2026",
      "url": "/accounting/voucher/1",
      "icon": "fa-file-invoice"
    },
    {
      "type": "TK",
      "title": "111 - Tiền mặt",
      "meta": "asset",
      "url": "/accounting/ledger/1",
      "icon": "fa-sitemap"
    },
    {
      "type": "KH",
      "title": "CUS-001 - Công ty ABC",
      "meta": "Khách hàng",
      "url": "/partner/1",
      "icon": "fa-address-book"
    }
  ]
}
```

---

## 13. API Response Format

### 12.1 Success Response

```json
{
  "status": "success",
  "data": { ... },
  "message": "Operation successful",
  "pagination": {
    "page": 1,
    "per_page": 50,
    "total": 100,
    "pages": 2
  }
}
```

### 12.2 Error Response

```json
{
  "status": "error",
  "message": "Error description",
  "errors": {
    "field_name": ["Error details"]
  }
}
```

### 12.3 HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 422 | Validation Error |
| 500 | Internal Server Error |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-03-17 | Initial API documentation |
| 2.0 | 2026-03-19 | Added financial, partner, tax endpoints |
| 2.3 | 2026-03-19 | Added dashboard KPI, search, notification endpoints |

---

**Document Status:** Active  
**Next Update:** Upon API changes
