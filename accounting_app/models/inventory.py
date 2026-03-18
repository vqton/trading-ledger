from datetime import datetime
from decimal import Decimal
from typing import Optional

from core.database import db
from core.utils import utc_now


class Warehouse(db.Model):
    """Warehouse model for inventory tracking."""

    __tablename__ = "warehouses"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(500), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    stock_transactions = db.relationship("StockTransaction", backref="warehouse", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<Warehouse {self.code} - {self.name}>"


class InventoryItem(db.Model):
    """Inventory Item model."""

    __tablename__ = "inventory_items"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    unit = db.Column(db.String(20), nullable=True)
    category = db.Column(db.String(50), nullable=True)
    default_warehouse_id = db.Column(db.Integer, db.ForeignKey("warehouses.id"), nullable=True)
    cost_method = db.Column(db.String(20), nullable=False, default="average")
    purchase_price = db.Column(db.Numeric(18, 2), default=Decimal("0.00"))
    sale_price = db.Column(db.Numeric(18, 2), default=Decimal("0.00"))
    reorder_level = db.Column(db.Numeric(18, 2), default=Decimal("0.00"))
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    default_warehouse = db.relationship("Warehouse", backref="items")
    stock_transactions = db.relationship("StockTransaction", backref="item", lazy="dynamic")

    __table_args__ = (
        db.Index("ix_item_category", "category"),
    )

    def __repr__(self) -> str:
        return f"<InventoryItem {self.code} - {self.name}>"

    @property
    def current_stock(self) -> Decimal:
        """Calculate current stock quantity."""
        stock_in = Decimal("0")
        stock_out = Decimal("0")
        for t in self.stock_transactions.filter_by(transaction_type="in"):
            stock_in += t.quantity
        for t in self.stock_transactions.filter_by(transaction_type="out"):
            stock_out += t.quantity
        return stock_in - stock_out


class StockTransaction(db.Model):
    """Stock Transaction model for inventory movements."""

    __tablename__ = "stock_transactions"

    id = db.Column(db.Integer, primary_key=True)
    transaction_no = db.Column(db.String(50), unique=True, nullable=False, index=True)
    transaction_date = db.Column(db.Date, nullable=False, index=True)
    transaction_type = db.Column(db.String(20), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey("inventory_items.id"), nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey("warehouses.id"), nullable=False)
    quantity = db.Column(db.Numeric(18, 2), nullable=False)
    unit_cost = db.Column(db.Numeric(18, 2), nullable=False)
    total_amount = db.Column(db.Numeric(18, 2), nullable=False)
    reference = db.Column(db.String(100), nullable=True)
    description = db.Column(db.String(500), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)

    creator = db.relationship("User", backref="stock_transactions")

    __table_args__ = (
        db.Index("ix_stock_item_warehouse", "item_id", "warehouse_id"),
        db.Index("ix_stock_date_type", "transaction_date", "transaction_type"),
    )

    def __repr__(self) -> str:
        return f"<StockTransaction {self.transaction_no} {self.transaction_type}>"

    @classmethod
    def generate_transaction_no(cls, transaction_type: str) -> str:
        """Generate stock transaction number."""
        from datetime import datetime
        year = datetime.now().year
        prefix = "SI" if transaction_type == "in" else "SO" if transaction_type == "out" else "SA"
        last_txn = cls.query.filter(
            cls.transaction_no.like(f"{prefix}-{year}%")
        ).order_by(cls.transaction_no.desc()).first()

        if last_txn:
            last_num = int(last_txn.transaction_no.split("-")[-1])
            new_num = last_num + 1
        else:
            new_num = 1

        return f"{prefix}-{year}-{new_num:05d}"


class InventoryValuationMethod:
    """Inventory valuation method constants."""

    FIFO = "fifo"
    AVERAGE = "average"
    SPECIFIC = "specific"

    CHOICES = [
        (FIFO, "FIFO - Nhập trước xuất trước"),
        (AVERAGE, "Bình quân gia quyền"),
        (SPECIFIC, "Đích danh - Specific Identification"),
    ]


class TransactionType:
    """Stock transaction type constants."""

    STOCK_IN = "in"
    STOCK_OUT = "out"
    ADJUSTMENT = "adjustment"

    CHOICES = [
        (STOCK_IN, "Nhập kho"),
        (STOCK_OUT, "Xuất kho"),
        (ADJUSTMENT, "Điều chỉnh"),
    ]


class InventoryBatch(db.Model):
    """Inventory Batch/Lot model for Specific Identification method.

    Tracks individual batches of inventory items with specific costs.
    Used when items can be individually identified (e.g., serial numbers).
    """

    __tablename__ = "inventory_batches"

    id = db.Column(db.Integer, primary_key=True)
    batch_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    item_id = db.Column(db.Integer, db.ForeignKey("inventory_items.id"), nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey("warehouses.id"), nullable=False)
    quantity = db.Column(db.Numeric(18, 2), nullable=False, default=Decimal("0.00"))
    unit_cost = db.Column(db.Numeric(18, 2), nullable=False)
    total_cost = db.Column(db.Numeric(18, 2), nullable=False)
    remaining_qty = db.Column(db.Numeric(18, 2), nullable=False, default=Decimal("0.00"))
    expiry_date = db.Column(db.Date, nullable=True)
    lot_number = db.Column(db.String(50), nullable=True)
    serial_number = db.Column(db.String(100), nullable=True)
    receipt_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    item = db.relationship("InventoryItem", backref="batches")
    warehouse = db.relationship("Warehouse", backref="batches")

    __table_args__ = (
        db.Index("ix_batch_item_wh", "item_id", "warehouse_id"),
        db.Index("ix_batch_expiry", "expiry_date"),
    )

    def __repr__(self) -> str:
        return f"<InventoryBatch {self.batch_code} - {self.item_id}>"

    @classmethod
    def generate_batch_code(cls, item_code: str) -> str:
        """Generate batch code for an item."""
        from datetime import datetime
        year = datetime.now().year
        last_batch = cls.query.filter(
            cls.batch_code.like(f"BATCH-{item_code}%")
        ).order_by(cls.batch_code.desc()).first()

        if last_batch:
            last_num = int(last_batch.batch_code.split("-")[-1])
            new_num = last_num + 1
        else:
            new_num = 1

        return f"BATCH-{item_code}-{year}-{new_num:04d}"

    def allocate_quantity(self, qty: Decimal) -> "InventoryBatch":
        """Allocate quantity from this batch for stock out."""
        if qty > self.remaining_qty:
            raise ValueError(f"Không đủ số lượng trong lô: {self.batch_code}")
        self.remaining_qty -= qty
        return self
