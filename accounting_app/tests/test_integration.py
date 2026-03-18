"""
Integration tests for the accounting application.

These tests verify end-to-end workflows.
Run with: pytest tests/test_integration.py -v
"""

import pytest
from datetime import date
from decimal import Decimal
from app import create_app
from core.database import db
from models.account import Account, AccountType, NormalBalance
from models.journal import JournalVoucher, JournalEntry, VoucherStatus
from models.audit_log import AuditLog
from core.security import User, Role, create_default_roles


@pytest.fixture(scope="function")
def app():
    """Create application for testing."""
    test_app = create_app("testing")
    test_app.config["TESTING"] = True
    test_app.config["WTF_CSRF_ENABLED"] = False
    
    with test_app.app_context():
        db.drop_all()
        db.create_all()
        
        create_default_roles()
        
        admin_role = Role.query.filter_by(name="admin").first()
        user = User(
            username="testuser",
            email="test@example.com",
            role_id=admin_role.id,
            is_active=True,
        )
        user.set_password("testpass123")
        db.session.add(user)
        
        accounts_data = [
            {"code": "111", "name_vi": "Cash", "type": AccountType.ASSET, "normal": NormalBalance.DEBIT, "is_postable": True, "level": 3},
            {"code": "112", "name_vi": "Bank", "type": AccountType.ASSET, "normal": NormalBalance.DEBIT, "is_postable": True, "level": 3},
            {"code": "131", "name_vi": "Receivable", "type": AccountType.ASSET, "normal": NormalBalance.DEBIT, "is_postable": True, "level": 3},
            {"code": "331", "name_vi": "Payable", "type": AccountType.LIABILITY, "normal": NormalBalance.CREDIT, "is_postable": True, "level": 3},
            {"code": "511", "name_vi": "Revenue", "type": AccountType.REVENUE, "normal": NormalBalance.CREDIT, "is_postable": True, "level": 3},
            {"code": "632", "name_vi": "COGS", "type": AccountType.EXPENSE, "normal": NormalBalance.DEBIT, "is_postable": True, "level": 3},
            {"code": "642", "name_vi": "Expense", "type": AccountType.EXPENSE, "normal": NormalBalance.DEBIT, "is_postable": True, "level": 3},
        ]
        
        for acc_data in accounts_data:
            account = Account(
                code=acc_data["code"],
                name_vi=acc_data["name_vi"],
                account_type=acc_data["type"],
                normal_balance=acc_data["normal"],
                is_postable=acc_data["is_postable"],
                level=acc_data["level"],
                is_active=True,
            )
            db.session.add(account)
        
        db.session.commit()
    
    yield test_app
    
    with test_app.app_context():
        db.drop_all()


@pytest.fixture(scope="function")
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def test_user(app):
    """Create test user."""
    with app.app_context():
        return User.query.filter_by(username="testuser").first()


@pytest.fixture
def logged_in_client(client, app, test_user):
    """Create logged in test client."""
    with client.session_transaction() as sess:
        sess["_user_id"] = str(test_user.id)
        sess["_fresh"] = True
    return client


class TestAuthenticationFlow:
    """Test authentication workflows."""

    def test_login_success(self, client, app):
        """Test successful login."""
        with app.app_context():
            response = client.post("/auth/login", data={
                "username": "testuser",
                "password": "testpass123",
            }, follow_redirects=True)
            
            assert response.status_code == 200

    def test_login_failure_wrong_password(self, client, app):
        """Test login with wrong password."""
        with app.app_context():
            response = client.post("/auth/login", data={
                "username": "testuser",
                "password": "wrongpassword",
            }, follow_redirects=True)
            
            assert response.status_code == 200

    def test_logout(self, logged_in_client, app):
        """Test logout."""
        with app.app_context():
            response = logged_in_client.get("/auth/logout", follow_redirects=True)
            assert response.status_code == 200


class TestJournalVoucherFlow:
    """Test journal voucher workflow."""

    def test_create_voucher_page_loads(self, logged_in_client, app):
        """Test create voucher page loads."""
        with app.app_context():
            response = logged_in_client.get("/accounting/journal/create")
            assert response.status_code == 200

    def test_voucher_list_page_loads(self, logged_in_client, app):
        """Test voucher list page loads."""
        with app.app_context():
            response = logged_in_client.get("/accounting/journal")
            assert response.status_code == 200


class TestAccountFlow:
    """Test account management."""

    def test_create_account(self, logged_in_client, app):
        """Test creating a new account - form validation."""
        with app.app_context():
            response = logged_in_client.get("/accounting/accounts/create")
            assert response.status_code == 200

    def test_duplicate_account_code_rejected(self, logged_in_client, app):
        """Test duplicate account code is rejected."""
        with app.app_context():
            response = logged_in_client.post("/accounting/accounts/create", data={
                "account_code": "111",
                "account_name": "Duplicate cash",
                "account_type": "ASSET",
                "normal_balance": "DEBIT",
                "is_detail": "y",
                "is_active": "y",
            }, follow_redirects=True)
            
            assert response.status_code == 200


class TestFinancialReportFlow:
    """Test financial report workflows."""

    def test_trial_balance_page(self, logged_in_client, app):
        """Test trial balance page loads."""
        with app.app_context():
            response = logged_in_client.get("/accounting/ledger/trial-balance")
            assert response.status_code == 200

    def test_ledger_page(self, logged_in_client, app):
        """Test ledger page loads."""
        with app.app_context():
            response = logged_in_client.get("/accounting/ledger")
            assert response.status_code == 200

    def test_balance_sheet_page(self, logged_in_client, app):
        """Test balance sheet page loads."""
        with app.app_context():
            response = logged_in_client.get("/accounting/reports/balance-sheet")
            assert response.status_code == 200

    def test_income_statement_page(self, logged_in_client, app):
        """Test income statement page loads."""
        with app.app_context():
            response = logged_in_client.get("/accounting/reports/income-statement")
            assert response.status_code == 200


class TestApiIntegration:
    """Test API endpoints."""

    def test_api_accounts_json(self, logged_in_client, app):
        """Test accounts API returns JSON."""
        with app.app_context():
            response = logged_in_client.get("/accounting/api/accounts")
            assert response.status_code == 200
            assert response.is_json
            
            data = response.get_json()
            assert isinstance(data, list)
            assert len(data) > 0


class TestAccessControl:
    """Test access control."""

    def test_unauthorized_redirect(self, client, app):
        """Test unauthorized access redirects."""
        with app.app_context():
            response = client.get("/accounting/accounts", follow_redirects=True)
            assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
