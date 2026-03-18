from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import StringField, SelectField, DateField, DecimalField, TextAreaField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Length, Optional, NumberRange
from wtforms import FormField, FieldList

from models.journal import VoucherType


class JournalEntryForm(FlaskForm):
    """Single journal entry line."""

    csrf_token = HiddenField()
    
    account_id = SelectField(
        "Tài khoản",
        coerce=int,
        choices=[],
        validators=[DataRequired(message="Chọn tài khoản")],
    )
    debit = DecimalField(
        "Nợ",
        validators=[Optional(), NumberRange(min=0)],
        default=0,
    )
    credit = DecimalField(
        "Có",
        validators=[Optional(), NumberRange(min=0)],
        default=0,
    )
    description = StringField(
        "Diễn giải",
        validators=[Optional(), Length(max=200)],
    )
    reference = StringField(
        "Tham chiếu",
        validators=[Optional(), Length(max=100)],
    )
    cost_center = StringField(
        "Đối tượng",
        validators=[Optional(), Length(max=50)],
    )


class JournalVoucherForm(FlaskForm):
    """Journal voucher form with multiple entries."""

    voucher_no = StringField(
        "Số chứng từ",
        validators=[Optional(), Length(max=50)],
    )
    voucher_date = DateField(
        "Ngày chứng từ",
        validators=[DataRequired(message="Nhập ngày chứng từ")],
    )
    voucher_type = SelectField(
        "Loại chứng từ",
        coerce=str,
        choices=VoucherType.CHOICES,
        default=VoucherType.GENERAL,
    )
    description = TextAreaField(
        "Diễn giải",
        validators=[Optional(), Length(max=500)],
    )
    reference = StringField(
        "Số tham chiếu",
        validators=[Optional(), Length(max=100)],
    )
    entries = FieldList(FormField(JournalEntryForm), min_entries=2)
    submit = SubmitField("Lưu")

    def validate_entries(self, entries):
        """Validate at least one entry."""
        if len(entries) == 0:
            raise ValueError("Phải có ít nhất một dòng kết toán")


class JournalSearchForm(FlaskForm):
    """Search/filter form for journal vouchers."""

    voucher_no = StringField("Số chứng từ", validators=[Optional()])
    start_date = DateField("Từ ngày", validators=[Optional()])
    end_date = DateField("Đến ngày", validators=[Optional()])
    status = SelectField(
        "Trạng thái",
        coerce=str,
        choices=[
            ("", "Tất cả"),
            ("draft", "Nháp"),
            ("posted", "Đã ghi sổ"),
            ("locked", "Khóa"),
            ("cancelled", "Hủy"),
        ],
        default="",
    )
    submit = SubmitField("Tìm kiếm")
