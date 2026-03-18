"""Inventory Service - Stock management with FIFO/Weighted Average."""

from datetime import date
from decimal import Decimal
from typing import Dict, List, Optional, Tuple

from core.database import db
from models.inventory import (
    InventoryBatch,
    InventoryItem,
    InventoryValuationMethod,
    StockTransaction,
    TransactionType,
    Warehouse,
)
from models.journal import JournalRepository
from models.account import Account


class InventoryService:
    """Service for inventory operations."""

    @staticmethod
    def get_all_items() -> List[InventoryItem]:
        """Get all inventory items."""
        return InventoryItem.query.filter_by(is_active=True).all()

    @staticmethod
    def get_item(item_id: int) -> Optional[InventoryItem]:
        """Get inventory item by ID."""
        return db.session.get(InventoryItem, item_id)

    @staticmethod
    def get_item_by_code(code: str) -> Optional[InventoryItem]:
        """Get inventory item by code."""
        return InventoryItem.query.filter_by(code=code).first()

    @staticmethod
    def create_item(item_data: Dict, user_id: int) -> InventoryItem:
        """Create new inventory item."""
        existing = InventoryItem.query.filter_by(code=item_data["code"]).first()
        if existing:
            raise ValueError(f"Mã hàng {item_data['code']} đã tồn tại")

        item = InventoryItem(
            code=item_data["code"],
            name=item_data["name"],
            unit=item_data.get("unit"),
            category=item_data.get("category"),
            default_warehouse_id=item_data.get("default_warehouse_id"),
            cost_method=item_data.get("cost_method", InventoryValuationMethod.AVERAGE),
            purchase_price=item_data.get("purchase_price", Decimal("0")),
            sale_price=item_data.get("sale_price", Decimal("0")),
            reorder_level=item_data.get("reorder_level", Decimal("0")),
            is_active=True,
        )
        db.session.add(item)
        db.session.commit()
        return item

    @staticmethod
    def update_item(item_id: int, item_data: Dict) -> InventoryItem:
        """Update inventory item."""
        item = db.session.get(InventoryItem, item_id)
        if not item:
            raise ValueError(f"Item {item_id} not found")

        for key, value in item_data.items():
            if hasattr(item, key):
                setattr(item, key, value)

        db.session.commit()
        return item

    @staticmethod
    def get_all_warehouses() -> List[Warehouse]:
        """Get all warehouses."""
        return Warehouse.query.filter_by(is_active=True).all()

    @staticmethod
    def create_warehouse(warehouse_data: Dict) -> Warehouse:
        """Create new warehouse."""
        existing = Warehouse.query.filter_by(code=warehouse_data["code"]).first()
        if existing:
            raise ValueError(f"Mã kho {warehouse_data['code']} đã tồn tại")

        warehouse = Warehouse(
            code=warehouse_data["code"],
            name=warehouse_data["name"],
            address=warehouse_data.get("address"),
            is_active=True,
        )
        db.session.add(warehouse)
        db.session.commit()
        return warehouse

    @staticmethod
    def get_stock_balance(item_id: int, warehouse_id: Optional[int] = None) -> Decimal:
        """Calculate current stock balance for an item."""
        query = StockTransaction.query.filter_by(item_id=item_id)
        
        if warehouse_id:
            query = query.filter_by(warehouse_id=warehouse_id)
        
        stock_in = query.filter_by(transaction_type=TransactionType.STOCK_IN).all()
        stock_out = query.filter_by(transaction_type=TransactionType.STOCK_OUT).all()
        
        total_in = sum(t.quantity for t in stock_in)
        total_out = sum(t.quantity for t in stock_out)
        
        return total_in - total_out

    @staticmethod
    def get_stock_valuation(
        item_id: int,
        valuation_date: date,
        warehouse_id: Optional[int] = None,
    ) -> Tuple[Decimal, Decimal]:
        """Calculate stock valuation using FIFO or Weighted Average.
        
        Returns: (total_quantity, total_value)
        """
        item = db.session.get(InventoryItem, item_id)
        if not item:
            raise ValueError(f"Item {item_id} not found")

        query = StockTransaction.query.filter(
            StockTransaction.item_id == item_id,
            StockTransaction.transaction_date <= valuation_date,
        )
        
        if warehouse_id:
            query = query.filter_by(warehouse_id=warehouse_id)
        
        transactions = query.order_by(StockTransaction.transaction_date).all()

        if item.cost_method == InventoryValuationMethod.FIFO:
            return InventoryService._calculate_fifo(transactions)
        elif item.cost_method == InventoryValuationMethod.AVERAGE:
            return InventoryService._calculate_average(transactions)
        else:
            return InventoryService._calculate_specific(transactions)

    @staticmethod
    def _calculate_fifo(transactions: List[StockTransaction]) -> Tuple[Decimal, Decimal]:
        """Calculate FIFO valuation."""
        total_qty = Decimal("0")
        total_value = Decimal("0")
        
        stock_in_qty = Decimal("0")
        stock_in_value = Decimal("0")
        
        for t in transactions:
            if t.transaction_type == TransactionType.STOCK_IN:
                stock_in_qty += t.quantity
                stock_in_value += t.total_amount
            else:
                if stock_in_qty > 0:
                    avg_cost = stock_in_value / stock_in_qty
                    cost = avg_cost * t.quantity
                    total_value += cost
                    
                    stock_in_qty -= t.quantity
                    stock_in_value -= cost
                    
                    if stock_in_qty < Decimal("0.01"):
                        stock_in_qty = Decimal("0")
                        stock_in_value = Decimal("0")
        
        total_qty = stock_in_qty
        if total_qty > 0 and stock_in_value > 0:
            pass
        else:
            total_value = sum(t.total_amount for t in transactions if t.transaction_type == TransactionType.STOCK_IN) - \
                         sum(t.unit_cost * min(t.quantity, stock_in_qty) for t in transactions if t.transaction_type == TransactionType.STOCK_OUT)
        
        return (total_qty, total_value)

    @staticmethod
    def _calculate_average(transactions: List[StockTransaction]) -> Tuple[Decimal, Decimal]:
        """Calculate Weighted Average valuation."""
        total_qty = Decimal("0")
        total_value = Decimal("0")
        
        for t in transactions:
            if t.transaction_type == TransactionType.STOCK_IN:
                total_qty += t.quantity
                total_value += t.total_amount
            else:
                if total_qty > 0:
                    avg_cost = total_value / total_qty
                    total_value -= avg_cost * t.quantity
                    total_qty -= t.quantity
        
        return (total_qty, total_value)

    @staticmethod
    def _calculate_specific(transactions: List[StockTransaction]) -> Tuple[Decimal, Decimal]:
        """Calculate Specific Identification valuation using batches."""
        total_qty = Decimal("0")
        total_value = Decimal("0")
        
        batches = InventoryBatch.query.filter(
            InventoryBatch.item_id == transactions[0].item_id if transactions else False,
            InventoryBatch.remaining_qty > 0,
        ).all()
        
        for batch in batches:
            total_qty += batch.remaining_qty
            total_value += batch.remaining_qty * batch.unit_cost
        
        return (total_qty, total_value)

    @staticmethod
    def create_stock_transaction(
        transaction_data: Dict,
        user_id: int,
    ) -> StockTransaction:
        """Create stock transaction and update batch records."""
        item = InventoryItem.query.get(transaction_data["item_id"])
        if not item:
            raise ValueError("Item not found")

        transaction = StockTransaction(
            transaction_no=StockTransaction.generate_transaction_no(
                transaction_data["transaction_type"]
            ),
            transaction_date=transaction_data["transaction_date"],
            transaction_type=transaction_data["transaction_type"],
            item_id=transaction_data["item_id"],
            warehouse_id=transaction_data["warehouse_id"],
            quantity=transaction_data["quantity"],
            unit_cost=transaction_data["unit_cost"],
            total_amount=transaction_data["quantity"] * transaction_data["unit_cost"],
            reference=transaction_data.get("reference"),
            description=transaction_data.get("description"),
            created_by=user_id,
        )
        db.session.add(transaction)

        if transaction_data["transaction_type"] == TransactionType.STOCK_IN:
            InventoryService._create_or_update_batch(
                item, transaction, transaction_data["warehouse_id"]
            )
        elif transaction_data["transaction_type"] == TransactionType.STOCK_OUT:
            InventoryService._allocate_from_batches(
                item, transaction, transaction_data["warehouse_id"]
            )

        db.session.commit()
        return transaction

    @staticmethod
    def _create_or_update_batch(
        item: InventoryItem,
        transaction: StockTransaction,
        warehouse_id: int,
    ) -> None:
        """Create batch record for stock in."""
        if item.cost_method == InventoryValuationMethod.FIFO:
            batch = InventoryBatch(
                batch_code=InventoryBatch.generate_batch_code(item.code),
                item_id=item.id,
                warehouse_id=warehouse_id,
                quantity=transaction.quantity,
                unit_cost=transaction.unit_cost,
                total_cost=transaction.total_amount,
                remaining_qty=transaction.quantity,
                receipt_date=transaction.transaction_date,
            )
            db.session.add(batch)

    @staticmethod
    def _allocate_from_batches(
        item: InventoryItem,
        transaction: StockTransaction,
        warehouse_id: int,
    ) -> None:
        """Allocate quantity from batches for stock out."""
        if item.cost_method == InventoryValuationMethod.FIFO:
            remaining = transaction.quantity
            batches = InventoryBatch.query.filter(
                InventoryBatch.item_id == item.id,
                InventoryBatch.warehouse_id == warehouse_id,
                InventoryBatch.remaining_qty > 0,
            ).order_by(InventoryBatch.receipt_date).all()

            for batch in batches:
                if remaining <= 0:
                    break
                allocate = min(remaining, batch.remaining_qty)
                batch.remaining_qty -= allocate
                remaining -= allocate

            if remaining > 0:
                raise ValueError(
                    f"Không đủ hàng trong kho để xuất: cần {transaction.quantity}, còn lại {transaction.quantity - remaining}"
                )

    @staticmethod
    def get_inventory_report(
        warehouse_id: Optional[int] = None,
        category: Optional[str] = None,
    ) -> List[Dict]:
        """Generate inventory report with quantities and values."""
        query = InventoryItem.query.filter_by(is_active=True)
        
        if category:
            query = query.filter_by(category=category)
        
        items = query.all()
        report = []
        
        for item in items:
            qty, value = InventoryService.get_stock_valuation(
                item.id, date.today(), warehouse_id
            )
            report.append({
                "item_code": item.code,
                "item_name": item.name,
                "unit": item.unit,
                "quantity": qty,
                "unit_cost": value / qty if qty > 0 else Decimal("0"),
                "total_value": value,
                "cost_method": item.cost_method,
            })
        
        return report
