"""
Pytest configuration and fixtures for accounting tests.
"""

import pytest
import sys
import os
import warnings

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

warnings.filterwarnings("ignore", message="unclosed database", category=ResourceWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning, module="sqlalchemy")

from app import create_app
from core.database import db
from models.account import Account, AccountType, NormalBalance
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
            {"code": "111", "name_vi": "Tiền mặt", "type": AccountType.ASSET, "normal": NormalBalance.DEBIT, "is_postable": True, "level": 1},
            {"code": "112", "name_vi": "Tiền gửi ngân hàng", "type": AccountType.ASSET, "normal": NormalBalance.DEBIT, "is_postable": True, "level": 1},
            {"code": "1311", "name_vi": "Phải thu khách hàng", "type": AccountType.ASSET, "normal": NormalBalance.DEBIT, "is_postable": True, "level": 2},
            {"code": "332", "name_vi": "Phải trả, phải nộp khác", "type": AccountType.LIABILITY, "normal": NormalBalance.CREDIT, "is_postable": True, "level": 1},
            {"code": "511", "name_vi": "Doanh thu bán hàng", "type": AccountType.REVENUE, "normal": NormalBalance.CREDIT, "is_postable": True, "level": 1},
            {"code": "627", "name_vi": "Giá vốn hàng bán", "type": AccountType.EXPENSE, "normal": NormalBalance.DEBIT, "is_postable": True, "level": 1},
            {"code": "635", "name_vi": "Chi phí quản lý DN", "type": AccountType.EXPENSE, "normal": NormalBalance.DEBIT, "is_postable": True, "level": 1},
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
        engine = db.engine
        if engine:
            engine.dispose()


@pytest.fixture(scope="function")
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture(scope="function")
def db_session(app):
    """Create database session for testing."""
    with app.app_context():
        yield db.session


@pytest.fixture
def sample_accounts(app):
    """Get sample accounts for testing."""
    with app.app_context():
        return {
            "cash": Account.query.filter_by(code="111").first(),
            "bank": Account.query.filter_by(code="112").first(),
            "receivable": Account.query.filter_by(code="1311").first(),
            "payable": Account.query.filter_by(code="332").first(),
            "revenue": Account.query.filter_by(code="511").first(),
            "cogs": Account.query.filter_by(code="627").first(),
            "expense": Account.query.filter_by(code="635").first(),
        }


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
