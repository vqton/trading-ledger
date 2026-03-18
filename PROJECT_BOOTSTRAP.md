# PROJECT_BOOTSTRAP.md

# Project Bootstrap Instructions

This document instructs AI agents how to **generate the entire accounting system project skeleton**.

The system must follow:

- Clean architecture
- Flask backend
- SQLite database
- SQLAlchemy ORM
- Modular structure
- Enterprise-level maintainability

---

# Step 1: Create Project Structure

Generate the following folder structure.

accounting_app/

    app.py
    config.py
    requirements.txt
    README.md

    core/
        database.py
        security.py
        logging.py

    models/
        user.py
        account.py
        journal_voucher.py
        journal_entry.py
        item.py
        warehouse.py
        stock_transaction.py

    repositories/
        user_repository.py
        account_repository.py
        journal_repository.py

    services/
        auth_service.py
        accounting_service.py
        inventory_service.py
        report_service.py

    routes/
        auth_routes.py
        account_routes.py
        journal_routes.py
        report_routes.py

    reports/
        balance_sheet.py
        income_statement.py
        trial_balance.py

    templates/
        base.html
        login.html
        dashboard.html

    static/
        css/
        js/

    migrations/

    tests/
        test_auth.py
        test_accounts.py
        test_journal.py

---

# Step 2: Generate requirements.txt

Include the following dependencies.

Flask
Flask-Login
Flask-WTF
SQLAlchemy
Alembic
Pandas
OpenPyXL
python-dotenv
gunicorn
pytest
black
flake8
mypy

---

# Step 3: Initialize Database Layer

File:

core/database.py

Responsibilities:

- initialize SQLAlchemy engine
- session management
- database connection

Example responsibilities:

create_engine  
sessionmaker  
Base model class  

---

# Step 4: Configure Application

config.py must support:

Development mode

SQLite database

Environment variables

Example variables:

SECRET_KEY  
DATABASE_URL  

---

# Step 5: Generate app.py

Responsibilities:

Initialize Flask application

Register blueprints

Initialize extensions

Example components:

Flask  
SQLAlchemy  
LoginManager  

---

# Step 6: Initialize Migration System

Use Alembic.

Commands:

alembic init migrations

alembic revision --autogenerate

alembic upgrade head

---

# Step 7: Generate Basic UI

Create base template:

templates/base.html

Include:

Bootstrap 5

Navigation bar

Sidebar

Content blocks

---

# Step 8: Implement Login Page

templates/login.html

Features:

username field

password field

login button

error messages

---

# Step 9: Generate Dashboard

templates/dashboard.html

Show:

number of accounts

recent vouchers

financial summary

---

# Step 10: Run Application

Development:

flask run

Production:

gunicorn app:app

---

# Expected Result

After bootstrap, the project must:

- run successfully
- show login page
- connect to database
- support migrations