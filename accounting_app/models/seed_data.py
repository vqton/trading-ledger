"""Vietnamese Chart of Accounts - Circular 99/2025/TT-BTC Appendix II.

Import from coa-circular99-appendix-ii-full.json
Uses coa_behavior.json for posting and subledger rules.
"""

import json
import os
import re

from models.account import Account, AccountType, NormalBalance
from core.database import db
from services.coa_engine import COAEngine, SubledgerType, NormalBalanceType


TYPE_MAP = {
    "Asset": AccountType.ASSET,
    "Liability": AccountType.LIABILITY,
    "Equity": AccountType.EQUITY,
    "Revenue": AccountType.REVENUE,
    "Expense": AccountType.EXPENSE,
}

NORMAL_BALANCE_MAP = {
    "Debit": NormalBalance.DEBIT,
    "Credit": NormalBalance.CREDIT,
}


def create_chart_of_accounts():
    """Create Vietnamese standard chart of accounts - Circular 99/2025.
    
    Uses COA Engine for determining is_postable and subledger requirements.
    TT99 Structure:
    - Level 1: 3-digit (111, 112, 131...) = PARENT (non-postable)
    - Level 2: 4-digit (1111, 1121, 1311...) = POSTABLE children
    
    Uses coa_behavior.json for specific account behaviors.
    """
    
    if Account.query.first():
        return
    
    coa_engine = COAEngine()
    
    json_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "coa-circular99-appendix-ii-full.json"
    )
    
    with open(json_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
    data = json.loads(content)
    
    code_to_account = {}
    
    for item in data.get("accounts", []):
        code = item["code"]
        code_len = len(code)
        
        sub_accounts = item.get("sub_accounts") or []
        
        has_explicit_children = len(sub_accounts) > 0
        
        behavior = coa_engine.get_behavior(code)
        
        if has_explicit_children:
            is_postable = False
            level = code_len
        elif code_len == 3:
            is_postable = behavior.is_postable
            level = 1
        else:
            is_postable = True
            level = code_len - 2
        
        account = Account(
            code=code,
            name_vi=item["name"],
            name_en=item.get("name_en"),
            level=level,
            account_type=TYPE_MAP.get(item["type"], AccountType.ASSET),
            normal_balance=NORMAL_BALANCE_MAP.get(item.get("normal_balance"), NormalBalance.DEBIT),
            is_postable=is_postable,
            is_active=True,
        )
        
        db.session.add(account)
        db.session.flush()
        code_to_account[code] = account
        
        for sub in item.get("sub_accounts", []):
            sub_code = sub["code"]
            sub_level = len(sub_code) - 2
            
            sub_behavior = coa_engine.get_behavior(sub_code)
            
            sub_account = Account(
                code=sub_code,
                name_vi=sub["name"],
                name_en=sub.get("name_en"),
                level=sub_level,
                account_type=TYPE_MAP.get(item["type"], AccountType.ASSET),
                normal_balance=NORMAL_BALANCE_MAP.get(item.get("normal_balance"), NormalBalance.DEBIT),
                is_postable=sub_behavior.is_postable,
                is_active=True,
            )
            
            db.session.add(sub_account)
            db.session.flush()
            code_to_account[sub_code] = sub_account
    
    for code, account in code_to_account.items():
        if len(code) == 4:
            parent_code = code[:3]
            if parent_code in code_to_account:
                account.parent_id = code_to_account[parent_code].id
    
    for item in data.get("accounts", []):
        parent_code = item["code"]
        if parent_code in code_to_account and item.get("sub_accounts"):
            parent_account = code_to_account[parent_code]
            for sub in item.get("sub_accounts", []):
                sub_code = sub["code"]
                if sub_code in code_to_account:
                    code_to_account[sub_code].parent_id = parent_account.id
    
    db.session.commit()
