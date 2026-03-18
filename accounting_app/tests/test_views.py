import pytest
import json
from app import create_app
from core.database import db
from models.account import Account, AccountType, NormalBalance
from models.journal import JournalVoucher, JournalEntry, VoucherStatus
from core.security import User, Role, create_default_roles


@pytest.fixture(scope="function")
def app():
    """Create application for testing."""
    test_app = create_app("testing")
    
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
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope="function")
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture(scope="function")
def test_user(app):
    """Create test user."""
    with app.app_context():
        user = User.query.filter_by(username="testuser").first()
        return user


@pytest.fixture
def logged_in_client(client, app, test_user):
    """Create logged in test client."""
    with client.session_transaction() as sess:
        sess["_user_id"] = str(test_user.id)
        sess["_fresh"] = True
    
    return client


class TestAccountViews:
    """Test Account CRUD views."""

    def test_accounts_list_view(self, logged_in_client, app):
        """Test accounts list page loads."""
        with app.app_context():
            response = logged_in_client.get("/accounting/accounts")
            assert response.status_code == 200
            assert b"111" in response.data

    def test_accounts_list_requires_login(self, client):
        """Test accounts list requires login."""
        response = client.get("/accounting/accounts", follow_redirects=True)
        assert b"username" in response.data

    def test_create_account_get_view(self, logged_in_client, app):
        """Test create account form loads."""
        with app.app_context():
            response = logged_in_client.get("/accounting/accounts/create")
            assert response.status_code == 200
            assert response.status_code == 200

    def test_create_account_post(self, logged_in_client, app):
        """Test create account via POST."""
        with app.app_context():
            account_count_before = Account.query.count()
            
            response = logged_in_client.post("/accounting/accounts/create", data={
                "account_code": "999",
                "account_name": "Test Inventory",
                "account_type": "asset",
                "normal_balance": "debit",
                "parent_id": "0",
                "is_detail": "y",
                "is_active": "y",
            }, follow_redirects=True)
            
            assert response.status_code == 200
            account_count_after = Account.query.count()
            assert account_count_after == account_count_before + 1
            
            new_account = Account.query.filter_by(code="999").first()
            assert new_account is not None
            assert new_account.name_vi == "Test Inventory"

    def test_create_account_duplicate_code(self, logged_in_client, app):
        """Test create account with duplicate code fails."""
        with app.app_context():
            response = logged_in_client.post("/accounting/accounts/create", data={
                "account_code": "111",
                "account_name": "Cash duplicate",
                "account_type": "ASSET",
                "normal_balance": "DEBIT",
                "is_detail": "y",
                "is_active": "y",
            }, follow_redirects=True)
            
            assert response.status_code == 200
            assert b"exist" in response.data.lower() or b"duplicate" in response.data.lower()

    def test_edit_account_get_view(self, logged_in_client, app):
        """Test edit account form loads."""
        with app.app_context():
            account = Account.query.filter_by(code="111").first()
            response = logged_in_client.get(f"/accounting/accounts/{account.id}/edit")
            assert response.status_code == 200

    def test_edit_account_post(self, logged_in_client, app):
        """Test edit account page loads."""
        with app.app_context():
            account = Account.query.filter_by(code="111").first()
            
            response = logged_in_client.post(f"/accounting/accounts/{account.id}/edit", data={
                "account_code": "111",
                "account_name": "Cash (updated)",
                "account_type": "asset",
                "normal_balance": "debit",
                "parent_id": "0",
                "is_detail": "y",
                "is_active": "y",
            }, follow_redirects=True)
            
            assert response.status_code == 200

    def test_delete_account(self, logged_in_client, app):
        """Test soft delete account."""
        with app.app_context():
            account = Account.query.filter_by(code="112").first()
            account_id = account.id
            
            response = logged_in_client.post(f"/accounting/accounts/{account_id}/delete", follow_redirects=True)
            assert response.status_code == 200
            
            deleted_account = db.session.get(Account, account_id)
            assert deleted_account is not None
            assert deleted_account.is_active is False


class TestJournalViews:
    """Test Journal Voucher CRUD views."""

    def test_journal_list_view(self, logged_in_client, app):
        """Test journal list page loads."""
        with app.app_context():
            response = logged_in_client.get("/accounting/journal")
            assert response.status_code == 200

    def test_journal_list_requires_login(self, client):
        """Test journal list requires login."""
        response = client.get("/accounting/journal", follow_redirects=True)
        assert b"username" in response.data

    def test_create_voucher_get_view(self, logged_in_client, app):
        """Test create voucher form loads."""
        with app.app_context():
            response = logged_in_client.get("/accounting/journal/create")
            assert response.status_code == 200

    def test_create_voucher_post(self, logged_in_client, app, test_user):
        """Test create voucher via POST with balanced entries."""
        with app.app_context():
            cash = Account.query.filter_by(code="111").first()
            revenue = Account.query.filter_by(code="511").first()
            
            voucher_count_before = JournalVoucher.query.count()
            
            response = logged_in_client.post("/accounting/journal/create", data={
                "voucher_date": "2026-03-18",
                "voucher_type": "purchase",
                "description": "Test purchase",
                "entries-0-account_id": str(cash.id),
                "entries-0-debit": "1000000",
                "entries-0-credit": "0",
                "entries-1-account_id": str(revenue.id),
                "entries-1-debit": "0",
                "entries-1-credit": "1000000",
            }, follow_redirects=True)
            
            voucher_count_after = JournalVoucher.query.count()
            assert voucher_count_after == voucher_count_before + 1

    def test_create_voucher_unbalanced_rejected(self, logged_in_client, app):
        """Test create voucher with unbalanced entries is rejected."""
        with app.app_context():
            cash = Account.query.filter_by(code="111").first()
            revenue = Account.query.filter_by(code="511").first()
            
            response = logged_in_client.post("/accounting/journal/create", data={
                "voucher_date": "2026-03-18",
                "voucher_type": "purchase",
                "description": "Test purchase",
                "entries-0-account_id": str(cash.id),
                "entries-0-debit": "1000000",
                "entries-0-credit": "0",
                "entries-1-account_id": str(revenue.id),
                "entries-1-debit": "0",
                "entries-1-credit": "500000",
            }, follow_redirects=True)
            
            assert response.status_code == 200
            assert b"error" in response.data.lower() or b"danger" in response.data.lower()

    def test_view_voucher(self, logged_in_client, app, test_user):
        """Test view voucher details."""
        with app.app_context():
            from datetime import date
            cash = Account.query.filter_by(code="111").first()
            revenue = Account.query.filter_by(code="511").first()
            
            voucher = JournalVoucher(
                voucher_no="PU-00001",
                voucher_date=date(2026, 3, 18),
                voucher_type="purchase",
                description="Test voucher",
                status=VoucherStatus.DRAFT,
                created_by=test_user.id,
            )
            db.session.add(voucher)
            db.session.commit()
            
            entry1 = JournalEntry(
                voucher_id=voucher.id,
                account_id=cash.id,
                line_number=1,
                debit=1000000,
                credit=0,
            )
            entry2 = JournalEntry(
                voucher_id=voucher.id,
                account_id=revenue.id,
                line_number=2,
                debit=0,
                credit=1000000,
            )
            db.session.add(entry1)
            db.session.add(entry2)
            db.session.commit()
            
            response = logged_in_client.get(f"/accounting/journal/{voucher.id}")
            assert response.status_code == 200
            assert b"Test voucher" in response.data

    def test_edit_voucher_draft_only(self, logged_in_client, app, test_user):
        """Test edit voucher works only for draft status."""
        with app.app_context():
            from datetime import date
            cash = Account.query.filter_by(code="111").first()
            revenue = Account.query.filter_by(code="511").first()
            
            voucher = JournalVoucher(
                voucher_no="PU-00002",
                voucher_date=date(2026, 3, 18),
                voucher_type="purchase",
                description="Test voucher",
                status=VoucherStatus.POSTED,
                created_by=test_user.id,
            )
            db.session.add(voucher)
            db.session.commit()
            
            response = logged_in_client.get(f"/accounting/journal/{voucher.id}/edit")
            assert response.status_code == 302

    def test_post_voucher(self, logged_in_client, app, test_user):
        """Test post voucher updates account balances."""
        with app.app_context():
            from datetime import date
            cash = Account.query.filter_by(code="111").first()
            revenue = Account.query.filter_by(code="511").first()
            
            voucher = JournalVoucher(
                voucher_no="PU-00003",
                voucher_date=date(2026, 3, 18),
                voucher_type="purchase",
                description="Test post voucher",
                status=VoucherStatus.DRAFT,
                created_by=test_user.id,
            )
            db.session.add(voucher)
            db.session.commit()
            
            entry1 = JournalEntry(
                voucher_id=voucher.id,
                account_id=cash.id,
                line_number=1,
                debit=500000,
                credit=0,
            )
            entry2 = JournalEntry(
                voucher_id=voucher.id,
                account_id=revenue.id,
                line_number=2,
                debit=0,
                credit=500000,
            )
            db.session.add(entry1)
            db.session.add(entry2)
            db.session.commit()
            
            response = logged_in_client.post(f"/accounting/journal/{voucher.id}/post", follow_redirects=True)
            assert response.status_code == 200
            
            db.session.refresh(voucher)
            
            assert voucher.status == VoucherStatus.POSTED

    def test_delete_voucher_draft_only(self, logged_in_client, app, test_user):
        """Test delete voucher works only for draft status."""
        with app.app_context():
            from datetime import date
            voucher = JournalVoucher(
                voucher_no="PU-00004",
                voucher_date=date(2026, 3, 18),
                voucher_type="purchase",
                description="Test delete",
                status=VoucherStatus.POSTED,
                created_by=test_user.id,
            )
            db.session.add(voucher)
            db.session.commit()
            
            response = logged_in_client.post(f"/accounting/journal/{voucher.id}/delete", follow_redirects=True)
            assert response.status_code == 200
            assert b"cannot" in response.data.lower() or b"delete" in response.data.lower()


class TestReportViews:
    """Test Report views."""

    def test_ledger_view(self, logged_in_client, app):
        """Test ledger page loads."""
        with app.app_context():
            response = logged_in_client.get("/accounting/ledger")
            assert response.status_code == 200

    def test_trial_balance_view(self, logged_in_client, app):
        """Test trial balance page loads."""
        with app.app_context():
            response = logged_in_client.get("/accounting/ledger/trial-balance")
            assert response.status_code == 200

    def test_balance_sheet_view(self, logged_in_client, app):
        """Test balance sheet page loads."""
        with app.app_context():
            response = logged_in_client.get("/accounting/reports/balance-sheet")
            assert response.status_code == 200

    def test_income_statement_view(self, logged_in_client, app):
        """Test income statement page loads."""
        with app.app_context():
            response = logged_in_client.get("/accounting/reports/income-statement")
            assert response.status_code == 200


class TestApiEndpoints:
    """Test API endpoints."""

    def test_api_accounts_list(self, logged_in_client, app):
        """Test accounts API returns JSON."""
        with app.app_context():
            response = logged_in_client.get("/accounting/api/accounts")
            assert response.status_code == 200
            assert response.is_json
            
            data = response.get_json()
            assert isinstance(data, list)
