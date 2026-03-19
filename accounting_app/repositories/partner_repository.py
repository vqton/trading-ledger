"""
Partner Repository - Database operations for Customer, Vendor, and Employee.
Based on Circular 99/2025/TT-BTC for Vietnamese accounting standards.
"""

from datetime import date
from decimal import Decimal
from typing import Dict, List, Optional

from sqlalchemy import func, and_, or_

from models.journal import JournalVoucher, JournalEntry, VoucherStatus
from models.account import Account
from models.partner import Customer, Vendor, Employee
from core.database import db


class PartnerRepository:
    """Repository for partner-related database operations."""

    @classmethod
    def get_all_customers(
        cls,
        is_active: Optional[bool] = None,
        customer_type: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        per_page: int = 50
    ) -> tuple[List[Customer], int]:
        """Get all customers with optional filters and pagination."""
        query = Customer.query

        if is_active is not None:
            query = query.filter(Customer.is_active == is_active)

        if customer_type:
            query = query.filter(Customer.customer_type == customer_type)

        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Customer.code.ilike(search_term),
                    Customer.name.ilike(search_term),
                    Customer.tax_id.ilike(search_term),
                    Customer.email.ilike(search_term)
                )
            )

        query = query.order_by(Customer.code)
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        return list(pagination.items), pagination.total

    @classmethod
    def get_customer_by_id(cls, customer_id: int) -> Optional[Customer]:
        """Get customer by ID."""
        return db.session.get(Customer, customer_id)

    @classmethod
    def get_customer_by_code(cls, code: str) -> Optional[Customer]:
        """Get customer by code."""
        return Customer.query.filter_by(code=code).first()

    @classmethod
    def create_customer(cls, data: Dict) -> Customer:
        """Create a new customer."""
        customer = Customer(
            code=data.get("code") or Customer.generate_code(),
            name=data["name"],
            tax_id=data.get("tax_id"),
            email=data.get("email"),
            phone=data.get("phone"),
            address=data.get("address"),
            city=data.get("city"),
            country=data.get("country", "Vietnam"),
            contact_person=data.get("contact_person"),
            credit_limit=data.get("credit_limit", Decimal("0.00")),
            payment_terms=data.get("payment_terms", 30),
            customer_type=data.get("customer_type", "corporate"),
            notes=data.get("notes"),
            created_by=data.get("created_by", 1)
        )
        db.session.add(customer)
        db.session.commit()
        return customer

    @classmethod
    def update_customer(cls, customer_id: int, data: Dict) -> Optional[Customer]:
        """Update an existing customer."""
        customer = cls.get_customer_by_id(customer_id)
        if not customer:
            return None

        updatable_fields = [
            "name", "tax_id", "email", "phone", "address", "city",
            "country", "contact_person", "credit_limit", "payment_terms",
            "customer_type", "notes", "is_active"
        ]
        for field in updatable_fields:
            if field in data:
                setattr(customer, field, data[field])

        db.session.commit()
        return customer

    @classmethod
    def get_customer_ar_balance(cls, customer_id: int) -> Decimal:
        """Get outstanding AR balance for a customer."""
        customer = cls.get_customer_by_id(customer_id)
        if not customer:
            return Decimal("0.00")
        return customer.get_outstanding_balance()

    @classmethod
    def get_customer_ar_aging(
        cls,
        customer_id: Optional[int] = None,
        end_date: Optional[date] = None
    ) -> List[Dict]:
        """Get AR aging report."""
        ar_account = Account.query.filter_by(code="131").first()
        if not ar_account:
            return []

        query = db.session.query(
            JournalEntry.customer_id,
            JournalEntry.voucher_id,
            JournalVoucher.voucher_date,
            func.sum(JournalEntry.debit).label("debit"),
            func.sum(JournalEntry.credit).label("credit")
        ).join(
            JournalVoucher, JournalEntry.voucher_id == JournalVoucher.id
        ).filter(
            JournalEntry.account_id == ar_account.id,
            JournalVoucher.status == VoucherStatus.POSTED,
            JournalEntry.customer_id.isnot(None)
        )

        if customer_id:
            query = query.filter(JournalEntry.customer_id == customer_id)

        if end_date:
            query = query.filter(JournalVoucher.voucher_date <= end_date)

        query = query.group_by(
            JournalEntry.customer_id,
            JournalEntry.voucher_id,
            JournalVoucher.voucher_date
        )

        entries = query.all()

        customer_balances = {}
        for entry in entries:
            cid = entry.customer_id
            if cid not in customer_balances:
                customer_balances[cid] = {
                    "customer_id": cid,
                    "customer": None,
                    "balance": Decimal("0.00"),
                    "current": Decimal("0.00"),
                    "overdue_30": Decimal("0.00"),
                    "overdue_60": Decimal("0.00"),
                    "overdue_90": Decimal("0.00"),
                    "overdue_180": Decimal("0.00"),
                }

            balance = entry.debit - entry.credit
            if balance > 0:
                customer_balances[cid]["balance"] += balance
                days = (end_date or date.today()) - entry.voucher_date
                if days.days <= 30:
                    customer_balances[cid]["current"] += balance
                elif days.days <= 60:
                    customer_balances[cid]["overdue_30"] += balance
                elif days.days <= 90:
                    customer_balances[cid]["overdue_60"] += balance
                elif days.days <= 180:
                    customer_balances[cid]["overdue_90"] += balance
                else:
                    customer_balances[cid]["overdue_180"] += balance

        for cid in customer_balances:
            customer = cls.get_customer_by_id(cid)
            if customer:
                customer_balances[cid]["customer"] = customer

        return list(customer_balances.values())

    @classmethod
    def get_all_vendors(
        cls,
        is_active: Optional[bool] = None,
        vendor_type: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        per_page: int = 50
    ) -> tuple[List[Vendor], int]:
        """Get all vendors with optional filters and pagination."""
        query = Vendor.query

        if is_active is not None:
            query = query.filter(Vendor.is_active == is_active)

        if vendor_type:
            query = query.filter(Vendor.vendor_type == vendor_type)

        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Vendor.code.ilike(search_term),
                    Vendor.name.ilike(search_term),
                    Vendor.tax_id.ilike(search_term),
                    Vendor.email.ilike(search_term)
                )
            )

        query = query.order_by(Vendor.code)
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        return list(pagination.items), pagination.total

    @classmethod
    def get_vendor_by_id(cls, vendor_id: int) -> Optional[Vendor]:
        """Get vendor by ID."""
        return db.session.get(Vendor, vendor_id)

    @classmethod
    def get_vendor_by_code(cls, code: str) -> Optional[Vendor]:
        """Get vendor by code."""
        return Vendor.query.filter_by(code=code).first()

    @classmethod
    def create_vendor(cls, data: Dict) -> Vendor:
        """Create a new vendor."""
        vendor = Vendor(
            code=data.get("code") or Vendor.generate_code(),
            name=data["name"],
            tax_id=data.get("tax_id"),
            email=data.get("email"),
            phone=data.get("phone"),
            address=data.get("address"),
            city=data.get("city"),
            country=data.get("country", "Vietnam"),
            contact_person=data.get("contact_person"),
            credit_limit=data.get("credit_limit", Decimal("0.00")),
            payment_terms=data.get("payment_terms", 30),
            vendor_type=data.get("vendor_type", "supplier"),
            bank_account=data.get("bank_account"),
            bank_name=data.get("bank_name"),
            notes=data.get("notes"),
            created_by=data.get("created_by", 1)
        )
        db.session.add(vendor)
        db.session.commit()
        return vendor

    @classmethod
    def update_vendor(cls, vendor_id: int, data: Dict) -> Optional[Vendor]:
        """Update an existing vendor."""
        vendor = cls.get_vendor_by_id(vendor_id)
        if not vendor:
            return None

        updatable_fields = [
            "name", "tax_id", "email", "phone", "address", "city",
            "country", "contact_person", "credit_limit", "payment_terms",
            "vendor_type", "bank_account", "bank_name", "notes", "is_active"
        ]
        for field in updatable_fields:
            if field in data:
                setattr(vendor, field, data[field])

        db.session.commit()
        return vendor

    @classmethod
    def get_vendor_ap_balance(cls, vendor_id: int) -> Decimal:
        """Get outstanding AP balance for a vendor."""
        vendor = cls.get_vendor_by_id(vendor_id)
        if not vendor:
            return Decimal("0.00")
        return vendor.get_outstanding_balance()

    @classmethod
    def get_vendor_ap_aging(
        cls,
        vendor_id: Optional[int] = None,
        end_date: Optional[date] = None
    ) -> List[Dict]:
        """Get AP aging report."""
        ap_account = Account.query.filter_by(code="331").first()
        if not ap_account:
            return []

        query = db.session.query(
            JournalEntry.vendor_id,
            JournalEntry.voucher_id,
            JournalVoucher.voucher_date,
            func.sum(JournalEntry.credit).label("credit"),
            func.sum(JournalEntry.debit).label("debit")
        ).join(
            JournalVoucher, JournalEntry.voucher_id == JournalVoucher.id
        ).filter(
            JournalEntry.account_id == ap_account.id,
            JournalVoucher.status == VoucherStatus.POSTED,
            JournalEntry.vendor_id.isnot(None)
        )

        if vendor_id:
            query = query.filter(JournalEntry.vendor_id == vendor_id)

        if end_date:
            query = query.filter(JournalVoucher.voucher_date <= end_date)

        query = query.group_by(
            JournalEntry.vendor_id,
            JournalEntry.voucher_id,
            JournalVoucher.voucher_date
        )

        entries = query.all()

        vendor_balances = {}
        for entry in entries:
            vid = entry.vendor_id
            if vid not in vendor_balances:
                vendor_balances[vid] = {
                    "vendor_id": vid,
                    "vendor": None,
                    "balance": Decimal("0.00"),
                    "current": Decimal("0.00"),
                    "overdue_30": Decimal("0.00"),
                    "overdue_60": Decimal("0.00"),
                    "overdue_90": Decimal("0.00"),
                    "overdue_180": Decimal("0.00"),
                }

            balance = entry.credit - entry.debit
            if balance > 0:
                vendor_balances[vid]["balance"] += balance
                days = (end_date or date.today()) - entry.voucher_date
                if days.days <= 30:
                    vendor_balances[vid]["current"] += balance
                elif days.days <= 60:
                    vendor_balances[vid]["overdue_30"] += balance
                elif days.days <= 90:
                    vendor_balances[vid]["overdue_60"] += balance
                elif days.days <= 180:
                    vendor_balances[vid]["overdue_90"] += balance
                else:
                    vendor_balances[vid]["overdue_180"] += balance

        for vid in vendor_balances:
            vendor = cls.get_vendor_by_id(vid)
            if vendor:
                vendor_balances[vid]["vendor"] = vendor

        return list(vendor_balances.values())

    @classmethod
    def get_all_employees(
        cls,
        is_active: Optional[bool] = None,
        department: Optional[str] = None,
        employee_type: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        per_page: int = 50
    ) -> tuple[List[Employee], int]:
        """Get all employees with optional filters and pagination."""
        query = Employee.query

        if is_active is not None:
            query = query.filter(Employee.is_active == is_active)

        if department:
            query = query.filter(Employee.department == department)

        if employee_type:
            query = query.filter(Employee.employee_type == employee_type)

        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Employee.code.ilike(search_term),
                    Employee.employee_id.ilike(search_term),
                    Employee.name.ilike(search_term),
                    Employee.email.ilike(search_term)
                )
            )

        query = query.order_by(Employee.code)
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        return list(pagination.items), pagination.total

    @classmethod
    def get_employee_by_id(cls, employee_id: int) -> Optional[Employee]:
        """Get employee by ID."""
        return db.session.get(Employee, employee_id)

    @classmethod
    def get_employee_by_code(cls, code: str) -> Optional[Employee]:
        """Get employee by code."""
        return Employee.query.filter_by(code=code).first()

    @classmethod
    def create_employee(cls, data: Dict) -> Employee:
        """Create a new employee."""
        employee = Employee(
            code=data.get("code") or Employee.generate_code(),
            employee_id=data.get("employee_id"),
            name=data["name"],
            date_of_birth=data.get("date_of_birth"),
            gender=data.get("gender"),
            email=data.get("email"),
            phone=data.get("phone"),
            address=data.get("address"),
            city=data.get("city"),
            department=data.get("department"),
            position=data.get("position"),
            employee_type=data.get("employee_type", "fulltime"),
            join_date=data.get("join_date"),
            leave_date=data.get("leave_date"),
            id_card=data.get("id_card"),
            tax_id=data.get("tax_id"),
            social_insurance_no=data.get("social_insurance_no"),
            bank_account=data.get("bank_account"),
            bank_name=data.get("bank_name"),
            notes=data.get("notes"),
            created_by=data.get("created_by", 1)
        )
        db.session.add(employee)
        db.session.commit()
        return employee

    @classmethod
    def update_employee(cls, employee_id: int, data: Dict) -> Optional[Employee]:
        """Update an existing employee."""
        employee = cls.get_employee_by_id(employee_id)
        if not employee:
            return None

        updatable_fields = [
            "employee_id", "name", "date_of_birth", "gender", "email",
            "phone", "address", "city", "department", "position",
            "employee_type", "join_date", "leave_date", "id_card",
            "tax_id", "social_insurance_no", "bank_account", "bank_name",
            "notes", "is_active"
        ]
        for field in updatable_fields:
            if field in data:
                setattr(employee, field, data[field])

        db.session.commit()
        return employee

    @classmethod
    def get_employee_advance_balance(cls, employee_id: int) -> Decimal:
        """Get outstanding advance balance for an employee."""
        employee = cls.get_employee_by_id(employee_id)
        if not employee:
            return Decimal("0.00")
        return employee.get_advance_balance()

    @classmethod
    def get_departments(cls) -> List[str]:
        """Get list of unique departments."""
        result = db.session.query(Employee.department).distinct().filter(
            Employee.department.isnot(None)
        ).all()
        return [r[0] for r in result]

    @classmethod
    def get_partner_summary(cls) -> Dict:
        """Get summary statistics for all partners."""
        return {
            "total_customers": Customer.query.count(),
            "active_customers": Customer.query.filter_by(is_active=True).count(),
            "total_vendors": Vendor.query.count(),
            "active_vendors": Vendor.query.filter_by(is_active=True).count(),
            "total_employees": Employee.query.count(),
            "active_employees": Employee.query.filter_by(is_active=True).count(),
        }
