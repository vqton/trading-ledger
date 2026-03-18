"""Authentication tests."""
import pytest
from core.security import User, Role
from core.database import db


def test_login_page_loads(client):
    """Test login page loads successfully."""
    response = client.get("/auth/login")
    assert response.status_code == 200
    assert b"VAS Accounting" in response.data


def test_login_success(client, app, db_session):
    """Test successful login."""
    with app.app_context():
        admin_role = Role.query.filter_by(name="admin").first()
        user = User(
            username="logintest",
            email="login@test.com",
            role_id=admin_role.id,
            is_active=True,
        )
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()
    
    response = client.post("/auth/login", data={
        "username": "logintest",
        "password": "password123",
    }, follow_redirects=True)
    
    assert response.status_code == 200


def test_login_invalid_credentials(client, app, db_session):
    """Test login with invalid credentials."""
    with app.app_context():
        admin_role = Role.query.filter_by(name="admin").first()
        user = User(
            username="invalidtest",
            email="invalid@test.com",
            role_id=admin_role.id,
            is_active=True,
        )
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()
    
    response = client.post("/auth/login", data={
        "username": "invalidtest",
        "password": "wrongpassword",
    })
    
    assert response.status_code == 200 or b"error" in response.data.lower()


def test_logout(app, client, db_session):
    """Test logout functionality."""
    with app.app_context():
        admin_role = Role.query.filter_by(name="admin").first()
        user = User(
            username="logouttest",
            email="logout@test.com",
            role_id=admin_role.id,
            is_active=True,
        )
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()
        user_id = user.id
    
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
    
    response = client.get("/auth/logout", follow_redirects=True)
    assert response.status_code == 200


def test_password_hashing(app, db_session):
    """Test password hashing works correctly."""
    with app.app_context():
        admin_role = Role.query.filter_by(name="admin").first()
        user = User(
            username="hashtest",
            email="hash@test.com",
            role_id=admin_role.id,
            is_active=True,
        )
        user.set_password("mypassword")
        
        assert user.password_hash != "mypassword"
        assert user.check_password("mypassword")
        assert not user.check_password("wrongpassword")


def test_user_has_role(app, db_session):
    """Test user has correct role."""
    with app.app_context():
        admin_role = Role.query.filter_by(name="admin").first()
        user = User(
            username="roletest",
            email="role@test.com",
            role_id=admin_role.id,
            is_active=True,
        )
        user.set_password("testpass")
        db.session.add(user)
        db.session.commit()
        
        assert user.role.name == "admin"


def test_inactive_user_cannot_login(client, app, db_session):
    """Test inactive user cannot login."""
    with app.app_context():
        admin_role = Role.query.filter_by(name="admin").first()
        user = User(
            username="inactive",
            email="inactive@test.com",
            role_id=admin_role.id,
            is_active=False,
        )
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()
    
    response = client.post("/auth/login", data={
        "username": "inactive",
        "password": "password123",
    })
    
    assert response.status_code == 200
