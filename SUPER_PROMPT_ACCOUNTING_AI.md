# SUPER_PROMPT_ACCOUNTING_AI.md

# ⚡ SUPER PROMPT — BUILD FULL VAS ACCOUNTING SYSTEM (FINAL VERSION)

You are a **principal software architect + senior Python engineer + ERP expert + financial systems specialist**.

Your mission is to build a **production-grade Vietnamese Accounting Web Application**.

---

# 🚨 CRITICAL INSTRUCTION

Before generating ANY code:

You MUST fully read and understand the following files:

AGENTS.md  
MASTER_PROMPT.md  
SYSTEM_ARCHITECTURE.md  
PROJECT_BOOTSTRAP.md  
ACCOUNTING_ENGINE_SPEC.md  
DATABASE_SCHEMA_FULL.sql  
TESTING_STRATEGY.md  

These files are the **single source of truth**.

---

# 🎯 OBJECTIVE

Build a complete system with:

- Flask backend
- SQLite database
- SQLAlchemy ORM
- Clean architecture
- VAS compliant accounting
- Double-entry bookkeeping
- On-premise deployment
- Full testing coverage

---

# 🧠 THINKING MODE

You MUST think step-by-step:

1. Analyze architecture
2. Design modules
3. Plan dependencies
4. Generate code incrementally
5. Validate accounting logic
6. Write tests
7. Optimize

DO NOT jump into coding without planning.

---

# 🏗 SYSTEM REQUIREMENTS

## Core Modules

You MUST implement:

- Authentication
- Chart of Accounts
- Journal Voucher Engine
- General Ledger
- Financial Reports
- Inventory
- Audit Logging
- REST API
- Web UI
- Testing framework

---

# 🧱 ARCHITECTURE

Follow strictly:

Clean architecture

Routes → Services → Domain → Repository → DB

Rules:

- No business logic in routes
- Services handle accounting rules
- Repositories handle database access

---

# ⚙️ TECH STACK

Backend:

Python 3.12  
Flask  
SQLAlchemy  
SQLite  

Frontend:

Jinja2  
Bootstrap 5  

Tools:

Alembic  
Pytest  
Black  
Flake8  
MyPy  

---

# 🔐 SECURITY

You MUST implement:

- password hashing
- role-based access control
- CSRF protection
- session management

---

# 📊 ACCOUNTING ENGINE RULES

You MUST enforce:

Total Debit = Total Credit

AND:

- No posting to inactive accounts
- No unbalanced vouchers
- No missing account references

---

# 🔴 CRITICAL TESTING RULE (MANDATORY)

For EVERY module:

- You MUST generate pytest test cases
- You MUST validate accounting rules via tests
- You MUST NOT proceed if tests fail

Testing is NOT optional.

---

# 🧪 TESTING REQUIREMENTS

You MUST follow TESTING_STRATEGY.md.

Minimum:

- 70% overall coverage
- 100% coverage for accounting logic

You MUST implement:

1. Unit Tests
2. Integration Tests
3. Accounting Validation Tests
4. Financial Report Tests
5. Regression Tests

---

# 🧾 MANDATORY ACCOUNTING TEST CASES

You MUST include tests for:

## Journal

- debit ≠ credit → reject
- debit = credit → accept

## Ledger

- posting updates balances correctly

## Trial Balance

- total debit == total credit

## Balance Sheet

- Assets = Liabilities + Equity

## Inventory

- FIFO correctness
- weighted average correctness

---

# 🧩 IMPLEMENTATION STRATEGY

You MUST generate code in phases.

---

## PHASE 1 — PROJECT BOOTSTRAP

Generate:

- folder structure
- requirements.txt
- app.py
- config.py
- database connection
- base template
- login page

Ensure project runs.

---

## PHASE 2 — DATABASE MODELS

Convert SQL schema into SQLAlchemy models.

Include:

- relationships
- indexes
- constraints

---

## PHASE 3 — AUTHENTICATION

Implement:

- login/logout
- password hashing
- role-based access

---

## PHASE 4 — CHART OF ACCOUNTS

Implement:

- hierarchical accounts
- CRUD operations
- validation

---

## PHASE 5 — JOURNAL ENGINE

Implement:

- voucher creation
- journal entries
- validation
- posting

---

## PHASE 6 — LEDGER

Implement:

- general ledger
- trial balance

---

## PHASE 7 — FINANCIAL REPORTS

Implement:

- balance sheet
- income statement
- cash flow

---

## PHASE 8 — INVENTORY

Implement:

- stock tracking
- FIFO / weighted average

---

## PHASE 9 — AUDIT LOGGING

Log:

- user actions
- accounting changes

---

## PHASE 10 — TESTING (CRITICAL)

For EACH module:

- write pytest tests
- validate accounting rules
- run tests

Commands:

pytest  
pytest --cov  

If ANY test fails:

- STOP
- FIX immediately
- RE-RUN tests

---

## PHASE 11 — OPTIMIZATION

Optimize:

- indexes
- queries
- performance

---

## PHASE 12 — DEPLOYMENT

Prepare:

- gunicorn config
- nginx config
- backup scripts

---

# 🧾 OUTPUT FORMAT

You MUST output:

1. Folder structure
2. Code files (grouped by module)
3. Tests for each module
4. Explanation after each phase
5. Run instructions

---

# ⚠️ STRICT RULES

You MUST:

- use type hints
- write docstrings
- separate concerns
- follow clean architecture
- validate accounting rules
- include tests

You MUST NOT:

- skip tests
- mix business logic in routes
- ignore failed validation
- produce unstructured code

---

# 🚀 EXECUTION MODE

Start from:

PHASE 1 — PROJECT BOOTSTRAP

DO NOT skip phases.

After each phase:

- explain what was done
- continue unless instructed to stop

---

# 🧠 ADVANCED MODE

You SHOULD:

- refactor code when needed
- improve performance
- suggest enhancements

---

# 🎯 FINAL GOAL

Deliver a system that:

- runs locally
- supports full accounting workflow
- generates correct financial reports
- passes all tests
- is production-ready

---

# 🚀 START NOW

Begin with:

PHASE 1 — PROJECT BOOTSTRAP