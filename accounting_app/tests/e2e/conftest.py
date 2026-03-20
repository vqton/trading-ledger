"""
Playwright configuration and fixtures for E2E tests.
Uses Flask's WSGI server via werkzeug for reliable testing.
"""

import os
import sys
import threading
import time

sys.path.insert(0, "/mnt/e/acct")
os.chdir("/mnt/e/acct/accounting_app")
sys.path.insert(0, "/mnt/e/acct/accounting_app")

import pytest
from playwright.sync_api import Browser, Page, sync_playwright

BASE_URL = "http://127.0.0.1:8765"
ADMIN_USER = "admin"
ADMIN_PASS = "admin123"

_server_instance = None


@pytest.fixture(scope="session")
def flask_server():
    """Start Flask dev server for the test session."""
    global _server_instance
    
    from app import create_app
    app = create_app("testing")
    
    from werkzeug.serving import make_server
    _server_instance = make_server("127.0.0.1", 8765, app, threaded=True)
    thread = threading.Thread(target=_server_instance.serve_forever, daemon=True)
    thread.start()
    
    for _ in range(10):
        try:
            import urllib.request
            urllib.request.urlopen(BASE_URL, timeout=1)
            break
        except Exception:
            time.sleep(0.5)
    
    yield BASE_URL
    
    if _server_instance:
        _server_instance.shutdown()


@pytest.fixture(scope="session")
def browser(flask_server):
    """Launch browser for the test session."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture(scope="function")
def page(browser: Browser):
    """Create a new page for each test."""
    context = browser.new_context()
    page = context.new_page()
    yield page
    context.close()


@pytest.fixture(scope="function")
def logged_in_page(page: Page, flask_server):
    """Create a logged-in page for each test."""
    page.goto(f"{flask_server}/auth/login")
    page.wait_for_load_state("networkidle")
    page.fill("#username", ADMIN_USER)
    page.fill("#password", ADMIN_PASS)
    page.click('button[type="submit"]')
    page.wait_for_load_state("networkidle")
    yield page
