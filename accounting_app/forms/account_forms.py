from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError

from models.account import AccountType, NormalBalance
from repositories.account_repository import AccountRepository


class AccountForm(FlaskForm):
    """Account creation/editing form."""

    account_code = StringField(
        "Mã tài khoản",
        validators=[
            DataRequired(message="Vui lòng nhập mã tài khoản"),
            Length(min=1, max=20, message="Mã tài khoản phải từ 1-20 ký tự"),
        ],
    )
    account_name = StringField(
        "Tên tài khoản",
        validators=[
            DataRequired(message="Vui lòng nhập tên tài khoản"),
            Length(min=1, max=200, message="Tên tài khoản phải từ 1-200 ký tự"),
        ],
    )
    account_type = SelectField(
        "Loại tài khoản",
        coerce=str,
        choices=AccountType.CHOICES,
        validators=[DataRequired(message="Vui lòng chọn loại tài khoản")],
    )
    parent_id = SelectField(
        "Tài khoản cha",
        coerce=int,
        choices=[],
        validators=[],
    )
    normal_balance = SelectField(
        "Số dư bình thường",
        coerce=str,
        choices=[
            (NormalBalance.DEBIT, "Nợ (Debit)"),
            (NormalBalance.CREDIT, "Có (Credit)"),
        ],
        validators=[DataRequired(message="Vui lòng chọn số dư bình thường")],
    )
    is_detail = BooleanField("Tài khoản chi tiết")
    is_active = BooleanField("Hoạt động")
    submit = SubmitField("Lưu")

    def validate_account_code(self, account_code: StringField) -> None:
        """Validate account code uniqueness."""
        existing = AccountRepository.get_by_code(account_code.data)
        if existing:
            raise ValidationError(f"Mã tài khoản {account_code.data} đã tồn tại")

    def validate_parent_id(self, parent_id: SelectField) -> None:
        """Validate parent account."""
        if parent_id.data:
            parent = AccountRepository.get_by_id(parent_id.data)
            if not parent:
                raise ValidationError("Tài khoản cha không tồn tại")
            if not parent.is_postable:
                raise ValidationError("Tài khoản cha phải là tài khoản tổng hợp")
