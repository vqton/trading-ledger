"""Currency Service - Exchange rates and foreign currency transactions."""

from datetime import date, timedelta
from decimal import Decimal
from typing import Dict, List, Optional

from core.database import db
from models.currency import Currency, ExchangeRate, FCTransactionType, ForeignCurrencyTransaction


class CurrencyService:
    """Service for currency operations."""

    @staticmethod
    def get_all_currencies() -> List[Currency]:
        """Get all currencies."""
        return Currency.query.filter_by(is_active=True).all()

    @staticmethod
    def get_currency(currency_id: int) -> Optional[Currency]:
        """Get currency by ID."""
        return db.session.get(Currency, currency_id)

    @staticmethod
    def get_currency_by_code(code: str) -> Optional[Currency]:
        """Get currency by code."""
        return Currency.query.filter_by(code=code).first()

    @staticmethod
    def get_base_currency() -> Optional[Currency]:
        """Get base currency."""
        return Currency.query.filter_by(is_base=True).first()

    @staticmethod
    def create_currency(currency_data: Dict) -> Currency:
        """Create new currency."""
        existing = Currency.query.filter_by(code=currency_data["code"]).first()
        if existing:
            raise ValueError(f"Mã tiền tệ {currency_data['code']} đã tồn tại")

        currency = Currency(
            code=currency_data["code"],
            name=currency_data["name"],
            symbol=currency_data.get("symbol"),
            exchange_rate=currency_data.get("exchange_rate", Decimal("1")),
            is_base=currency_data.get("is_base", False),
            is_active=True,
        )
        db.session.add(currency)
        db.session.commit()
        return currency

    @staticmethod
    def update_exchange_rate(currency_id: int, rate: Decimal) -> Currency:
        """Update exchange rate for a currency."""
        currency = db.session.get(Currency, currency_id)
        if not currency:
            raise ValueError("Currency not found")

        currency.exchange_rate = rate
        db.session.commit()
        return currency

    @staticmethod
    def get_exchange_rate(
        from_currency_id: int,
        to_currency_id: int,
        effective_date: date = None,
    ) -> Decimal:
        """Get exchange rate for currency pair."""
        if effective_date is None:
            effective_date = date.today()

        rate = ExchangeRate.query.filter(
            ExchangeRate.from_currency_id == from_currency_id,
            ExchangeRate.to_currency_id == to_currency_id,
            ExchangeRate.effective_date <= effective_date,
        ).order_by(ExchangeRate.effective_date.desc()).first()

        if rate:
            return rate.rate

        from_curr = db.session.get(Currency, from_currency_id)
        to_curr = db.session.get(Currency, to_currency_id)

        if from_curr and to_curr:
            return to_curr.exchange_rate / from_curr.exchange_rate

        return Decimal("1")

    @staticmethod
    def add_exchange_rate(rate_data: Dict) -> ExchangeRate:
        """Add exchange rate."""
        rate = ExchangeRate(
            from_currency_id=rate_data["from_currency_id"],
            to_currency_id=rate_data["to_currency_id"],
            rate=rate_data["rate"],
            effective_date=rate_data["effective_date"],
        )
        db.session.add(rate)
        db.session.commit()
        return rate

    @staticmethod
    def convert_amount(
        amount: Decimal,
        from_currency_id: int,
        to_currency_id: int,
        effective_date: date = None,
    ) -> Decimal:
        """Convert amount from one currency to another."""
        if from_currency_id == to_currency_id:
            return amount

        rate = CurrencyService.get_exchange_rate(
            from_currency_id, to_currency_id, effective_date
        )
        return amount * rate

    @staticmethod
    def create_fc_transaction(transaction_data: Dict, user_id: int) -> ForeignCurrencyTransaction:
        """Create foreign currency transaction."""
        currency = db.session.get(Currency, transaction_data["currency_id"])
        if not currency:
            raise ValueError("Currency not found")

        rate = transaction_data.get("exchange_rate")
        if not rate:
            rate = CurrencyService.get_exchange_rate(
                currency.id,
                CurrencyService.get_base_currency().id,
                transaction_data["transaction_date"],
            )

        amount_vnd = transaction_data["amount"] * rate

        transaction = ForeignCurrencyTransaction(
            transaction_no=ForeignCurrencyTransaction.generate_transaction_no(
                transaction_data["transaction_type"]
            ),
            transaction_date=transaction_data["transaction_date"],
            transaction_type=transaction_data["transaction_type"],
            currency_id=transaction_data["currency_id"],
            amount=transaction_data["amount"],
            exchange_rate=rate,
            amount_vnd=amount_vnd,
            reference=transaction_data.get("reference"),
            description=transaction_data.get("description"),
            created_by=user_id,
        )
        db.session.add(transaction)
        db.session.commit()
        return transaction

    @staticmethod
    def get_fc_balance(currency_id: int, as_of_date: date = None) -> Decimal:
        """Get foreign currency balance."""
        if as_of_date is None:
            as_of_date = date.today()

        transactions = ForeignCurrencyTransaction.query.filter(
            ForeignCurrencyTransaction.currency_id == currency_id,
            ForeignCurrencyTransaction.transaction_date <= as_of_date,
        ).all()

        total_received = sum(t.amount for t in transactions if t.transaction_type in [FCTransactionType.RECEIPT, FCTransactionType.SALE])
        total_paid = sum(t.amount for t in transactions if t.transaction_type in [FCTransactionType.PAYMENT, FCTransactionType.PURCHASE])

        return total_received - total_paid

    @staticmethod
    def get_fc_balance_vnd(currency_id: int, as_of_date: date = None) -> Decimal:
        """Get foreign currency balance in VND."""
        if as_of_date is None:
            as_of_date = date.today()

        transactions = ForeignCurrencyTransaction.query.filter(
            ForeignCurrencyTransaction.currency_id == currency_id,
            ForeignCurrencyTransaction.transaction_date <= as_of_date,
        ).all()

        return sum(t.amount_vnd for t in transactions if t.transaction_type in [FCTransactionType.RECEIPT, FCTransactionType.SALE]) - \
               sum(t.amount_vnd for t in transactions if t.transaction_type in [FCTransactionType.PAYMENT, FCTransactionType.PURCHASE])

    @staticmethod
    def get_exchange_rate_history(
        from_currency_id: int,
        to_currency_id: int,
        start_date: date,
        end_date: date,
    ) -> List[Dict]:
        """Get exchange rate history."""
        rates = ExchangeRate.query.filter(
            ExchangeRate.from_currency_id == from_currency_id,
            ExchangeRate.to_currency_id == to_currency_id,
            ExchangeRate.effective_date >= start_date,
            ExchangeRate.effective_date <= end_date,
        ).order_by(ExchangeRate.effective_date).all()

        return [
            {
                "date": r.effective_date,
                "rate": r.rate,
            }
            for r in rates
        ]

    @staticmethod
    def seed_default_currencies() -> None:
        """Seed default currencies."""
        if Currency.query.first():
            return

        default_currencies = [
            {"code": "VND", "name": "Vietnamese Dong", "symbol": "₫", "exchange_rate": Decimal("1"), "is_base": True},
            {"code": "USD", "name": "US Dollar", "symbol": "$", "exchange_rate": Decimal("24500"), "is_base": False},
            {"code": "EUR", "name": "Euro", "symbol": "€", "exchange_rate": Decimal("26500"), "is_base": False},
            {"code": "JPY", "name": "Japanese Yen", "symbol": "¥", "exchange_rate": Decimal("165"), "is_base": False},
            {"code": "CNY", "name": "Chinese Yuan", "symbol": "¥", "exchange_rate": Decimal("3400"), "is_base": False},
            {"code": "GBP", "name": "British Pound", "symbol": "£", "exchange_rate": Decimal("31000"), "is_base": False},
        ]

        for curr_data in default_currencies:
            currency = Currency(**curr_data)
            db.session.add(currency)

        db.session.commit()
