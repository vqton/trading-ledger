# -*- coding: utf-8 -*-
"""
Chuyển đổi file Excel hệ thống tài khoản kế toán (COA) sang JSON phân cấp
Hỗ trợ level 1 → 4 dựa trên độ dài mã số
"""

import pandas as pd
import json
from pathlib import Path
from typing import Dict, List, Optional


def determine_level(code: str) -> int:
    """Xác định level dựa trên độ dài mã số (sau khi loại bỏ dấu chấm/phẩy nếu có)"""
    code_clean = str(code).strip().replace(".", "").replace(",", "")
    if not code_clean.isdigit():
        return 0
    length = len(code_clean)
    if length == 3:
        return 1
    elif length == 4:
        return 2
    elif length == 5:
        return 3
    elif length == 6:
        return 4
    else:
        return 0  # không phải tài khoản


def guess_account_type(code: str) -> str:
    """Dự đoán loại tài khoản dựa trên mã số (rất cơ bản)"""
    if code.startswith(('1', '2')):
        return "Asset"
    elif code.startswith('3'):
        return "Liability"
    elif code.startswith('4'):
        return "Equity"
    elif code.startswith(('5', '7')):
        return "Revenue"
    elif code.startswith(('6', '8')):
        return "Expense"
    elif code == "911":
        return "Nominal"
    else:
        return "Other"


def guess_normal_balance(code: str) -> str:
    """Dự đoán số dư thường (Debit/Credit)"""
    if code.startswith(('1', '2', '911')):
        return "Debit"
    elif code.startswith(('3', '4', '5', '7')):
        return "Credit"
    elif code.startswith(('6', '8')):
        return "Debit"
    # một số ngoại lệ
    if code.startswith('214') or code.startswith('229'):
        return "Credit"  # hao mòn, dự phòng
    return "Debit"


def find_parent(accounts: List[Dict], current_code: str, current_level: int) -> Optional[str]:
    """Tìm tài khoản cha gần nhất (level thấp hơn 1 bậc)"""
    if current_level <= 1:
        return None
    
    current_clean = current_code.strip().replace(".", "").replace(",", "")
    
    for acc in reversed(accounts):  # tìm ngược từ dưới lên để lấy cha gần nhất
        parent_code = acc["code"].replace(".", "").replace(",", "")
        parent_level = acc["level"]
        
        if parent_level >= current_level:
            continue
        if parent_level != current_level - 1:
            continue
            
        # kiểm tra xem current_code có bắt đầu bằng parent_code không
        if current_clean.startswith(parent_code):
            return acc["code"]
    
    return None


def excel_to_coa_json(
    excel_path: str,
    sheet_name: str = "Sheet1",
    output_json: str = "coa_tt99.json",
    start_row: int = 4  # dòng đầu tiên có dữ liệu tài khoản (thường bỏ header)
):
    # Đọc file Excel
    df = pd.read_excel(
        excel_path,
        sheet_name=sheet_name,
        header=None,           # không dùng header mặc định
        skiprows=start_row-1,  # bỏ các dòng header
        dtype=str
    )

    # Đặt tên cột theo ý nghĩa (dựa trên file mẫu của bạn)
    df.columns = ["stt", "code1", "code2", "name"]

    # Tạo cột code tổng hợp
    df["code"] = df["code1"].combine_first(df["code2"]).fillna("")
    df["name"] = df["name"].fillna("").str.strip()

    # Lọc chỉ các dòng có code hợp lệ
    df = df[df["code"].str.strip().str.match(r"^\d{3,6}$", na=False)]

    accounts: List[Dict] = []
    code_to_acc: Dict[str, Dict] = {}

    for _, row in df.iterrows():
        code = str(row["code"]).strip()
        name = str(row["name"]).strip()

        if not code or not name:
            continue

        level = determine_level(code)
        if level == 0:
            continue

        acc = {
            "code": code,
            "name": name,
            "level": level,
            "type": guess_account_type(code),
            "normal_balance": guess_normal_balance(code),
        }

        parent = find_parent(accounts, code, level)
        if parent:
            acc["parent"] = parent

        accounts.append(acc)
        code_to_acc[code] = acc

    # Metadata
    metadata = {
        "source": "Phụ lục II – Thông tư 99/2025/TT-BTC",
        "effective_date": "2026-01-01",
        "max_level": 4,
        "total_accounts": len(accounts),
        "description": "Hệ thống tài khoản kế toán doanh nghiệp Việt Nam",
        "note": "Tự động sinh từ file Excel",
        "generated": "2026-03"
    }

    output_data = {
        "metadata": metadata,
        "accounts": accounts
    }

    # Lưu file JSON
    output_path = Path(output_json)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"Đã tạo file JSON: {output_path.absolute()}")
    print(f"Tổng số tài khoản: {len(accounts)}")


if __name__ == "__main__":
    # Thay đổi đường dẫn file Excel của bạn
    excel_file = "COA_TT99.xlsx"          # ← thay bằng đường dẫn thực tế
    output_file = "coa_tt99_full.json"

    excel_to_coa_json(
        excel_path=excel_file,
        sheet_name="Sheet1",
        output_json=output_file,
        start_row=5     # điều chỉnh nếu header khác (thử 4,5,6)
    )