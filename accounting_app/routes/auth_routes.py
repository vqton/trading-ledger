from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user
from flask_wtf.csrf import generate_csrf

from core.database import db
from core.security import Role, User
from forms.auth_forms import LoginForm, ChangePasswordForm, UserForm, RoleForm
from models.audit_log import AuditLog, AuditAction, AuditEntity

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Login page with authentication."""
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = LoginForm()
    if request.method == "POST" and form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash("Tài khoản đã bị vô hiệu hóa", "danger")
                return render_template("auth/login.html", form=form)

            login_user(user, remember=form.remember_me.data)
            user.update_last_login()

            AuditLog.log(
                action=AuditAction.LOGIN,
                entity=AuditEntity.USER,
                entity_id=user.id,
                user_id=user.id,
                ip_address=request.remote_addr,
                user_agent=request.headers.get("User-Agent"),
            )

            next_page = request.args.get("next")
            flash(f"Chào mừng {user.username}!", "success")
            return redirect(next_page or url_for("index"))
        else:
            flash("Tên đăng nhập hoặc mật khẩu không đúng", "danger")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
def logout():
    """Logout action."""
    if current_user.is_authenticated:
        AuditLog.log(
            action=AuditAction.LOGOUT,
            entity=AuditEntity.USER,
            entity_id=current_user.id,
            user_id=current_user.id,
            ip_address=request.remote_addr,
            user_agent=request.headers.get("User-Agent"),
        )

    logout_user()
    flash("Đã đăng xuất thành công", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/change-password", methods=["GET", "POST"])
def change_password():
    """Change password page."""
    if not current_user.is_authenticated:
        return redirect(url_for("auth.login"))

    form = ChangePasswordForm()
    if request.method == "POST" and form.validate_on_submit():
        if not current_user.check_password(form.old_password.data):
            flash("Mật khẩu cũ không đúng", "danger")
            return render_template("auth/change_password.html", form=form)

        current_user.set_password(form.new_password.data)
        db.session.commit()

        AuditLog.log(
            action=AuditAction.UPDATE,
            entity=AuditEntity.USER,
            entity_id=current_user.id,
            user_id=current_user.id,
            old_value={"action": "change_password"},
            new_value={"action": "password_changed"},
            ip_address=request.remote_addr,
        )

        flash("Đổi mật khẩu thành công", "success")
        return redirect(url_for("index"))

    return render_template("auth/change_password.html", form=form)


@auth_bp.route("/users")
def users():
    """User management page."""
    from core.rbac import permission_required

    @permission_required("user", "read")
    def _users():
        all_users = User.query.all()
        return render_template("auth/users.html", users=all_users)

    return _users()


@auth_bp.route("/users/create", methods=["GET", "POST"])
def create_user():
    """Create new user."""
    from core.rbac import admin_required

    @admin_required
    def _create_user():
        form = UserForm()
        form.role_id.choices = [(r.id, r.name) for r in Role.query.all()]

        if request.method == "POST" and form.validate_on_submit():
            existing_user = User.query.filter(
                (User.username == form.username.data) | (User.email == form.email.data)
            ).first()

            if existing_user:
                flash("Tên đăng nhập hoặc email đã tồn tại", "danger")
                return render_template("auth/user_form.html", form=form)

            user = User(
                username=form.username.data,
                email=form.email.data,
                role_id=form.role_id.data,
                is_active=form.is_active.data,
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()

            AuditLog.log(
                action=AuditAction.CREATE,
                entity=AuditEntity.USER,
                entity_id=user.id,
                user_id=current_user.id,
                new_value={"username": user.username, "email": user.email},
                ip_address=request.remote_addr,
            )

            flash(f"Đã tạo người dùng {user.username}", "success")
            return redirect(url_for("auth.users"))

        return render_template("auth/user_form.html", form=form)

    return _create_user()


@auth_bp.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
def edit_user(user_id: int):
    """Edit existing user."""
    from core.rbac import admin_required

    @admin_required
    def _edit_user(user_id: int):
        user = User.query.get_or_404(user_id)
        form = UserForm(obj=user)
        form.role_id.choices = [(r.id, r.name) for r in Role.query.all()]

        if request.method == "POST" and form.validate_on_submit():
            old_values = {"username": user.username, "email": user.email, "role_id": user.role_id}

            user.email = form.email.data
            user.role_id = form.role_id.data
            user.is_active = form.is_active.data

            if form.password.data:
                user.set_password(form.password.data)

            db.session.commit()

            AuditLog.log(
                action=AuditAction.UPDATE,
                entity=AuditEntity.USER,
                entity_id=user.id,
                user_id=current_user.id,
                old_value=old_values,
                new_value={"email": user.email, "role_id": user.role_id},
                ip_address=request.remote_addr,
            )

            flash(f"Đã cập nhật người dùng {user.username}", "success")
            return redirect(url_for("auth.users"))

        return render_template("auth/user_form.html", form=form, user=user)

    return _edit_user(user_id)


@auth_bp.route("/roles")
def roles():
    """Role management page."""
    from core.rbac import admin_required

    @admin_required
    def _roles():
        all_roles = Role.query.all()
        return render_template("auth/roles.html", roles=all_roles)

    return _roles()
