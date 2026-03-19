"""
Tests for CostCenter, Project, and TaxPayment models and services.
"""
import pytest
from datetime import date
from decimal import Decimal

from models.cost_center import CostCenter
from models.project import Project
from models.tax_payment import TaxPayment
from core.security import User
from core.database import db


class TestCostCenterModel:
    """Tests for CostCenter model."""

    def test_create_cost_center(self, app):
        """Test creating a cost center."""
        with app.app_context():
            admin = User.query.filter_by(username="testuser").first()
            
            cc = CostCenter(
                code="CC-001",
                name="Accounting Department",
                description="Test description",
                department="Finance",
                budget_allocated=Decimal("100000000"),
                created_by=admin.id
            )
            db.session.add(cc)
            db.session.commit()
            
            assert cc.id is not None
            assert cc.code == "CC-001"
            assert cc.name == "Accounting Department"
            assert cc.is_active is True
            assert cc.budget_allocated == Decimal("100000000")

    def test_cost_center_auto_code(self, app):
        """Test auto-generating cost center code."""
        with app.app_context():
            code = CostCenter.generate_code()
            assert code.startswith("CC-")

    def test_cost_center_budget_used(self, app):
        """Test calculating budget used."""
        with app.app_context():
            admin = User.query.filter_by(username="testuser").first()
            
            cc = CostCenter(
                code="CC-BUDGET",
                name="Budget Test",
                created_by=admin.id
            )
            db.session.add(cc)
            db.session.commit()
            
            used = cc.get_budget_used()
            assert used == Decimal("0.00")

    def test_cost_center_to_dict(self, app):
        """Test cost center to dict conversion."""
        with app.app_context():
            admin = User.query.filter_by(username="testuser").first()
            
            cc = CostCenter(
                code="CC-DICT",
                name="Dict Test",
                department="IT",
                budget_allocated=Decimal("50000000"),
                created_by=admin.id
            )
            db.session.add(cc)
            db.session.commit()
            
            data = cc.to_dict()
            assert data["code"] == "CC-DICT"
            assert data["name"] == "Dict Test"
            assert data["department"] == "IT"

    def test_cost_center_parent_child(self, app):
        """Test cost center hierarchy."""
        with app.app_context():
            admin = User.query.filter_by(username="testuser").first()
            
            parent = CostCenter(
                code="CC-PARENT",
                name="Parent CC",
                created_by=admin.id
            )
            db.session.add(parent)
            db.session.commit()
            
            child = CostCenter(
                code="CC-CHILD",
                name="Child CC",
                parent_id=parent.id,
                created_by=admin.id
            )
            db.session.add(child)
            db.session.commit()
            
            assert child.parent_id == parent.id
            assert child.parent.id == parent.id


class TestProjectModel:
    """Tests for Project model."""

    def test_create_project(self, app):
        """Test creating a project."""
        with app.app_context():
            admin = User.query.filter_by(username="testuser").first()
            
            proj = Project(
                code="PRJ-001",
                name="Project A",
                description="Test project A",
                start_date=date(2024, 1, 1),
                end_date=date(2024, 12, 31),
                status="planning",
                project_type="service",
                total_contract_value=Decimal("500000000"),
                created_by=admin.id
            )
            db.session.add(proj)
            db.session.commit()
            
            assert proj.id is not None
            assert proj.code == "PRJ-001"
            assert proj.status == "planning"
            assert proj.total_contract_value == Decimal("500000000")

    def test_project_auto_code(self, app):
        """Test auto-generating project code."""
        with app.app_context():
            code = Project.generate_code()
            assert code.startswith("PRJ-")

    def test_project_profit_calculation(self, app):
        """Test project profit calculation."""
        with app.app_context():
            admin = User.query.filter_by(username="testuser").first()
            
            proj = Project(
                code="PRJ-PROFIT",
                name="Profit Test",
                total_revenue=Decimal("100000000"),
                total_expense=Decimal("60000000"),
                created_by=admin.id
            )
            db.session.add(proj)
            db.session.commit()
            
            assert proj.profit == Decimal("40000000")
            assert proj.profit_margin == Decimal("40.00")

    def test_project_to_dict(self, app):
        """Test project to dict conversion."""
        with app.app_context():
            admin = User.query.filter_by(username="testuser").first()
            
            proj = Project(
                code="PRJ-DICT",
                name="Dict Test",
                start_date=date(2024, 1, 1),
                status="active",
                project_type="consulting",
                total_contract_value=Decimal("200000000"),
                created_by=admin.id
            )
            db.session.add(proj)
            db.session.commit()
            
            data = proj.to_dict()
            assert data["code"] == "PRJ-DICT"
            assert data["name"] == "Dict Test"
            assert data["status"] == "active"


class TestTaxPaymentModel:
    """Tests for TaxPayment model."""

    def test_create_tax_payment(self, app):
        """Test creating a tax payment."""
        with app.app_context():
            admin = User.query.filter_by(username="testuser").first()
            
            payment = TaxPayment(
                payment_no="TVA-2024-00001",
                tax_type="vat",
                period_year=2024,
                period_month=1,
                taxable_amount=Decimal("100000000"),
                tax_rate=Decimal("0.1000"),
                tax_amount=Decimal("10000000"),
                due_date=date(2024, 2, 20),
                payment_status="pending",
                created_by=admin.id
            )
            db.session.add(payment)
            db.session.commit()
            
            assert payment.id is not None
            assert payment.payment_no == "TVA-2024-00001"
            assert payment.tax_type == "vat"
            assert payment.tax_amount == Decimal("10000000")

    def test_tax_payment_auto_number(self, app):
        """Test auto-generating payment number."""
        with app.app_context():
            code = TaxPayment.generate_payment_no("vat")
            assert code.startswith("TVA-")

    def test_tax_payment_is_overdue(self, app):
        """Test overdue check."""
        with app.app_context():
            admin = User.query.filter_by(username="testuser").first()
            
            overdue_payment = TaxPayment(
                payment_no="TVA-OVER",
                tax_type="vat",
                period_year=2023,
                tax_amount=Decimal("5000000"),
                due_date=date(2023, 12, 31),
                payment_status="pending",
                created_by=admin.id
            )
            db.session.add(overdue_payment)
            db.session.commit()
            
            assert overdue_payment.is_overdue is True

    def test_tax_payment_total_calculation(self, app):
        """Test total amount calculation."""
        with app.app_context():
            admin = User.query.filter_by(username="testuser").first()
            
            payment = TaxPayment(
                payment_no="TVA-TOTAL",
                tax_type="vat",
                period_year=2024,
                tax_amount=Decimal("10000000"),
                interest_amount=Decimal("500000"),
                penalty_amount=Decimal("200000"),
                created_by=admin.id
            )
            db.session.add(payment)
            db.session.commit()
            
            payment.calculate_total()
            
            assert payment.total_amount == Decimal("10700000")

    def test_tax_payment_to_dict(self, app):
        """Test tax payment to dict conversion."""
        with app.app_context():
            admin = User.query.filter_by(username="testuser").first()
            
            payment = TaxPayment(
                payment_no="TVA-DICT",
                tax_type="cit",
                period_year=2024,
                period_quarter=1,
                taxable_amount=Decimal("200000000"),
                tax_rate=Decimal("0.2000"),
                tax_amount=Decimal("40000000"),
                due_date=date(2024, 4, 30),
                payment_status="pending",
                created_by=admin.id
            )
            db.session.add(payment)
            db.session.commit()
            
            data = payment.to_dict()
            assert data["payment_no"] == "TVA-DICT"
            assert data["tax_type"] == "cit"
            assert data["period_year"] == 2024

    def test_get_total_by_type(self, app):
        """Test getting total tax by type."""
        with app.app_context():
            admin = User.query.filter_by(username="testuser").first()
            
            payment1 = TaxPayment(
                payment_no="TVA-2024-001",
                tax_type="vat",
                period_year=2024,
                tax_amount=Decimal("10000000"),
                payment_status="paid",
                created_by=admin.id
            )
            payment2 = TaxPayment(
                payment_no="TVA-2024-002",
                tax_type="vat",
                period_year=2024,
                tax_amount=Decimal("15000000"),
                payment_status="paid",
                created_by=admin.id
            )
            db.session.add(payment1)
            db.session.add(payment2)
            db.session.commit()
            
            total = TaxPayment.get_total_by_type("vat", 2024)
            assert total == Decimal("25000000")


class TestCostCenterViews:
    """Tests for CostCenter views."""

    def test_cost_center_list_requires_login(self, client):
        """Test cost center list requires login."""
        response = client.get("/cost-centers/")
        assert response.status_code == 302

    def test_cost_center_list_authenticated(self, logged_in_client, app):
        """Test cost center list page loads."""
        response = logged_in_client.get("/cost-centers/")
        assert response.status_code == 200

    def test_cost_center_create_get(self, logged_in_client, app):
        """Test cost center create form loads."""
        response = logged_in_client.get("/cost-centers/create")
        assert response.status_code == 200

    def test_cost_center_create_post(self, logged_in_client, app):
        """Test creating cost center via form."""
        response = logged_in_client.post("/cost-centers/create", data={
            "name": "Marketing Department",
            "department": "Marketing",
            "budget_allocated": "50000000"
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b"Marketing" in response.data

    def test_cost_center_tree_view(self, logged_in_client, app):
        """Test cost center tree view."""
        response = logged_in_client.get("/cost-centers/tree")
        assert response.status_code == 200

    def test_cost_center_budget_report(self, logged_in_client, app):
        """Test budget report page."""
        response = logged_in_client.get("/cost-centers/budget-report")
        assert response.status_code == 200


class TestProjectViews:
    """Tests for Project views."""

    def test_project_list_requires_login(self, client):
        """Test project list requires login."""
        response = client.get("/projects/")
        assert response.status_code == 302

    def test_project_list_authenticated(self, logged_in_client, app):
        """Test project list page loads."""
        response = logged_in_client.get("/projects/")
        assert response.status_code == 200

    def test_project_create_get(self, logged_in_client, app):
        """Test project create form loads."""
        response = logged_in_client.get("/projects/create")
        assert response.status_code == 200

    def test_project_create_post(self, logged_in_client, app):
        """Test creating project via form."""
        response = logged_in_client.post("/projects/create", data={
            "name": "Website Project",
            "project_type": "software",
            "status": "planning",
            "total_contract_value": "100000000"
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b"Website" in response.data

    def test_project_summary(self, logged_in_client, app):
        """Test project summary page."""
        response = logged_in_client.get("/projects/summary")
        assert response.status_code == 200


class TestTaxPaymentViews:
    """Tests for TaxPayment views."""

    def test_tax_payment_list_requires_login(self, client):
        """Test tax payment list requires login."""
        response = client.get("/tax-payments/")
        assert response.status_code == 302

    def test_tax_payment_list_authenticated(self, logged_in_client, app):
        """Test tax payment list page loads."""
        response = logged_in_client.get("/tax-payments/")
        assert response.status_code == 200

    def test_tax_payment_create_get(self, logged_in_client, app):
        """Test tax payment create form loads."""
        response = logged_in_client.get("/tax-payments/create")
        assert response.status_code == 200

    def test_tax_payment_create_post(self, logged_in_client, app):
        """Test creating tax payment via form."""
        response = logged_in_client.post("/tax-payments/create", data={
            "tax_type": "vat",
            "period_year": "2024",
            "period_month": "6",
            "taxable_amount": "100000000",
            "tax_rate": "0.10",
            "tax_amount": "10000000",
            "payment_status": "pending"
        }, follow_redirects=True)
        assert response.status_code == 200

    def test_tax_payment_summary(self, logged_in_client, app):
        """Test tax payment summary page."""
        response = logged_in_client.get("/tax-payments/summary")
        assert response.status_code == 200

    def test_tax_payment_pending(self, logged_in_client, app):
        """Test pending tax payments page."""
        response = logged_in_client.get("/tax-payments/pending")
        assert response.status_code == 200


class TestCostCenterService:
    """Tests for CostCenter service."""

    def test_cost_center_service_create(self, app):
        """Test CostCenterService create."""
        from services.cost_center_service import CostCenterService
        
        with app.app_context():
            admin = User.query.filter_by(username="testuser").first()
            
            cc, error = CostCenterService.create_cost_center(
                name="HR Department",
                created_by=admin.id
            )
            
            assert error is None
            assert cc is not None
            assert cc.name == "HR Department"

    def test_cost_center_service_create_validation(self, app):
        """Test CostCenterService validation."""
        from services.cost_center_service import CostCenterService
        
        with app.app_context():
            admin = User.query.filter_by(username="testuser").first()
            
            cc, error = CostCenterService.create_cost_center(
                name="AB",
                created_by=admin.id
            )
            
            assert cc is None
            assert error is not None


class TestProjectService:
    """Tests for Project service."""

    def test_project_service_create(self, app):
        """Test ProjectService create."""
        from services.project_service import ProjectService
        
        with app.app_context():
            admin = User.query.filter_by(username="testuser").first()
            
            proj, error = ProjectService.create_project(
                name="New Project",
                created_by=admin.id
            )
            
            assert error is None
            assert proj is not None
            assert proj.name == "New Project"

    def test_project_service_create_validation(self, app):
        """Test ProjectService validation."""
        from services.project_service import ProjectService
        
        with app.app_context():
            admin = User.query.filter_by(username="testuser").first()
            
            proj, error = ProjectService.create_project(
                name="A",
                created_by=admin.id
            )
            
            assert proj is None
            assert error is not None


class TestTaxPaymentService:
    """Tests for TaxPayment service."""

    def test_tax_payment_service_create(self, app):
        """Test TaxPaymentService create."""
        from services.tax_payment_service import TaxPaymentService
        
        with app.app_context():
            admin = User.query.filter_by(username="testuser").first()
            
            payment, error = TaxPaymentService.create_tax_payment(
                tax_type="vat",
                period_year=2024,
                tax_amount=Decimal("5000000"),
                created_by=admin.id
            )
            
            assert error is None
            assert payment is not None
            assert payment.tax_type == "vat"

    def test_tax_payment_service_create_validation(self, app):
        """Test TaxPaymentService validation."""
        from services.tax_payment_service import TaxPaymentService
        
        with app.app_context():
            admin = User.query.filter_by(username="testuser").first()
            
            payment, error = TaxPaymentService.create_tax_payment(
                tax_type="invalid_type",
                period_year=2024,
                created_by=admin.id
            )
            
            assert payment is None
            assert error is not None
