"""
COA Engine - Centralized Chart of Accounts validation and behavior engine.

This module provides centralized validation for all COA-related business rules
according to Vietnamese Accounting Standards (VAS) - Circular 99/2025/TT-BTC.
"""

from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import Optional, List, Dict, Any
import json
import os


class SubledgerType(Enum):
    NONE = "none"
    CUSTOMER = "customer"
    VENDOR = "vendor"
    BANK = "bank"
    INVENTORY = "inventory"
    PROJECT = "project"
    EMPLOYEE = "employee"


class NormalBalanceType(Enum):
    DEBIT = "debit"
    CREDIT = "credit"


@dataclass
class ValidationResult:
    success: bool
    message: str = ""
    code: str = ""
    
    @classmethod
    def ok(cls, message: str = "", code: str = ""):
        return cls(success=True, message=message, code=code)
    
    @classmethod
    def error(cls, message: str, code: str = ""):
        return cls(success=False, message=message, code=code)


@dataclass
class AccountBehavior:
    code_prefix: str
    is_postable: bool = True
    normal_balance: NormalBalanceType = NormalBalanceType.DEBIT
    requires_subledger: bool = False
    subledger_type: SubledgerType = SubledgerType.NONE
    requires_cost_center: bool = False
    requires_reference: bool = False
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "code_prefix": self.code_prefix,
            "is_postable": self.is_postable,
            "normal_balance": self.normal_balance.value,
            "requires_subledger": self.requires_subledger,
            "subledger_type": self.subledger_type.value,
            "requires_cost_center": self.requires_cost_center,
            "requires_reference": self.requires_reference,
            "description": self.description,
        }


class COAEngine:
    """
    Centralized COA validation engine.
    Single source of truth for account posting rules and behaviors.
    
    Usage:
        engine = COAEngine()
        result = engine.validate_posting("1311")
        result = engine.validate_subledger("1311", entry)
    """
    
    _instance = None
    _config = None
    _behavior_cache: Dict[str, AccountBehavior] = {}
    
    def __new__(cls, config_path: str = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize(config_path)
        return cls._instance
    
    def _initialize(self, config_path: str = None):
        self._load_config(config_path)
        self._behavior_cache = {}
    
    def _load_config(self, config_path: str = None) -> Dict:
        if config_path is None:
            config_path = self._default_config_path()
        
        if not os.path.exists(config_path):
            config_path = self._fallback_config_path()
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self._config = json.load(f)
        
        return self._config
    
    def _default_config_path(self) -> str:
        base_dir = os.path.dirname(os.path.dirname(__file__))
        return os.path.join(base_dir, 'config', 'coa_behavior.json')
    
    def _fallback_config_path(self) -> str:
        base_dir = os.path.dirname(os.path.dirname(__file__))
        return os.path.join(base_dir, 'coa_behavior.json')
    
    def reload_config(self, config_path: str = None):
        self._load_config(config_path)
        self._behavior_cache = {}
    
    def get_behavior(self, account_code: str) -> AccountBehavior:
        if account_code in self._behavior_cache:
            return self._behavior_cache[account_code]
        
        matching_config = None
        longest_prefix = ""
        
        for prefix, config in self._config.get('accounts', {}).items():
            if account_code.startswith(prefix) and len(prefix) > len(longest_prefix):
                longest_prefix = prefix
                matching_config = config
        
        if matching_config is None:
            return AccountBehavior(code_prefix="")
        
        behavior = AccountBehavior(
            code_prefix=longest_prefix,
            is_postable=matching_config.get('is_postable', True),
            normal_balance=NormalBalanceType(matching_config.get('normal_balance', 'debit')),
            requires_subledger=matching_config.get('requires_subledger', False),
            subledger_type=SubledgerType(matching_config.get('subledger_type', 'none')),
            requires_cost_center=matching_config.get('requires_cost_center', False),
            requires_reference=matching_config.get('requires_reference', False),
            min_amount=Decimal(str(matching_config['min_amount'])) if matching_config.get('min_amount') else None,
            max_amount=Decimal(str(matching_config['max_amount'])) if matching_config.get('max_amount') else None,
            description=matching_config.get('description', ''),
        )
        
        self._behavior_cache[account_code] = behavior
        return behavior
    
    def validate_posting(self, account_code: str) -> ValidationResult:
        behavior = self.get_behavior(account_code)
        
        if not behavior.code_prefix:
            return ValidationResult.ok(f"Tài khoản {account_code} không có trong cấu hình, cho phép ghi sổ mặc định")
        
        if not behavior.is_postable:
            return ValidationResult.error(
                f"Tài khoản {account_code} không thể ghi sổ trực tiếp (không phải tài khoản chi tiết). "
                f"Vui lòng sử dụng tài khoản chi tiết.",
                code=behavior.code_prefix
            )
        
        return ValidationResult.ok(f"Tài khoản {account_code} có thể ghi sổ", code=behavior.code_prefix)
    
    def validate_subledger(
        self,
        account_code: str,
        customer_id: Optional[int] = None,
        vendor_id: Optional[int] = None,
        bank_account_id: Optional[int] = None,
        inventory_item_id: Optional[int] = None,
    ) -> ValidationResult:
        behavior = self.get_behavior(account_code)
        
        if not behavior.requires_subledger:
            return ValidationResult.ok()
        
        prefix = behavior.code_prefix
        
        if behavior.subledger_type == SubledgerType.CUSTOMER:
            if customer_id is None:
                return ValidationResult.error(
                    f"Tài khoản {account_code} ({behavior.description}) yêu cầu thông tin khách hàng",
                    code=prefix
                )
        
        elif behavior.subledger_type == SubledgerType.VENDOR:
            if vendor_id is None:
                return ValidationResult.error(
                    f"Tài khoản {account_code} ({behavior.description}) yêu cầu thông tin nhà cung cấp",
                    code=prefix
                )
        
        elif behavior.subledger_type == SubledgerType.BANK:
            if bank_account_id is None:
                return ValidationResult.error(
                    f"Tài khoản {account_code} ({behavior.description}) yêu cầu thông tin tài khoản ngân hàng",
                    code=prefix
                )
        
        elif behavior.subledger_type == SubledgerType.INVENTORY:
            if inventory_item_id is None:
                return ValidationResult.error(
                    f"Tài khoản {account_code} ({behavior.description}) yêu cầu thông tin vật tư/hàng hóa",
                    code=prefix
                )
        
        return ValidationResult.ok()
    
    def validate_entry_amount(
        self,
        account_code: str,
        amount: Decimal
    ) -> ValidationResult:
        behavior = self.get_behavior(account_code)
        
        if behavior.min_amount is not None and amount < behavior.min_amount:
            return ValidationResult.error(
                f"Số tiền {amount} nhỏ hơn mức tối thiểu {behavior.min_amount} cho tài khoản {account_code}",
                code=behavior.code_prefix
            )
        
        if behavior.max_amount is not None and amount > behavior.max_amount:
            return ValidationResult.error(
                f"Số tiền {amount} vượt mức tối đa {behavior.max_amount} cho tài khoản {account_code}",
                code=behavior.code_prefix
            )
        
        return ValidationResult.ok()
    
    def validate_voucher_entries(
        self,
        entries: List[Dict[str, Any]]
    ) -> List[ValidationResult]:
        errors = []
        
        for entry in entries:
            account_code = entry.get('account_code', '')
            amount = Decimal(str(entry.get('amount', 0)))
            
            result = self.validate_posting(account_code)
            if not result.success:
                errors.append(result)
            
            result = self.validate_subledger(
                account_code,
                customer_id=entry.get('customer_id'),
                vendor_id=entry.get('vendor_id'),
                bank_account_id=entry.get('bank_account_id'),
                inventory_item_id=entry.get('inventory_item_id'),
            )
            if not result.success:
                errors.append(result)
            
            result = self.validate_entry_amount(account_code, amount)
            if not result.success:
                errors.append(result)
        
        return errors
    
    def get_normal_balance(self, account_code: str) -> NormalBalanceType:
        return self.get_behavior(account_code).normal_balance
    
    def is_debit_normal(self, account_code: str) -> bool:
        return self.get_normal_balance(account_code) == NormalBalanceType.DEBIT
    
    def is_credit_normal(self, account_code: str) -> bool:
        return self.get_normal_balance(account_code) == NormalBalanceType.CREDIT
    
    def get_all_accounts_config(self) -> Dict[str, AccountBehavior]:
        result = {}
        for prefix, config in self._config.get('accounts', {}).items():
            result[prefix] = AccountBehavior(
                code_prefix=prefix,
                is_postable=config.get('is_postable', True),
                normal_balance=NormalBalanceType(config.get('normal_balance', 'debit')),
                requires_subledger=config.get('requires_subledger', False),
                subledger_type=SubledgerType(config.get('subledger_type', 'none')),
                description=config.get('description', ''),
            )
        return result
    
    @classmethod
    def reset_instance(cls):
        cls._instance = None
        cls._config = None
        cls._behavior_cache = {}
