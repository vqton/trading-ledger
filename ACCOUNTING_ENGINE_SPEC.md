# ACCOUNTING_ENGINE_SPEC.md

# Accounting Engine Specification

This document defines the **core accounting logic**.

The engine must comply with:

Vietnamese Accounting Standards (VAS)

Double-entry bookkeeping

---

# Core Rule

Every transaction must satisfy:

Total Debit = Total Credit

Validation must occur before saving.

---

# Voucher Lifecycle

Draft

Posted

Locked

Cancelled

---

# Voucher Creation Flow

User creates voucher

↓

User adds journal entries

↓

System validates debit/credit

↓

Voucher saved as draft

↓

Accountant posts voucher

↓

Ledger updated

---

# Journal Entry Structure

Each journal entry must include:

account_id

debit

credit

description

reference

Rules:

Only one of debit or credit can be non-zero.

---

# Example Transaction

Buy office supplies in cash.

Debit:

642 Operating Expense

Credit:

111 Cash

Example entries:

Account: 642  
Debit: 500000  

Account: 111  
Credit: 500000  

---

# Ledger Generation

Ledger must be derived from journal entries.

Fields:

account_id

date

debit

credit

balance

---

# Trial Balance Logic

Trial balance aggregates:

SUM(debit)

SUM(credit)

Validation:

Total debit = Total credit

---

# Balance Sheet Logic

Assets = Liabilities + Equity

Assets include:

Cash  
Bank  
Receivables  
Inventory  

Liabilities include:

Payables  
Taxes  

Equity includes:

Owner capital  
Retained earnings  

---

# Income Statement Logic

Revenue accounts:

5xx

Expense accounts:

6xx

Profit calculation:

Profit = Revenue - Expenses

---

# Inventory Accounting

Supported valuation methods:

FIFO

Weighted Average

Transactions:

Stock In

Stock Out

Adjustments

---

# Audit Logging

Every action must be logged.

Examples:

Voucher created

Voucher modified

Voucher deleted

User login

---

# Performance Rules

Journal queries must be indexed.

Indexes required:

voucher_date

account_id

voucher_id

---

# Error Handling

Engine must detect:

unbalanced journal entries

invalid accounts

posting to inactive accounts

---

# Future Extensions

The engine must support future modules:

multi-company accounting

multi-currency

consolidation

tax automation

ERP integration