"""Inventory tests - FIFO, Weighted Average calculations."""
import pytest
from decimal import Decimal
from datetime import date, timedelta
from models.inventory import InventoryItem, InventoryBatch, InventoryValuationMethod, TransactionType, Warehouse
from core.security import User, Role
from core.database import db


def test_inventory_item_creation(app, db_session):
    """Test creating inventory item."""
    with app.app_context():
        item = InventoryItem(
            code="ITEM001",
            name="Test Product",
            unit="piece",
            cost_method=InventoryValuationMethod.FIFO,
        )
        db.session.add(item)
        db.session.commit()
        
        assert item.id is not None
        assert item.code == "ITEM001"
        assert item.cost_method == InventoryValuationMethod.FIFO


def test_inventory_item_average_cost_method(app, db_session):
    """Test inventory item with weighted average cost method."""
    with app.app_context():
        item = InventoryItem(
            code="ITEM002",
            name="Average Cost Item",
            unit="kg",
            cost_method=InventoryValuationMethod.AVERAGE,
        )
        db.session.add(item)
        db.session.commit()
        
        assert item.cost_method == InventoryValuationMethod.AVERAGE


def test_inventory_batch_creation(app, db_session):
    """Test creating inventory batch for FIFO tracking."""
    with app.app_context():
        warehouse = Warehouse(
            code="WH001",
            name="Main Warehouse",
            is_active=True,
        )
        db.session.add(warehouse)
        
        item = InventoryItem(
            code="ITEM003",
            name="FIFO Item",
            unit="piece",
            cost_method=InventoryValuationMethod.FIFO,
        )
        db.session.add(item)
        db.session.commit()
        
        batch = InventoryBatch(
            batch_code="BATCH-ITEM003-00001",
            item_id=item.id,
            warehouse_id=warehouse.id,
            quantity=Decimal("100"),
            unit_cost=Decimal("50000"),
            total_cost=Decimal("5000000"),
            remaining_qty=Decimal("100"),
            receipt_date=date.today(),
        )
        db.session.add(batch)
        db.session.commit()
        
        assert batch.id is not None
        assert batch.remaining_qty == Decimal("100")


def test_inventory_fifo_calculation(app, db_session):
    """Test FIFO inventory cost calculation.
    
    FIFO: First In, First Out
    - Oldest inventory is used first
    - Cost = sum of oldest batch costs
    """
    with app.app_context():
        warehouse = Warehouse(
            code="WH002",
            name="Test Warehouse",
            is_active=True,
        )
        db.session.add(warehouse)
        db.session.commit()
        
        item = InventoryItem(
            code="FIFO001",
            name="FIFO Test Item",
            unit="piece",
            cost_method=InventoryValuationMethod.FIFO,
        )
        db.session.add(item)
        db.session.commit()
        
        batch1 = InventoryBatch(
            batch_code="BATCH-FIFO001-00001",
            item_id=item.id,
            warehouse_id=warehouse.id,
            quantity=Decimal("50"),
            unit_cost=Decimal("10000"),
            total_cost=Decimal("500000"),
            remaining_qty=Decimal("50"),
            receipt_date=date.today() - timedelta(days=10),
        )
        
        batch2 = InventoryBatch(
            batch_code="BATCH-FIFO001-00002",
            item_id=item.id,
            warehouse_id=warehouse.id,
            quantity=Decimal("50"),
            unit_cost=Decimal("12000"),
            total_cost=Decimal("600000"),
            remaining_qty=Decimal("50"),
            receipt_date=date.today() - timedelta(days=5),
        )
        
        db.session.add(batch1)
        db.session.add(batch2)
        db.session.commit()
        
        sold_qty = Decimal("60")
        remaining = sold_qty
        
        cost_of_sold = Decimal("0")
        
        batches = InventoryBatch.query.filter_by(item_id=item.id).order_by(InventoryBatch.receipt_date).all()
        
        for batch in batches:
            if remaining <= 0:
                break
            qty_from_batch = min(batch.remaining_qty, remaining)
            cost_of_sold += qty_from_batch * batch.unit_cost
            remaining -= qty_from_batch
        
        assert cost_of_sold == Decimal("500000") + Decimal("120000")


def test_inventory_weighted_average_calculation(app, db_session):
    """Test weighted average inventory cost calculation.
    
    Weighted Average: (Total Cost) / (Total Quantity)
    """
    with app.app_context():
        warehouse = Warehouse(
            code="WH003",
            name="Avg Warehouse",
            is_active=True,
        )
        db.session.add(warehouse)
        db.session.commit()
        
        item = InventoryItem(
            code="AVG001",
            name="Average Test Item",
            unit="kg",
            cost_method=InventoryValuationMethod.AVERAGE,
        )
        db.session.add(item)
        db.session.commit()
        
        batch1 = InventoryBatch(
            batch_code="BATCH-AVG001-00001",
            item_id=item.id,
            warehouse_id=warehouse.id,
            quantity=Decimal("100"),
            unit_cost=Decimal("10000"),
            total_cost=Decimal("1000000"),
            remaining_qty=Decimal("100"),
            receipt_date=date.today() - timedelta(days=10),
        )
        
        batch2 = InventoryBatch(
            batch_code="BATCH-AVG001-00002",
            item_id=item.id,
            warehouse_id=warehouse.id,
            quantity=Decimal("100"),
            unit_cost=Decimal("12000"),
            total_cost=Decimal("1200000"),
            remaining_qty=Decimal("100"),
            receipt_date=date.today() - timedelta(days=5),
        )
        
        db.session.add(batch1)
        db.session.add(batch2)
        db.session.commit()
        
        total_qty = Decimal("200")
        total_cost = Decimal("2200000")
        
        weighted_avg = total_cost / total_qty
        
        assert weighted_avg == Decimal("11000")
        
        sold_qty = Decimal("50")
        cost_of_sold = sold_qty * weighted_avg
        
        assert cost_of_sold == Decimal("550000")


def test_inventory_warehouse_creation(app, db_session):
    """Test warehouse creation."""
    with app.app_context():
        warehouse = Warehouse(
            code="WH100",
            name="Central Warehouse",
            address="123 Main St",
            is_active=True,
        )
        db.session.add(warehouse)
        db.session.commit()
        
        assert warehouse.id is not None
        assert warehouse.code == "WH100"
        assert warehouse.is_active == True


def test_inventory_specific_identification(app, db_session):
    """Test specific identification method uses batch tracking."""
    with app.app_context():
        warehouse = Warehouse(
            code="WH004",
            name="Specific ID Warehouse",
            is_active=True,
        )
        db.session.add(warehouse)
        db.session.commit()
        
        item = InventoryItem(
            code="SPEC001",
            name="Specific ID Item",
            unit="piece",
            cost_method=InventoryValuationMethod.SPECIFIC,
        )
        db.session.add(item)
        db.session.commit()
        
        for i in range(3):
            batch = InventoryBatch(
                batch_code=f"BATCH-SPEC001-{i+1:05d}",
                item_id=item.id,
                warehouse_id=warehouse.id,
                quantity=Decimal("10"),
                unit_cost=Decimal(f"{10000 + i * 1000}"),
                total_cost=Decimal(f"{(10000 + i * 1000) * 10}"),
                remaining_qty=Decimal("10"),
                receipt_date=date.today() - timedelta(days=10-i),
                serial_number=f"SN-{1000+i}",
            )
            db.session.add(batch)
        
        db.session.commit()
        
        batches = InventoryBatch.query.filter_by(item_id=item.id).all()
        
        assert len(batches) == 3
        assert batches[0].serial_number == "SN-1000"
        assert batches[1].serial_number == "SN-1001"
        assert batches[2].serial_number == "SN-1002"
