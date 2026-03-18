


```markdown
# DATABASE_SCHEMA_FULL.sql

-- Users

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Chart of Accounts

CREATE TABLE accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_code TEXT NOT NULL,
    account_name TEXT NOT NULL,
    account_type TEXT NOT NULL,
    parent_id INTEGER,
    normal_balance TEXT,
    is_active BOOLEAN DEFAULT 1
);

-- Journal Vouchers

CREATE TABLE journal_vouchers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    voucher_no TEXT UNIQUE,
    voucher_date DATE,
    description TEXT,
    created_by INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Journal Entries

CREATE TABLE journal_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    voucher_id INTEGER,
    account_id INTEGER,
    debit NUMERIC DEFAULT 0,
    credit NUMERIC DEFAULT 0,
    reference TEXT
);

-- Inventory Items

CREATE TABLE items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_code TEXT,
    item_name TEXT,
    unit TEXT
);

-- Warehouses

CREATE TABLE warehouses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    warehouse_name TEXT
);

-- Stock Transactions

CREATE TABLE stock_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER,
    warehouse_id INTEGER,
    quantity NUMERIC,
    transaction_type TEXT,
    transaction_date DATE
);

-- Audit Logs

CREATE TABLE audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT,
    entity TEXT,
    entity_id INTEGER,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    old_value TEXT,
    new_value TEXT,
    ip_address TEXT
);
```

