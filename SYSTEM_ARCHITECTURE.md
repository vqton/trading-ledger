```markdown
# SYSTEM_ARCHITECTURE.md

# VAS Accounting System Architecture

## Overview

The system is designed as a **modular accounting platform** that can evolve into a **full ERP system**.

Core principles:

- modular
- auditable
- scalable
- maintainable

---

# High Level Architecture

```

```
            Web Browser
                 |
                 v
           Flask Web Server
                 |
    --------------------------------
    |              |               |
    v              v               v
```

Auth Module   Accounting Core   Reporting
|
v
Domain Services
|
v
Repositories
|
v
Database

```

---

# Core Modules

## Authentication

- login
- logout
- role management

---

## Accounting Engine

Handles:

- journal vouchers
- double-entry logic
- ledger updates

---

## Reporting Engine

Generates:

- trial balance
- balance sheet
- income statement
- cash flow

---

## Inventory Engine

Tracks:

- stock in
- stock out
- valuation

Methods:

```

FIFO
Weighted Average

```

---

# Accounting Data Flow

```

User creates voucher
↓
Voucher validation
↓
Double-entry validation
↓
Journal entries saved
↓
Ledger updated
↓
Reports generated

```

---

# Security Model

Roles:

```

Admin
Accountant
Auditor
Viewer

```

Permissions:

```

create voucher
edit voucher
view reports
manage users

```

---

# Logging & Auditing

Every critical action is logged.

Examples:

- login
- voucher creation
- voucher modification
- account changes

---

# Future ERP Modules

The system is designed to support future modules.

Possible extensions:

```

POS integration
E-invoice integration
Bank API
HR module
Asset management
Budget management
BI dashboards

```

---

# Deployment Model

On-premise infrastructure.

Recommended stack:

```

Linux Server
Gunicorn
Nginx
SQLite

```

Optional enterprise stack:

```

Docker
PostgreSQL
Redis

```
```
