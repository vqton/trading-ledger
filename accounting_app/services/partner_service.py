"""
Partner Service - Business logic for Customer, Vendor, and Employee management.
Based on Circular 99/2025/TT-BTC for Vietnamese accounting standards.
"""

from datetime import date
from decimal import Decimal
from typing import Dict, List, Optional, Tuple

from repositories.partner_repository import PartnerRepository
from models.partner import Customer, Vendor, Employee, CustomerType, VendorType, EmployeeType


class PartnerService:
    """Service for partner-related business operations."""

    @staticmethod
    def get_customers(
        is_active: Optional[bool] = None,
        customer_type: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        per_page: int = 50
    ) -> Tuple[List[Dict], int]:
        """Get customers with pagination and filters."""
        customers, total = PartnerRepository.get_all_customers(
            is_active=is_active,
            customer_type=customer_type,
            search=search,
            page=page,
            per_page=per_page
        )
        return [c.to_dict() for c in customers], total

    @staticmethod
    def get_customer(customer_id: int) -> Optional[Dict]:
        """Get customer by ID."""
        customer = PartnerRepository.get_customer_by_id(customer_id)
        if not customer:
            return None
        result = customer.to_dict()
        result["ar_balance"] = customer.get_outstanding_balance()
        return result

    @staticmethod
    def get_customer_by_code(code: str) -> Optional[Dict]:
        """Get customer by code."""
        customer = PartnerRepository.get_customer_by_code(code)
        if not customer:
            return None
        result = customer.to_dict()
        result["ar_balance"] = customer.get_outstanding_balance()
        return result

    @staticmethod
    def create_customer(data: Dict) -> Tuple[bool, Dict]:
        """Create a new customer."""
        if not data.get("name"):
            return False, {"error": "Customer name is required"}

        if data.get("tax_id"):
            existing = Customer.query.filter_by(tax_id=data["tax_id"]).first()
            if existing:
                return False, {"error": f"Customer with tax ID {data['tax_id']} already exists"}

        try:
            customer = PartnerRepository.create_customer(data)
            return True, customer.to_dict()
        except Exception as e:
            return False, {"error": str(e)}

    @staticmethod
    def update_customer(customer_id: int, data: Dict) -> Tuple[bool, Dict]:
        """Update an existing customer."""
        if data.get("tax_id"):
            existing = Customer.query.filter(
                Customer.tax_id == data["tax_id"],
                Customer.id != customer_id
            ).first()
            if existing:
                return False, {"error": f"Customer with tax ID {data['tax_id']} already exists"}

        try:
            customer = PartnerRepository.update_customer(customer_id, data)
            if not customer:
                return False, {"error": "Customer not found"}
            return True, customer.to_dict()
        except Exception as e:
            return False, {"error": str(e)}

    @staticmethod
    def delete_customer(customer_id: int) -> Tuple[bool, str]:
        """Delete (deactivate) a customer."""
        customer = PartnerRepository.get_customer_by_id(customer_id)
        if not customer:
            return False, "Customer not found"

        ar_balance = customer.get_outstanding_balance()
        if ar_balance > 0:
            return False, f"Cannot delete customer with outstanding AR balance of {ar_balance}"

        customer.is_active = False
        from core.database import db
        db.session.commit()
        return True, "Customer deactivated successfully"

    @staticmethod
    def get_customer_ar_aging(
        customer_id: Optional[int] = None,
        end_date: Optional[date] = None
    ) -> List[Dict]:
        """Get AR aging report for customers."""
        aging = PartnerRepository.get_customer_ar_aging(customer_id, end_date)
        result = []
        for item in aging:
            entry = {
                "customer_id": item["customer_id"],
                "customer_code": item["customer"].code if item["customer"] else None,
                "customer_name": item["customer"].name if item["customer"] else None,
                "balance": item["balance"],
                "current": item["current"],
                "overdue_30": item["overdue_30"],
                "overdue_60": item["overdue_60"],
                "overdue_90": item["overdue_90"],
                "overdue_180": item["overdue_180"],
            }
            result.append(entry)
        return result

    @staticmethod
    def get_vendors(
        is_active: Optional[bool] = None,
        vendor_type: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        per_page: int = 50
    ) -> Tuple[List[Dict], int]:
        """Get vendors with pagination and filters."""
        vendors, total = PartnerRepository.get_all_vendors(
            is_active=is_active,
            vendor_type=vendor_type,
            search=search,
            page=page,
            per_page=per_page
        )
        return [v.to_dict() for v in vendors], total

    @staticmethod
    def get_vendor(vendor_id: int) -> Optional[Dict]:
        """Get vendor by ID."""
        vendor = PartnerRepository.get_vendor_by_id(vendor_id)
        if not vendor:
            return None
        result = vendor.to_dict()
        result["ap_balance"] = vendor.get_outstanding_balance()
        return result

    @staticmethod
    def get_vendor_by_code(code: str) -> Optional[Dict]:
        """Get vendor by code."""
        vendor = PartnerRepository.get_vendor_by_code(code)
        if not vendor:
            return None
        result = vendor.to_dict()
        result["ap_balance"] = vendor.get_outstanding_balance()
        return result

    @staticmethod
    def create_vendor(data: Dict) -> Tuple[bool, Dict]:
        """Create a new vendor."""
        if not data.get("name"):
            return False, {"error": "Vendor name is required"}

        if data.get("tax_id"):
            existing = Vendor.query.filter_by(tax_id=data["tax_id"]).first()
            if existing:
                return False, {"error": f"Vendor with tax ID {data['tax_id']} already exists"}

        try:
            vendor = PartnerRepository.create_vendor(data)
            return True, vendor.to_dict()
        except Exception as e:
            return False, {"error": str(e)}

    @staticmethod
    def update_vendor(vendor_id: int, data: Dict) -> Tuple[bool, Dict]:
        """Update an existing vendor."""
        if data.get("tax_id"):
            existing = Vendor.query.filter(
                Vendor.tax_id == data["tax_id"],
                Vendor.id != vendor_id
            ).first()
            if existing:
                return False, {"error": f"Vendor with tax ID {data['tax_id']} already exists"}

        try:
            vendor = PartnerRepository.update_vendor(vendor_id, data)
            if not vendor:
                return False, {"error": "Vendor not found"}
            return True, vendor.to_dict()
        except Exception as e:
            return False, {"error": str(e)}

    @staticmethod
    def delete_vendor(vendor_id: int) -> Tuple[bool, str]:
        """Delete (deactivate) a vendor."""
        vendor = PartnerRepository.get_vendor_by_id(vendor_id)
        if not vendor:
            return False, "Vendor not found"

        ap_balance = vendor.get_outstanding_balance()
        if ap_balance > 0:
            return False, f"Cannot delete vendor with outstanding AP balance of {ap_balance}"

        vendor.is_active = False
        from core.database import db
        db.session.commit()
        return True, "Vendor deactivated successfully"

    @staticmethod
    def get_vendor_ap_aging(
        vendor_id: Optional[int] = None,
        end_date: Optional[date] = None
    ) -> List[Dict]:
        """Get AP aging report for vendors."""
        aging = PartnerRepository.get_vendor_ap_aging(vendor_id, end_date)
        result = []
        for item in aging:
            entry = {
                "vendor_id": item["vendor_id"],
                "vendor_code": item["vendor"].code if item["vendor"] else None,
                "vendor_name": item["vendor"].name if item["vendor"] else None,
                "balance": item["balance"],
                "current": item["current"],
                "overdue_30": item["overdue_30"],
                "overdue_60": item["overdue_60"],
                "overdue_90": item["overdue_90"],
                "overdue_180": item["overdue_180"],
            }
            result.append(entry)
        return result

    @staticmethod
    def get_employees(
        is_active: Optional[bool] = None,
        department: Optional[str] = None,
        employee_type: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        per_page: int = 50
    ) -> Tuple[List[Dict], int]:
        """Get employees with pagination and filters."""
        employees, total = PartnerRepository.get_all_employees(
            is_active=is_active,
            department=department,
            employee_type=employee_type,
            search=search,
            page=page,
            per_page=per_page
        )
        return [e.to_dict() for e in employees], total

    @staticmethod
    def get_employee(employee_id: int) -> Optional[Dict]:
        """Get employee by ID."""
        employee = PartnerRepository.get_employee_by_id(employee_id)
        if not employee:
            return None
        result = employee.to_dict()
        result["advance_balance"] = employee.get_advance_balance()
        return result

    @staticmethod
    def get_employee_by_code(code: str) -> Optional[Dict]:
        """Get employee by code."""
        employee = PartnerRepository.get_employee_by_code(code)
        if not employee:
            return None
        result = employee.to_dict()
        result["advance_balance"] = employee.get_advance_balance()
        return result

    @staticmethod
    def create_employee(data: Dict) -> Tuple[bool, Dict]:
        """Create a new employee."""
        if not data.get("name"):
            return False, {"error": "Employee name is required"}

        if data.get("employee_id"):
            existing = Employee.query.filter_by(employee_id=data["employee_id"]).first()
            if existing:
                return False, {"error": f"Employee with ID {data['employee_id']} already exists"}

        try:
            employee = PartnerRepository.create_employee(data)
            return True, employee.to_dict()
        except Exception as e:
            return False, {"error": str(e)}

    @staticmethod
    def update_employee(employee_id: int, data: Dict) -> Tuple[bool, Dict]:
        """Update an existing employee."""
        if data.get("employee_id"):
            existing = Employee.query.filter(
                Employee.employee_id == data["employee_id"],
                Employee.id != employee_id
            ).first()
            if existing:
                return False, {"error": f"Employee with ID {data['employee_id']} already exists"}

        try:
            employee = PartnerRepository.update_employee(employee_id, data)
            if not employee:
                return False, {"error": "Employee not found"}
            return True, employee.to_dict()
        except Exception as e:
            return False, {"error": str(e)}

    @staticmethod
    def delete_employee(employee_id: int) -> Tuple[bool, str]:
        """Delete (deactivate) an employee."""
        employee = PartnerRepository.get_employee_by_id(employee_id)
        if not employee:
            return False, "Employee not found"

        advance_balance = employee.get_advance_balance()
        if advance_balance > 0:
            return False, f"Cannot delete employee with outstanding advance balance of {advance_balance}"

        employee.is_active = False
        employee.leave_date = date.today()
        from core.database import db
        db.session.commit()
        return True, "Employee deactivated successfully"

    @staticmethod
    def get_departments() -> List[str]:
        """Get list of departments."""
        return PartnerRepository.get_departments()

    @staticmethod
    def get_partner_summary() -> Dict:
        """Get summary statistics for all partners."""
        return PartnerRepository.get_partner_summary()

    @staticmethod
    def get_customer_types() -> List[Dict]:
        """Get customer type choices."""
        return [{"value": k, "label": v} for k, v in CustomerType.CHOICES]

    @staticmethod
    def get_vendor_types() -> List[Dict]:
        """Get vendor type choices."""
        return [{"value": k, "label": v} for k, v in VendorType.CHOICES]

    @staticmethod
    def get_employee_types() -> List[Dict]:
        """Get employee type choices."""
        return [{"value": k, "label": v} for k, v in EmployeeType.CHOICES]
