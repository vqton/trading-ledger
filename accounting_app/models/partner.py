from datetime import datetime, date
from decimal import Decimal
from typing import Optional

from core.database import db
from core.utils import utc_now


class Customer(db.Model):
    """Customer model for AR subledger (TK 131).

    Tracks customer information for accounts receivable tracking,
    supporting the B01 Balance Sheet and B05 Notes to Financial Statements.
    """

    __tablename__ = "customers"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    tax_id = db.Column(db.String(20), nullable=True, index=True)
    email = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(500), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    country = db.Column(db.String(100), nullable=True, default="Vietnam")
    contact_person = db.Column(db.String(100), nullable=True)
    credit_limit = db.Column(db.Numeric(18, 2), default=Decimal("0.00"))
    payment_terms = db.Column(db.Integer, default=30)
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    customer_type = db.Column(db.String(20), default="corporate", index=True)
    notes = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    creator = db.relationship("User", backref="customers")

    __table_args__ = (
        db.Index("ix_customer_name", "name"),
        db.Index("ix_customer_active_type", "is_active", "customer_type"),
    )

    def __repr__(self) -> str:
        return f"<Customer {self.code} - {self.name}>"

    @property
    def full_address(self) -> str:
        parts = [self.address, self.city, self.country]
        return ", ".join(p for p in parts if p)

    def get_outstanding_balance(self) -> Decimal:
        """Calculate outstanding AR balance from journal entries."""
        from models.journal import JournalEntry, VoucherStatus
        from models.account import Account

        ar_account = Account.query.filter_by(code="131").first()
        if not ar_account:
            return Decimal("0.00")

        total_debit = db.session.query(db.func.sum(JournalEntry.debit)).join(
            JournalVoucher, JournalEntry.voucher_id == JournalVoucher.id
        ).filter(
            JournalEntry.account_id == ar_account.id,
            JournalEntry.customer_id == self.id,
            JournalVoucher.status == VoucherStatus.POSTED
        ).scalar() or Decimal("0.00")

        total_credit = db.session.query(db.func.sum(JournalEntry.credit)).join(
            JournalVoucher, JournalEntry.voucher_id == JournalVoucher.id
        ).filter(
            JournalEntry.account_id == ar_account.id,
            JournalEntry.customer_id == self.id,
            JournalVoucher.status == VoucherStatus.POSTED
        ).scalar() or Decimal("0.00")

        return total_debit - total_credit

    @classmethod
    def generate_code(cls) -> str:
        """Generate next customer code."""
        year = datetime.now().year
        last_customer = cls.query.filter(
            cls.code.like(f"CUS-{year}%")
        ).order_by(cls.code.desc()).first()

        if last_customer:
            last_num = int(last_customer.code.split("-")[-1])
            new_num = last_num + 1
        else:
            new_num = 1

        return f"CUS-{year}-{new_num:04d}"

    def to_dict(self) -> dict:
        """Convert customer to dictionary."""
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "tax_id": self.tax_id,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "city": self.city,
            "country": self.country,
            "full_address": self.full_address,
            "contact_person": self.contact_person,
            "credit_limit": float(self.credit_limit) if self.credit_limit else 0.0,
            "payment_terms": self.payment_terms,
            "is_active": self.is_active,
            "customer_type": self.customer_type,
            "notes": self.notes,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


from models.journal import JournalVoucher


class Vendor(db.Model):
    """Vendor model for AP subledger (TK 331).

    Tracks vendor information for accounts payable tracking,
    supporting the B01 Balance Sheet and B05 Notes to Financial Statements.
    """

    __tablename__ = "vendors"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    tax_id = db.Column(db.String(20), nullable=True, index=True)
    email = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(500), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    country = db.Column(db.String(100), nullable=True, default="Vietnam")
    contact_person = db.Column(db.String(100), nullable=True)
    credit_limit = db.Column(db.Numeric(18, 2), default=Decimal("0.00"))
    payment_terms = db.Column(db.Integer, default=30)
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    vendor_type = db.Column(db.String(20), default="corporate", index=True)
    bank_account = db.Column(db.String(50), nullable=True)
    bank_name = db.Column(db.String(100), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    creator = db.relationship("User", backref="vendors")

    __table_args__ = (
        db.Index("ix_vendor_name", "name"),
        db.Index("ix_vendor_active_type", "is_active", "vendor_type"),
    )

    def __repr__(self) -> str:
        return f"<Vendor {self.code} - {self.name}>"

    @property
    def full_address(self) -> str:
        parts = [self.address, self.city, self.country]
        return ", ".join(p for p in parts if p)

    def get_outstanding_balance(self) -> Decimal:
        """Calculate outstanding AP balance from journal entries."""
        from models.journal import JournalEntry, VoucherStatus
        from models.account import Account

        ap_account = Account.query.filter_by(code="331").first()
        if not ap_account:
            return Decimal("0.00")

        total_credit = db.session.query(db.func.sum(JournalEntry.credit)).join(
            JournalVoucher, JournalEntry.voucher_id == JournalVoucher.id
        ).filter(
            JournalEntry.account_id == ap_account.id,
            JournalEntry.vendor_id == self.id,
            JournalVoucher.status == VoucherStatus.POSTED
        ).scalar() or Decimal("0.00")

        total_debit = db.session.query(db.func.sum(JournalEntry.debit)).join(
            JournalVoucher, JournalEntry.voucher_id == JournalVoucher.id
        ).filter(
            JournalEntry.account_id == ap_account.id,
            JournalEntry.vendor_id == self.id,
            JournalVoucher.status == VoucherStatus.POSTED
        ).scalar() or Decimal("0.00")

        return total_credit - total_debit

    @classmethod
    def generate_code(cls) -> str:
        """Generate next vendor code."""
        year = datetime.now().year
        last_vendor = cls.query.filter(
            cls.code.like(f"VEN-{year}%")
        ).order_by(cls.code.desc()).first()

        if last_vendor:
            last_num = int(last_vendor.code.split("-")[-1])
            new_num = last_num + 1
        else:
            new_num = 1

        return f"VEN-{year}-{new_num:04d}"

    def to_dict(self) -> dict:
        """Convert vendor to dictionary."""
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "tax_id": self.tax_id,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "city": self.city,
            "country": self.country,
            "full_address": self.full_address,
            "contact_person": self.contact_person,
            "credit_limit": float(self.credit_limit) if self.credit_limit else 0.0,
            "payment_terms": self.payment_terms,
            "is_active": self.is_active,
            "vendor_type": self.vendor_type,
            "bank_account": self.bank_account,
            "bank_name": self.bank_name,
            "notes": self.notes,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Employee(db.Model):
    """Employee model for advances (TK 141) and payroll (TK 334).

    Tracks employee information for advances tracking,
    supporting the B01 Balance Sheet and B05 Notes to Financial Statements.
    """

    __tablename__ = "employees"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    employee_id = db.Column(db.String(20), nullable=True, index=True)
    name = db.Column(db.String(200), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(500), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    department = db.Column(db.String(100), nullable=True, index=True)
    position = db.Column(db.String(100), nullable=True)
    employee_type = db.Column(db.String(20), default="fulltime", index=True)
    join_date = db.Column(db.Date, nullable=True)
    leave_date = db.Column(db.Date, nullable=True)
    id_card = db.Column(db.String(20), nullable=True)
    tax_id = db.Column(db.String(20), nullable=True)
    social_insurance_no = db.Column(db.String(20), nullable=True)
    bank_account = db.Column(db.String(50), nullable=True)
    bank_name = db.Column(db.String(100), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    notes = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    creator = db.relationship("User", backref="employees")

    __table_args__ = (
        db.Index("ix_employee_name", "name"),
        db.Index("ix_employee_dept_active", "department", "is_active"),
    )

    def __repr__(self) -> str:
        return f"<Employee {self.code} - {self.name}>"

    @property
    def full_address(self) -> str:
        parts = [self.address, self.city]
        return ", ".join(p for p in parts if p)

    @property
    def is_employed(self) -> bool:
        return self.is_active and self.leave_date is None

    def get_advance_balance(self) -> Decimal:
        """Calculate outstanding advance balance from journal entries (TK 141)."""
        from models.journal import JournalEntry, JournalVoucher, VoucherStatus
        from models.account import Account

        advance_account = Account.query.filter_by(code="141").first()
        if not advance_account:
            return Decimal("0.00")

        total_debit = db.session.query(db.func.sum(JournalEntry.debit)).join(
            JournalVoucher, JournalEntry.voucher_id == JournalVoucher.id
        ).filter(
            JournalEntry.account_id == advance_account.id,
            JournalEntry.reference == self.code,
            JournalVoucher.status == VoucherStatus.POSTED
        ).scalar() or Decimal("0.00")

        total_credit = db.session.query(db.func.sum(JournalEntry.credit)).join(
            JournalVoucher, JournalEntry.voucher_id == JournalVoucher.id
        ).filter(
            JournalEntry.account_id == advance_account.id,
            JournalEntry.reference == self.code,
            JournalVoucher.status == VoucherStatus.POSTED
        ).scalar() or Decimal("0.00")

        return total_debit - total_credit

    @classmethod
    def generate_code(cls) -> str:
        """Generate next employee code."""
        year = datetime.now().year
        last_emp = cls.query.filter(
            cls.code.like(f"EMP-{year}%")
        ).order_by(cls.code.desc()).first()

        if last_emp:
            last_num = int(last_emp.code.split("-")[-1])
            new_num = last_num + 1
        else:
            new_num = 1

        return f"EMP-{year}-{new_num:04d}"

    def to_dict(self) -> dict:
        """Convert employee to dictionary."""
        return {
            "id": self.id,
            "code": self.code,
            "employee_id": self.employee_id,
            "name": self.name,
            "date_of_birth": self.date_of_birth.isoformat() if self.date_of_birth else None,
            "gender": self.gender,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "city": self.city,
            "full_address": self.full_address,
            "department": self.department,
            "position": self.position,
            "employee_type": self.employee_type,
            "join_date": self.join_date.isoformat() if self.join_date else None,
            "leave_date": self.leave_date.isoformat() if self.leave_date else None,
            "id_card": self.id_card,
            "tax_id": self.tax_id,
            "social_insurance_no": self.social_insurance_no,
            "bank_account": self.bank_account,
            "bank_name": self.bank_name,
            "is_active": self.is_active,
            "is_employed": self.is_employed,
            "notes": self.notes,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class CustomerType:
    """Customer type constants."""

    CORPORATE = "corporate"
    INDIVIDUAL = "individual"
    GOVERNMENT = "government"

    CHOICES = [
        (CORPORATE, "Doanh nghiệp"),
        (INDIVIDUAL, "Cá nhân"),
        (GOVERNMENT, "Nhà nước"),
    ]


class VendorType:
    """Vendor type constants."""

    SUPPLIER = "supplier"
    SERVICE = "service"
    CONTRACTOR = "contractor"
    INDIVIDUAL = "individual"

    CHOICES = [
        (SUPPLIER, "Nhà cung cấp"),
        (SERVICE, "Dịch vụ"),
        (CONTRACTOR, "Nhà thầu"),
        (INDIVIDUAL, "Cá nhân"),
    ]


class EmployeeType:
    """Employee type constants."""

    FULLTIME = "fulltime"
    PARTTIME = "parttime"
    CONTRACTOR = "contractor"
    PROBATION = "probation"

    CHOICES = [
        (FULLTIME, "Toàn thời gian"),
        (PARTTIME, "Bán thời gian"),
        (CONTRACTOR, "Hợp đồng"),
        (PROBATION, "Thử việc"),
    ]
