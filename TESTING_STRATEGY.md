# TESTING_STRATEGY.md

# Accounting System Testing Strategy

This document defines **testing requirements for financial-grade software**.

---

# 1. Testing Philosophy

The system must ensure:

- correctness of financial data
- integrity of accounting rules
- auditability
- regression safety

Testing is NOT optional.

---

# 2. Test Coverage Requirements

Minimum coverage:

70% (code coverage)

BUT:

100% coverage required for:

- accounting engine
- journal validation
- financial reports

---

# 3. Test Types

## 3.1 Unit Tests

Test small components.

Examples:

- account creation
- journal entry validation
- debit/credit rules

---

## 3.2 Integration Tests

Test module interactions.

Examples:

- create voucher → post → update ledger
- generate trial balance

---

## 3.3 Accounting Validation Tests

CRITICAL layer.

Test cases:

- unbalanced journal → must fail
- posting to inactive account → must fail
- missing account → must fail

---

## 3.4 Financial Report Tests

Verify reports:

- trial balance must balance
- balance sheet must satisfy:

Assets = Liabilities + Equity

- income statement correctness

---

## 3.5 Regression Tests

Ensure old features are not broken.

Run automatically after every change.

---

# 4. Mandatory Test Cases

## Journal Validation

- debit ≠ credit → reject
- debit = credit → accept

---

## Ledger Accuracy

- posting updates correct balances
- historical data remains unchanged

---

## Trial Balance

- total debit == total credit

---

## Balance Sheet

- Assets = Liabilities + Equity

---

## Inventory

- FIFO calculation correct
- weighted average correct

---

# 5. Test Data Strategy

Use:

- realistic accounting scenarios
- multiple vouchers
- edge cases

Example:

- zero value transactions
- large transactions
- rounding issues

---

# 6. Automation

Use:

pytest

Run:

pytest --cov

---

# 7. Continuous Testing

Tests must run:

- before commit
- before deployment

---

# 8. Error Handling Tests

Test:

- invalid input
- missing fields
- database failures

---

# 9. Performance Tests

Test:

- large dataset (10k+ entries)
- report generation speed

---

# 10. Audit Validation

Ensure:

- all actions logged
- logs cannot be altered

---

# 11. AI Agent Rules

Agents MUST:

- generate tests with every module
- never skip validation tests
- ensure financial correctness

Agents MUST NOT:

- ignore failed tests
- bypass accounting rules

---

# 12. Definition of Done

A feature is complete ONLY IF:

- code is written
- tests are written
- tests pass
- accounting rules validated