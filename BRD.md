# Business Requirements Document (BRD)
# VAS Accounting WebApp - Thông tư 99/2025/TT-BTC Compliance

| Field | Value |
|---|---|
| Project | VAS Accounting WebApp |
| Document | BRD - Financial Reports TT99 Compliance |
| Version | 1.0 |
| Date | 2026-03-20 |
| Reference | Thông tư 99/2025/TT-BTC (effective 01/01/2026) |
| Target Compliance | 95%+ |

---

## 1. Executive Summary

This BRD defines requirements to bring the VAS Accounting WebApp financial reporting module into full compliance with **Thông tư 99/2025/TT-BTC** (replacing Thông tư 200/2014/TT-BTC). Current compliance is **~35%**. Target is **95%+** after implementation.

### Scope
- Balance Sheet (Báo cáo tình hình tài chính - B01-DN)
- Income Statement (Báo cáo kết quả hoạt động kinh doanh - B02-DN)
- Cash Flow Statement (Báo cáo lưu chuyển tiền tệ - B03-DN)
- General Ledger, Trial Balance, Account Ledger
- VAT/CIT tax reports

### Out of Scope (future phases)
- Financial Notes (Bản thuyết minh BCTC - B09-DN)
- Interim reports (B01a-DN, B02a-DN, B03a-DN)
- Non-going-concern reports (B01-DNKLT)
- Consolidated financial statements

---

## 2. TT99 Report Structure Requirements

### 2.1 Balance Sheet (B01-DN) - Báo cáo tình hình tài chính

#### A. TÀI SẢN (ASSETS)

| Mã số | Line Item | Account Mapping |
|---|---|---|
| **100** | **Tài sản ngắn hạn** | = 110 + 120 + 130 + 140 + 160 |
| 110 | Tiền và các khoản tương đương tiền | = 111 + 112 |
| 111 | Tiền | Σ Nợ(111, 112, 113) - Σ Có(111, 112, 113) |
| 112 | Các khoản tương đương tiền | Σ Nợ(1281 ≤3month) - Σ Có(1281 ≤3month) |
| 120 | Đầu tư tài chính ngắn hạn | Σ Nợ(121) - Σ Có(2291) |
| 130 | Các khoản phải thu ngắn hạn | = 131 + 135 |
| 131 | Phải thu ngắn hạn của khách hàng | Σ Nợ(131) - Σ Có(2293 short) |
| 135 | Phải thu ngắn hạn khác | Σ Nợ(1388, 141, 334 short) |
| 140 | Hàng tồn kho | = 141 + 142 |
| 141 | Hàng tồn kho | Σ Nợ(151-158) |
| 142 | Dự phòng giảm giá hàng tồn kho | Σ Có(2294) (âm) |
| 160 | Tài sản ngắn hạn khác | = 161 + 162 + 163 |
| 161 | Chi phí trả trước ngắn hạn | Σ Nợ(242) |
| 162 | Thuế GTGT được khấu trừ | Σ Nợ(133) |
| 163 | Thuế và khoản khác phải thu NS | Σ Nợ(333 debit) |
| **200** | **Tài sản dài hạn** | = 210 + 220 + 240 + 260 |
| 210 | Các khoản phải thu dài hạn | Σ Nợ(131 long, 136, 1388 long) |
| 220 | Tài sản cố định | = 221 + 224 + 227 |
| 221 | TSCĐ hữu hình | Σ Nợ(211) - Σ Có(2141) |
| 224 | TSCĐ thuê tài chính | Σ Nợ(212) - Σ Có(2142) |
| 227 | TSCĐ vô hình | Σ Nợ(213) - Σ Có(2143) |
| 240 | Bất động sản đầu tư | Σ Nợ(217) - Σ Có(2147) |
| 260 | Đầu tư tài chính dài hạn | Σ Nợ(221, 222, 2282) - Σ Có(2292) |
| **270** | **Tài sản dài hạn khác** | = 271 + 272 + 273 |
| 271 | Chi phí sản xuất KD dở dang dài hạn | Σ Nợ(154 long) |
| 272 | Xây dựng cơ bản dở dang | Σ Nợ(241) |
| 273 | Chi phí chờ phân bổ dài hạn | Σ Nợ(242, 243) |

#### B. NỢ PHẢI TRẢ (LIABILITIES)

| Mã số | Line Item | Account Mapping |
|---|---|---|
| **300** | **Nợ ngắn hạn** | = 310 + 320 + 330 + 340 + 350 |
| 310 | Phải trả người bán ngắn hạn | Σ Có(331 short) |
| 320 | Người mua trả tiền trước ngắn hạn | Σ Có(131 credit short) |
| 330 | Thuế và các khoản phải nộp NS | Σ Có(333) |
| 340 | Phải trả người lao động | Σ Có(334) |
| 350 | Nợ ngắn hạn khác | Σ Có(336, 338, 341 short) |
| **400** | **Nợ dài hạn** | = 410 + 420 + 430 |
| 410 | Phải trả người bán dài hạn | Σ Có(331 long) |
| 420 | Vay và nợ thuê tài chính dài hạn | Σ Có(341 long) |
| 430 | Nợ dài hạn khác | Σ Có(338 long) |

#### C. VỐN CHỦ SỞ HỮU (EQUITY)

| Mã số | Line Item | Account Mapping |
|---|---|---|
| **500** | **Vốn chủ sở hữu** | = 510 + 520 + 530 |
| 510 | Vốn chủ sở hữu | = 411 + 412 + 413 + 414 + 415 + 417 + 418 + 419 |
| 411 | Vốn góp của chủ sở hữu | Σ Có(411) - Σ Nợ(411) |
| 421 | LNST chưa phân phối | Σ Có(421) - Σ Nợ(421) |
| 520 | Các quỹ thuộc VCSH | Σ Có(412, 413, 414, 415, 417, 418, 419) |
| 530 | Chênh lệch đánh giá lại TSCĐ | Σ Có(412) |

#### BALANCE CHECK
```
Mã số 100 + Mã số 200 = Mã số 300 + Mã số 400 + Mã số 500
(Total Assets = Total Liabilities + Equity)
```

### 2.2 Income Statement (B02-DN) - Báo cáo kết quả hoạt động kinh doanh

| Mã số | Line Item | Account Mapping |
|---|---|---|
| 10 | Doanh thu bán hàng và CCDV | Σ Có(511) |
| 20 | Các khoản giảm trừ doanh thu | Σ Nợ(521) (âm) |
| 30 | **Doanh thu thuần** | = 10 - 20 |
| 40 | Giá vốn hàng bán | Σ Nợ(632) |
| 50 | **Lợi nhuận gộp** | = 30 - 40 |
| 60 | Doanh thu hoạt động tài chính | Σ Có(515) |
| 70 | Chi phí tài chính | Σ Nợ(635) |
| 80 | Chi phí bán hàng | Σ Nợ(641) |
| 90 | Chi phí QL doanh nghiệp | Σ Nợ(642) |
| 100 | Lợi nhuận khác | Σ Có(711) - Σ Nợ(811) |
| 110 | **Lợi nhuận khác, chi phí khác** | = 100 |
| 120 | **Lợi nhuận trước thuế TNDN** | = 50 + 60 - 70 - 80 - 90 + 110 |
| 130 | Chi phí thuế TNDN hiện hành | Σ Nợ(8211) |
| 140 | Chi phí thuế TNDN hoãn lại | Σ Nợ(8212) - Σ Có(8212) |
| 150 | **Lợi nhuận sau thuế TNDN** | = 120 - 130 - 140 |

### 2.3 Cash Flow (B03-DN) - Báo cáo lưu chuyển tiền tệ (Indirect Method)

| Mã số | Line Item | Calculation |
|---|---|---|
| **I** | **LCTT từ hoạt động kinh doanh** | |
| 01 | Lợi nhuận trước thuế | From B02 line 120 |
| 02 | Khấu hao TSCĐ | Σ Nợ(214x) period |
| 03 | Điều chỉnh khác | Provisions, unrealized gains/losses |
| 10 | Thay đổi KPHĐ | ΔAssets_working - ΔLiabilities_working |
| 11 | Tăng/giảm các khoản phải thu | -(Δ131 + Δ136 + Δ1388) |
| 12 | Tăng/giảm hàng tồn kho | -(Δ15x) |
| 13 | Tăng/giảm các khoản phải trả | Δ(331 + 333 + 334 + 338) |
| 20 | **LCTT ròng từ HĐKD** | = 01 + 02 + 03 + 11 + 12 + 13 |
| **II** | **LCTT từ hoạt động đầu tư** | |
| 21 | Mua sắm TSCĐ, BĐSĐT | -Σ Nợ(211, 212, 213, 217) period |
| 22 | Thu tiền từ bán TSCĐ | Σ Có(211, 212, 213) period |
| 23 | Đầu tư dài hạn | -Δ(221, 222, 2282) |
| 30 | **LCTT ròng từ HĐĐT** | = 21 + 22 + 23 |
| **III** | **LCTT từ hoạt động tài chính** | |
| 31 | Vay thêm / trả nợ vay | Δ(341) |
| 32 | Phát hành cổ phiếu | Δ(411) |
| 33 | Chi trả cổ tức | -Σ Nợ(421 period) |
| 40 | **LCTT ròng từ HĐTC** | = 31 + 32 + 33 |
| **IV** | **LCTT ròng trong kỳ** | = 20 + 30 + 40 |
| 50 | Tiền và TTT cuối kỳ | Σ Nợ(11x end) - Σ Có(11x end) |

---

## 3. Technical Requirements

### 3.1 Repository Layer
- `get_account_balance_range(code_prefix, start, end)` - period balance change
- `get_account_balance_at(code, end_date)` - cumulative balance at date
- `get_fixed_asset_depreciation(start, end)` - depreciation for period
- `get_account_balances_for_ma_so(ma_so, end_date)` - grouped by TT99 Mã số

### 3.2 Service Layer
- Rename `BalanceSheetService` → `FinancialPositionService` (Báo cáo tình hình tài chính)
- Rename `IncomeStatementService` → `BusinessResultService` (Báo cáo kết quả hoạt động kinh doanh)
- Each service returns `Dict` with keys: `ma_so`, `line_name_vi`, `amount`
- Balance sheet must include `short_term_assets`, `long_term_assets`, `short_term_liabilities`, `long_term_liabilities`, `equity` sections
- Cash flow must use period balance changes, not cumulative

### 3.3 Validation Rules
- Balance Sheet: `100 + 200 == 300 + 400 + 500`
- Income Statement: `30 = 10 - 20`, `50 = 30 - 40`, `120 = 50 + 60 - 70 - 80 - 90 + 110`
- Cash Flow: `opening_cash + net_cash_flow == closing_cash` (must match actual 11x balance)

### 3.4 Data Requirements
- Only POSTED vouchers included
- Account level: postable (detail) accounts only for sums, parent accounts for totals
- Depreciation: account 214x (2141, 2142, 2143, 2147)
- Retained Earnings: account 421 (Lợi nhuận sau thuế chưa phân phối)

---

## 4. Implementation Phases

| Phase | Scope | Status |
|---|---|---|
| Phase 1 | BRD + Repository layer fixes | In Progress |
| Phase 2 | Balance Sheet (B01-DN) full TT99 structure | Pending |
| Phase 3 | Income Statement (B02-DN) full TT99 structure | Pending |
| Phase 4 | Cash Flow (B03-DN) full TT99 structure | Pending |
| Phase 5 | Tests + validation | Pending |

---

## 5. Acceptance Criteria

1. Balance Sheet output includes all Mã số per TT99 B01-DN
2. Balance Sheet is balanced: Assets = Liabilities + Equity
3. Income Statement includes all 15 line items per TT99 B02-DN
4. Income Statement internally consistent: 30=10-20, 50=30-40, 120 calculated correctly
5. Cash Flow opening_cash uses actual account 11x balance
6. Cash Flow includes depreciation adjustment
7. Cash Flow investing activities uses actual fixed asset changes
8. All reports only use POSTED vouchers
9. All reports support date range parameters
10. Report names in Vietnamese per TT99 (not English)
