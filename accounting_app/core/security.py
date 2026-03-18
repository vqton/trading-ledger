from datetime import datetime, timezone
from typing import Optional

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from core.database import db
from core.utils import utc_now


class User(UserMixin, db.Model):
    """User model for authentication."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)
    last_login = db.Column(db.DateTime)

    role = db.relationship("Role", backref="users")

    def set_password(self, password: str) -> None:
        """Hash and set password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify password against hash."""
        return check_password_hash(self.password_hash, password)

    def has_permission(self, resource: str, action: str = "read") -> bool:
        """Check if user has permission for a resource/action."""
        if not self.role:
            return False

        if self.role.name == "admin":
            return True

        permission = self.role.permissions.filter_by(
            resource=resource, action=action
        ).first()
        return permission is not None

    def can_create(self, resource: str) -> bool:
        """Check if user can create resource."""
        return self.has_permission(resource, "create")

    def can_read(self, resource: str) -> bool:
        """Check if user can read resource."""
        return self.has_permission(resource, "read")

    def can_update(self, resource: str) -> bool:
        """Check if user can update resource."""
        return self.has_permission(resource, "update")

    def can_delete(self, resource: str) -> bool:
        """Check if user can delete resource."""
        return self.has_permission(resource, "delete")

    def update_last_login(self) -> None:
        """Update last login timestamp."""
        self.last_login = utc_now()
        db.session.commit()


class Role(db.Model):
    """Role model for RBAC."""

    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))

    permissions = db.relationship("Permission", backref="role", lazy="dynamic")


class Permission(db.Model):
    """Permission model for fine-grained access control."""

    __tablename__ = "permissions"

    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)
    resource = db.Column(db.String(50), nullable=False)
    action = db.Column(db.String(50), nullable=False)

    __table_args__ = (db.UniqueConstraint("role_id", "resource", "action"),)


def create_default_roles():
    """Create default roles and permissions."""
    roles_data = [
        {"name": "admin", "description": "Full system access"},
        {"name": "accountant", "description": "Accounting operations"},
        {"name": "auditor", "description": "Read-only audit access"},
        {"name": "viewer", "description": "View-only access"},
    ]

    for role_data in roles_data:
        if not Role.query.filter_by(name=role_data["name"]).first():
            role = Role(**role_data)
            db.session.add(role)

    db.session.commit()

    admin_role = Role.query.filter_by(name="admin").first()
    if admin_role:
        resources = ["account", "journal", "report", "user", "settings", "inventory"]
        actions = ["create", "read", "update", "delete"]
        for resource in resources:
            for action in actions:
                if not Permission.query.filter_by(role_id=admin_role.id, resource=resource, action=action).first():
                    perm = Permission(role_id=admin_role.id, resource=resource, action=action)
                    db.session.add(perm)

    accountant_role = Role.query.filter_by(name="accountant").first()
    if accountant_role:
        resources = ["account", "journal", "report", "inventory"]
        actions = ["create", "read", "update"]
        for resource in resources:
            for action in actions:
                if not Permission.query.filter_by(role_id=accountant_role.id, resource=resource, action=action).first():
                    perm = Permission(role_id=accountant_role.id, resource=resource, action=action)
                    db.session.add(perm)

    auditor_role = Role.query.filter_by(name="auditor").first()
    if auditor_role:
        resources = ["account", "journal", "report"]
        for resource in resources:
            if not Permission.query.filter_by(role_id=auditor_role.id, resource=resource, action="read").first():
                perm = Permission(role_id=auditor_role.id, resource=resource, action="read")
                db.session.add(perm)

    db.session.commit()

    viewer_role = Role.query.filter_by(name="viewer").first()
    if viewer_role:
        resources = ["account", "journal", "report"]
        for resource in resources:
            if not Permission.query.filter_by(role_id=viewer_role.id, resource=resource, action="read").first():
                perm = Permission(role_id=viewer_role.id, resource=resource, action="read")
                db.session.add(perm)

    db.session.commit()


def create_admin_user():
    """Create default admin user if not exists."""
    if not User.query.filter_by(username="admin").first():
        admin_role = Role.query.filter_by(name="admin").first()
        if admin_role:
            admin = User(
                username="admin",
                email="admin@example.com",
                role_id=admin_role.id,
                is_active=True,
            )
            admin.set_password("admin123")
            db.session.add(admin)
            db.session.commit()
