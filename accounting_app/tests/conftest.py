"""
Pytest configuration and fixtures for all tests.
Shared across: core/, e2e/, and root test_*.py files.
"""

import os
import sys
import threading
import time
import warnings

import pytest

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, APP_DIR)

warnings.filterwarnings("ignore", message="unclosed database", category=ResourceWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning, module="sqlalchemy")

from app import create_app
from core.database import db
from models.account import Account, AccountType, NormalBalance
from core.security import User, Role, create_default_roles

BASE_URL = "http://127.0.0.1:8765"
TEST_USER = "admin"
TEST_PASS = "admin123"

# ========================================================================
# Core Fixtures (for unit/integration tests)
# ========================================================================


@pytest.fixture(scope="function")
def app():
    """Create application for testing with seeded data."""
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
    """Flask test client (alias for test_client)."""
    return app.test_client()


@pytest.fixture(scope="function")
def test_client(app):
    """Flask test client for unit/integration tests.

    Usage:
        def test_login_page(test_client):
            resp = test_client.get("/auth/login")
            assert resp.status_code == 200
    """
    return app.test_client()


@pytest.fixture(scope="function")
def db_session(app):
    """Database session for testing."""
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
    """Get the test user."""
    with app.app_context():
        return User.query.filter_by(username="testuser").first()


@pytest.fixture
def logged_in_client(client, app, test_user):
    """Logged-in test client via session."""
    with client.session_transaction() as sess:
        sess["_user_id"] = str(test_user.id)
        sess["_fresh"] = True
    return client


# ========================================================================
# Flask App (session-scoped, for Playwright)
# ========================================================================


@pytest.fixture(scope="session")
def flask_app():
    """Flask app with TESTING=True (session-scoped for Playwright)."""
    app = create_app("testing")
    app.config["WTF_CSRF_ENABLED"] = False
    return app


# ========================================================================
# Playwright Fixtures
# ========================================================================

_server_instance = None


@pytest.fixture(scope="session")
def flask_server(flask_app):
    """Start a live Flask WSGI server for Playwright browser tests.

    Returns the base URL (e.g., http://127.0.0.1:8765).
    """
    global _server_instance
    from werkzeug.serving import make_server

    _server_instance = make_server("127.0.0.1", 8765, flask_app, threaded=True)
    thread = threading.Thread(target=_server_instance.serve_forever, daemon=True)
    thread.start()

    import urllib.request
    for _ in range(20):
        try:
            urllib.request.urlopen(BASE_URL, timeout=1)
            break
        except Exception:
            time.sleep(0.5)

    yield BASE_URL

    if _server_instance:
        _server_instance.shutdown()
        _server_instance = None


@pytest.fixture(scope="session")
def browser(flask_server):
    """Launch a Chromium browser for the entire test session."""
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        yield b
        b.close()


@pytest.fixture(scope="function")
def page(browser):
    """Fresh browser page per test (isolated context)."""
    context = browser.new_context(viewport={"width": 1280, "height": 800})
    pg = context.new_page()
    yield pg
    context.close()


@pytest.fixture(scope="function")
def authenticated_page(page, flask_server, request):
    """Auto-logged-in page using admin/admin123.

    Saves screenshot to tests/e2e/snapshots/ on test failure.

    Usage:
        def test_dashboard(authenticated_page):
            authenticated_page.goto(f"{authenticated_page._base_url}/")
    """
    page.goto(f"{flask_server}/auth/login")
    page.wait_for_load_state("networkidle")
    page.fill("#username", TEST_USER)
    page.fill("#password", TEST_PASS)
    page.click('button[type="submit"]')
    page.wait_for_load_state("networkidle")

    page._base_url = flask_server
    yield page

    # Auto-screenshot on failure
    if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
        snapshot = _get_snapshot_dir()
        name = request.node.name
        ts = int(time.time())
        try:
            page.screenshot(path=os.path.join(snapshot, f"{name}_{ts}.png"), full_page=True)
        except Exception:
            pass


# ========================================================================
# Snapshot Directory
# ========================================================================


def _get_snapshot_dir():
    """Create and return the snapshot directory."""
    snapshot = os.path.join(os.path.dirname(__file__), "e2e", "snapshots")
    os.makedirs(snapshot, exist_ok=True)
    return snapshot


@pytest.fixture(scope="session")
def snapshot_dir():
    """Directory for storing screenshots on test failure."""
    return _get_snapshot_dir()


# ========================================================================
# Hooks
# ========================================================================


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Store test result on item for fixture inspection (screenshot on fail)."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)
