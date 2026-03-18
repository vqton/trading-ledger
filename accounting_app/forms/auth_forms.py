from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length, ValidationError

from core.security import User


class LoginForm(FlaskForm):
    """User login form."""

    username = StringField(
        "Tên đăng nhập",
        validators=[
            DataRequired(message="Vui lòng nhập tên đăng nhập"),
            Length(min=3, max=80, message="Tên đăng nhập phải từ 3-80 ký tự"),
        ],
    )
    password = PasswordField(
        "Mật khẩu",
        validators=[
            DataRequired(message="Vui lòng nhập mật khẩu"),
        ],
    )
    remember_me = BooleanField("Ghi nhớ đăng nhập")
    submit = SubmitField("Đăng nhập")

    def validate_username(self, username: StringField) -> None:
        """Validate username exists."""
        user = User.query.filter_by(username=username.data).first()
        if user is None:
            raise ValidationError("Tên đăng nhập không tồn tại")

    def validate_password(self, password: PasswordField) -> None:
        """Validate password matches."""
        user = User.query.filter_by(username=self.username.data).first()
        if user and not user.check_password(password.data):
            raise ValidationError("Mật khẩu không đúng")


class ChangePasswordForm(FlaskForm):
    """Change password form."""

    old_password = PasswordField(
        "Mật khẩu cũ",
        validators=[DataRequired(message="Vui lòng nhập mật khẩu cũ")],
    )
    new_password = PasswordField(
        "Mật khẩu mới",
        validators=[
            DataRequired(message="Vui lòng nhập mật khẩu mới"),
            Length(min=6, max=128, message="Mật khẩu phải từ 6-128 ký tự"),
        ],
    )
    confirm_password = PasswordField(
        "Xác nhận mật khẩu",
        validators=[DataRequired(message="Vui lòng xác nhận mật khẩu")],
    )
    submit = SubmitField("Đổi mật khẩu")

    def validate_confirm_password(self, confirm_password: PasswordField) -> None:
        """Validate password confirmation."""
        if self.new_password.data != confirm_password.data:
            raise ValidationError("Mật khẩu xác nhận không khớp")


class UserForm(FlaskForm):
    """User creation/editing form."""

    username = StringField(
        "Tên đăng nhập",
        validators=[
            DataRequired(message="Vui lòng nhập tên đăng nhập"),
            Length(min=3, max=80, message="Tên đăng nhập phải từ 3-80 ký tự"),
        ],
    )
    email = StringField(
        "Email",
        validators=[
            DataRequired(message="Vui lòng nhập email"),
            Email(message="Email không hợp lệ"),
        ],
    )
    password = PasswordField(
        "Mật khẩu",
        validators=[
            DataRequired(message="Vui lòng nhập mật khẩu"),
            Length(min=6, max=128, message="Mật khẩu phải từ 6-128 ký tự"),
        ],
    )
    role_id = SelectField(
        "Vai trò",
        coerce=int,
        validators=[DataRequired(message="Vui lòng chọn vai trò")],
    )
    is_active = BooleanField("Hoạt động")
    submit = SubmitField("Lưu")


class RoleForm(FlaskForm):
    """Role creation/editing form."""

    name = StringField(
        "Tên vai trò",
        validators=[
            DataRequired(message="Vui lòng nhập tên vai trò"),
            Length(min=2, max=50, message="Tên vai trò phải từ 2-50 ký tự"),
        ],
    )
    description = StringField("Mô tả")
    submit = SubmitField("Lưu")
