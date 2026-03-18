from functools import wraps
from typing import Callable, List, Optional

from flask import abort, flash, redirect, request, url_for
from flask_login import current_user


def permission_required(*permissions: str) -> Callable:
    """Decorator to check if user has required permissions.

    Usage:
        @permission_required('account', 'create')
        def create_account():
            ...
    """

    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Vui lòng đăng nhập để tiếp tục", "warning")
                return redirect(url_for("auth.login", next=request.url))

            if not current_user.role:
                flash("Tài khoản không có vai trò hợp lệ", "danger")
                abort(403)

            for permission in permissions:
                if not current_user.has_permission(permission[0], permission[1] if len(permission) > 1 else "read"):
                    flash(f"Bạn không có quyền thực hiện hành động này", "danger")
                    abort(403)

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def admin_required(f: Callable) -> Callable:
    """Decorator to check if user is admin."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Vui lòng đăng nhập để tiếp tục", "warning")
            return redirect(url_for("auth.login", next=request.url))

        if not current_user.role or current_user.role.name != "admin":
            flash("Bạn cần quyền quản trị để truy cập", "danger")
            abort(403)

        return f(*args, **kwargs)

    return decorated_function


def active_user_required(f: Callable) -> Callable:
    """Decorator to check if user account is active."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Vui lòng đăng nhập để tiếp tục", "warning")
            return redirect(url_for("auth.login", next=request.url))

        if not current_user.is_active:
            flash("Tài khoản của bạn đã bị vô hiệu hóa", "danger")
            logout_user()
            return redirect(url_for("auth.login"))

        return f(*args, **kwargs)

    return decorated_function


def logout_user() -> None:
    """Logout user and clear session."""
    from flask_login import logout_user
    logout_user()
