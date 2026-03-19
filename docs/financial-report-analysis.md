# Financial Report Analysis - Circular 99/2025/TT-BTC

**Version:** 1.0  
**Circular:** 99/2025/TT-BTC  
**Last Updated:** 2026-03-19

---

## Executive Summary

This document analyzes all financial reports required by Circular 99/2025/TT-BTC (Phụ lục IV) and identifies which models are missing to support complete reporting.

---

## Part 1: Required Financial Reports

### Standard Reports (Phụ lục IV)

| Code | Report Name | Status | Priority |
|------|-------------|--------|----------|
| B01 | Báo cáo tình hình tài chính | 🔄 Partial | Required |
| B02 | Kết quả hoạt động kinh doanh | 🔄 Partial | Required |
| B03 | Lưu chuyển tiền tệ | 🔄 Partial | Required |
| B05 | Thuyết minh BCTC | 📋 Pending | Required |

### Management Reports

| Code | Report Name | Status | Priority |
|------|-------------|--------|----------|
| AR | Công nợ phải thu (AR Aging) | 📋 Pending | High |
| AP | Công nợ phải trả (AP Aging) | 📋 Pending | High |
| TB | Bảng cân đối tài khoản | ✅ | High |
| GL | Sổ cái tổng hợp | ✅ | High |
| SL | Sổ chi tiết | 🔄 Partial | High |

### Tax Reports

| Code | Report Name | Status | Priority |
|------|-------------|--------|----------|
| VAT | Khai thuế GTGT | ✅ | Required |
| CIT | Tạm tính/Quyết toán TNDN | ✅ | Required |
| PIT | Quyết toán TNCN | 📋 Pending | Required |

---

## Part 2: Report-by-Report Analysis

### B01 - Báo cáo tình hình tài chính (Financial Position Report)

**Formerly:** Bảng cân đối kế toán

#### Structure (per TT99)

```
A. TÀI SẢN (ASSETS)
   A100. Tài sản ngắn hạn
      A110. Tiền và tương đương tiền (TK 111, 112, 113)
      A120. Các khoản phải thu ngắn hạn (TK 131, 136, 138)
      A130. Hàng tồn kho (TK 151-158)
      A140. Tài sản ngắn hạn khác
   
   A200. Tài sản dài hạn
      A210. Tài sản cố định (TK 211, 212, 213, 214)
      A220. Bất động sản đầu tư (TK 217)
      A230. Tài sản sinh học (TK 215) ← NEW in TT99
      A240. Đầu tư tài chính dài hạn (TK 221, 222, 228)

B. NGUỒN VỐN (LIABILITIES + EQUITY)
   B100. Nợ phải trả
      B110. Nợ ngắn hạn (TK 331, 332, 333, 334, 335, 336, 337, 338)
      B120. Nợ dài hạn (TK 341, 343, 344, 347, 352)
   
   B200. VỐN CHỦ SỞ HỮU
      B210. Vốn góp của chủ sở hữu (TK 411, 412, 413, 414, 418, 419)
      B220. Lợi nhuận sau thuế chưa phân phối (TK 421)
```

#### Validation Rules

```
B01-001: Tổng Tài sản = Tổng Nguồn vốn (BẮT BUỘC)
B01-002: Tài sản ngắn hạn = Tài sản có chu kỳ ≤ 12 tháng
B01-003: Tài sản dài hạn = Tài sản có chu kỳ > 12 tháng
B01-004: Nợ ngắn hạn = Nợ thời hạn ≤ 12 tháng
B01-005: Nợ dài hạn = Nợ thời hạn > 12 tháng
B01-006: Sắp xếp theo tính thanh khoản giảm dần
```

#### Data Requirements

| Account Range | Data Needed | Model Required | Status |
|--------------|-------------|---------------|--------|
| 111, 112, 113 | Cash & bank balances | `BankAccount` | ✅ |
| 121, 128 | Investment balances | `Account` | ✅ |
| **131** | AR by customer | `Customer` | ❌ |
| 133 | VAT receivable | `TaxPolicy` | ✅ |
| **136, 138** | Internal & other receivables | `Employee` | ❌ |
| **141** | Advances by employee | `Employee` | ❌ |
| 151-158 | Inventory | `InventoryItem`, `Warehouse` | ✅ |
| **171** | Repo transactions | - | ✅ |
| 211-214 | Fixed assets | `FixedAsset` | ✅ |
| **215** | Biological assets | `BiologicalAsset` | ❌ |
| 217 | Investment property | `Account` | ✅ |
| 221, 222, 228 | Long-term investments | `Account` | ✅ |
| **331** | AP by vendor | `Vendor` | ❌ |
| **332** | Dividends payable | - | ❌ |
| 333 | Tax payable | `TaxPolicy` | ✅ |
| **334** | Payroll payable | `Employee` | ❌ |
| 341, 343, 344 | Loans & bonds | `BankAccount` | ✅ |
| 347 | Deferred tax | `Account` | ✅ |
| 352 | Provisions | `Account` | ✅ |
| 411, 412, 413 | Equity accounts | `Account` | ✅ |
| **421** | Retained earnings | `Account` | ✅ |

#### Missing Models for B01

| Model | File | Description | Priority |
|-------|------|-------------|----------|
| `Customer` | `models/customer.py` | AR subledger (TK 131) | **HIGH** |
| `Vendor` | `models/vendor.py` | AP subledger (TK 331) | **HIGH** |
| `Employee` | `models/employee.py` | Advances (TK 141), Payroll (TK 334) | **HIGH** |
| `BiologicalAsset` | `models/biological_asset.py` | TK 215 (NEW in TT99) | **MEDIUM** |
| `DividendPayable` | `models/dividend.py` | TK 332 (NEW in TT99) | **MEDIUM** |

---

### B02 - Kết quả hoạt động kinh doanh (Income Statement)

#### Structure (per TT99)

```
1. Doanh thu bán hàng và cung cấp dịch vụ (TK 511)
2. Các khoản giảm trừ doanh thu (TK 521)
   **Doanh thu thuần = 1 - 2**
3. Giá vốn hàng bán (TK 632)
   **Lợi nhuận gộp = Doanh thu thuần - 3**
4. Doanh thu hoạt động tài chính (TK 515)
5. Chi phí tài chính (TK 635)
   - Trong đó: Chi phí lãi vay
6. Chi phí bán hàng (TK 641)
7. Chi phí quản lý doanh nghiệp (TK 642)
8. Lợi nhuận thuần từ HĐKD = 2 + 4 - 5 - 6 - 7
9. Thu nhập khác (TK 711)
10. Chi phí khác (TK 811)
11. Lợi nhuận khác = 9 - 10
12. Chi phí thuế TNDN hiện hành (TK 82111)
13. Chi phí thuế TNDN hoãn lại
14. **Lợi nhuận sau thuế = 8 + 11 - 12 - 13**
```

#### New TT99 Requirements

```
B02-001: Doanh thu thuần = Doanh thu - Các khoản giảm trừ
B02-002: Lợi nhuận gộp = Doanh thu thuần - Giá vốn
B02-003: Lợi nhuận thuần = Lợi nhuận gộp - Chi phí - Thuế
B02-004: Chi phí thuế TNDN (8211) tách riêng hiện hành và hoãn lại
B02-005: 82112 = Chi phí thuế TNDN bổ sung (Pillar 2 - Global Minimum Tax)
```

#### Data Requirements

| Account | Description | Model Required | Status |
|---------|-------------|---------------|--------|
| 511 | Revenue from sales | `Account` | ✅ |
| 515 | Financial revenue | `Account` | ✅ |
| 521 | Revenue deductions | `Account` | ✅ |
| 632 | COGS | `InventoryItem` | ✅ |
| 635 | Financial expenses | `Account` | ✅ |
| 641 | Selling expenses | `CostCenter` | ❌ |
| 642 | Admin expenses | `CostCenter` | ❌ |
| 711 | Other income | `Account` | ✅ |
| 811 | Other expenses | `Account` | ✅ |
| 82111 | Current CIT | `TaxPolicy` | ✅ |
| **82112** | Pillar 2 CIT | `TaxPolicy` | ✅ |
| 243 | Deferred tax asset | `Account` | ✅ |
| 347 | Deferred tax liability | `Account` | ✅ |

#### Missing Models for B02

| Model | File | Description | Priority |
|-------|------|-------------|----------|
| `CostCenter` | `models/cost_center.py` | Expense allocation (641, 642) | **HIGH** |
| `Project` | `models/project.py` | Revenue/expense by project | **MEDIUM** |

---

### B03 - Lưu chuyển tiền tệ (Cash Flow Statement)

**Method:** Indirect Method (Phương pháp gián tiếp)

#### Structure (per TT99)

```
I. LƯU CHUYỂN TIỀN TỪ HOẠT ĐỘNG KINH DOANH
   1. Lợi nhuận trước thuế
   2. Điều chỉnh cho:
      - Khấu hao TSCĐ (211, 212, 213)
      - Các khoản dự phòng
      - Chênh lệch tỷ giá chưa thực hiện (TK 413)
      - Lãi/lỗ từ hoạt động đầu tư
      - Chi phí lãi vay
   3. Lợi nhuận từ HĐKD trước thay đổi vốn lưu động
   4. Thay đổi các khoản vốn lưu động:
      - Tăng/giảm các khoản phải thu
      - Tăng/giảm hàng tồn kho
      - Tăng/giảm các khoản phải trả
      - Tăng/giảm chi phí trả trước
   **Tiền từ HĐKD = 1 + 2 + 3 + 4**

II. LƯU CHUYỂN TIỀN TỪ HOẠT ĐỘNG ĐẦU TƯ
   1. Mua sắm TSCĐ, BĐSĐT
   2. Tiền bán TSCĐ, BĐSĐT
   3. Cho vay, mua công cụ nợ
   4. Thu hồi cho vay, bán công cụ nợ
   **Tiền từ HĐT = 1 - 2 + 3 - 4**

III. LƯU CHUYỂN TIỀN TỪ HOẠT ĐỘNG TÀI CHÍNH
   1. Tiền vay gốc
   2. Trả tiền vay gốc
   3. Cổ tức, lợi nhuận đã trả
   **Tiền từ HĐTC = 1 - 2 - 3**

**Tiền đầu kỳ + Tiền trong kỳ = Tiền cuối kỳ**
```

#### Validation Rules

```
B03-001: Sử dụng phương pháp gián tiếp (Indirect Method)
B03-002: Tiền tồn đầu kỳ + Lưu chuyển trong kỳ = Tiền tồn cuối kỳ
B03-003: Lưu chuyển từ HĐKD = Lợi nhuận + Điều chỉnh các khoản phi tiền tệ
B03-004: TK 413 (Chênh lệch tỷ giá) phải phản ánh vào lưu chuyển tiền tệ
```

#### Current Implementation Issues

| Issue | Description | Fix Required |
|-------|-------------|--------------|
| Opening Cash | Currently hardcoded to 0 | Need to track opening balances |
| 211-214 Depreciation | Not calculated | Need `FixedAsset` depreciation |
| TK 413 | FX differences | Need `ExchangeRate` & `UnrealizedExchangeDiff` |
| 215 Biological | Not tracked | Need `BiologicalAsset` model |

#### Missing Models for B03

| Model | File | Description | Priority |
|-------|------|-------------|----------|
| `OpeningBalance` | `models/opening_balance.py` | Track opening cash/balances | **HIGH** |
| `BiologicalAsset` | `models/biological_asset.py` | TK 215 changes affect cash | **MEDIUM** |
| `DepreciationDetail` | `models/fixed_asset.py` | Depreciation in cash flow | **HIGH** |

---

### B05 - Thuyết minh BCTC (Notes to Financial Statements)

#### Required Notes (per TT99)

| Note | Content | Model Required | Status |
|------|---------|---------------|--------|
| 1 | Trình bày BCTC | - | ✅ |
| 2 | Đặc điểm hoạt động | - | - |
| 3 | Chính sách kế toán | - | - |
| 4 | Thông tin bổ sung | - | - |
| 5 | Tiền và tương đương tiền | Cash detail | `BankAccount` | ✅ |
| 6 | Các khoản phải thu | AR aging by customer | `Customer` | ❌ |
| 7 | Hàng tồn kho | Inventory detail | `InventoryItem` | ✅ |
| 8 | Tài sản cố định | FA by category, depreciation | `FixedAsset` | ✅ |
| **9** | **Bất động sản đầu tư** | Investment property | - | ✅ |
| **10** | **Tài sản sinh học** | Biological assets | `BiologicalAsset` | ❌ |
| 11 | Chi phí trả trước | Prepaid expenses | `Account` | ✅ |
| 12 | Tài sản thuế thu nhập hoãn lại | Deferred tax | `Account` | ✅ |
| 13 | Các khoản phải trả | AP detail | `Vendor` | ❌ |
| 14 | Vay và nợ thuê tài chính | Loan detail | `BankAccount` | ✅ |
| 15 | Thuế và các khoản phải nộp | Tax payable | `TaxPolicy` | ✅ |
| 16 | Vốn chủ sở hữu | Equity breakdown | `Account` | ✅ |
| 17 | Doanh thu | Revenue by segment | `Customer`, `Project` | ❌ |
| 18 | Chi phí sản xuất kinh doanh | By nature/function | `CostCenter` | ❌ |
| 19 | Chi phí thuế TNDN | CIT breakdown | `TaxPolicy` | ✅ |
| 20 | Lãi trên cổ phiếu | EPS calculation | - | - |
| 21 | Công cụ tài chính | Financial instruments | - | - |
| 22 | Giao dịch với các bên liên quan | Related party | `Customer`, `Vendor` | ❌ |
| 23 | Tình hình thực hiện nghĩa vụ | Contingencies | - | - |
| 24 | Các khoản nợ tiềm tàng | Guarantees | - | - |
| 25 | Đánh giá tái cơ cấu | Restructuring | - | - |
| 26 | Những sự kiện sau ngày kết thúc | Post-balance events | - | - |
| 27 | Thông tin khác | Other information | - | - |

#### Missing Models for B05

| Model | File | Description | Priority |
|-------|------|-------------|----------|
| `Customer` | `models/customer.py` | AR detail, related party | **HIGH** |
| `Vendor` | `models/vendor.py` | AP detail, related party | **HIGH** |
| `BiologicalAsset` | `models/biological_asset.py` | Note 10 | **MEDIUM** |
| `CostCenter` | `models/cost_center.py` | Note 18 | **HIGH** |
| `Project` | `models/project.py` | Note 17 | **MEDIUM** |

---

## Part 3: Subsidiary Ledgers (Sổ chi tiết)

Per Phụ lục III - Sổ kế toán (42 mẫu)

| Ledger | TK | Model Required | Status |
|--------|----|---------------|--------|
| Sổ chi tiết TK 131 | Phải thu khách hàng | `Customer` | ❌ |
| Sổ chi tiết TK 331 | Phải trả người bán | `Vendor` | ❌ |
| Sổ chi tiết TK 141 | Tạm ứng | `Employee` | ❌ |
| Sổ chi tiết TK 156 | Hàng hóa | `InventoryItem` | ✅ |
| Sổ chi tiết TK 211 | TSCĐ hữu hình | `FixedAsset` | ✅ |
| Sổ chi tiết TK 212 | TSCĐ thuê tài chính | `FixedAsset` | ✅ |
| Sổ chi tiết TK 213 | TSCĐ vô hình | `FixedAsset` | ✅ |

#### Validation Rules

```
SL-001: TK 131: Theo dõi chi tiết theo khách hàng
SL-002: TK 331: Theo dõi chi tiết theo nhà cung cấp
SL-003: TK 156: Theo dõi chi tiết theo vật tư/hàng hóa
SL-004: TK 141: Theo dõi chi tiết theo nhân viên
SL-005: Số dư Sổ chi tiết = Số dư Sổ cái
```

---

## Part 4: Management Reports

### AR Aging Report (Công nợ phải thu)

| Due Status | Days | Model Required |
|------------|------|---------------|
| Chưa đến hạn | 0-30 | `Customer` |
| Đến hạn 1-30 ngày | 31-60 | `Customer` |
| Đến hạn 31-60 ngày | 61-90 | `Customer` |
| Đến hạn 61-90 ngày | 91-180 | `Customer` |
| Quá hạn > 180 ngày | >180 | `Customer` |

### AP Aging Report (Công nợ phải trả)

| Due Status | Days | Model Required |
|------------|------|---------------|
| Chưa đến hạn | 0-30 | `Vendor` |
| Đến hạn 1-30 ngày | 31-60 | `Vendor` |
| Đến hạn 31-60 ngày | 61-90 | `Vendor` |
| Đến hạn 61-90 ngày | 91-180 | `Vendor` |
| Quá hạn > 180 ngày | >180 | `Vendor` |

---

## Part 5: Summary - All Missing Models

### Priority 1: Critical for TT99 Compliance

| Model | Purpose | Reports Affected |
|-------|---------|-----------------|
| `Customer` | AR subledger (TK 131) | B01, B05, AR Aging, SL |
| `Vendor` | AP subledger (TK 331) | B01, B05, AP Aging, SL |
| `Employee` | Advances (TK 141), Payroll (TK 334) | B01, B05, SL |

### Priority 2: Required for Complete Reports

| Model | Purpose | Reports Affected |
|-------|---------|-----------------|
| `CostCenter` | Expense allocation (641, 642) | B02, B05 |
| `Project` | Revenue/expense by project | B02, B05 |
| `OpeningBalance` | Opening cash for B03 | B03 |
| `BiologicalAsset` | TK 215 (NEW in TT99) | B01, B03, B05 |

### Priority 3: Enhanced Features

| Model | Purpose | Reports Affected |
|-------|---------|-----------------|
| `Document` | Supporting documents | All |
| `RelatedParty` | Related party disclosures | B05 |
| `Contingency` | Guarantees/commitments | B05 |
| `DividendPayable` | TK 332 | B01 |

---

## Part 6: Current vs Required Models

### Models Currently in Project

```
✅ Account
✅ JournalVoucher
✅ JournalEntry
✅ AccountingPeriod
✅ AuditLog
✅ TaxPolicy
✅ BankAccount
✅ BankStatement
✅ BankReconciliation
✅ Warehouse
✅ InventoryItem
✅ StockTransaction
✅ InventoryBatch
✅ FixedAsset
✅ FixedAssetCategory
✅ DepreciationEntry
✅ Budget
✅ BudgetDetail
✅ BudgetActual
✅ Currency
✅ ExchangeRate
✅ ForeignCurrencyTransaction
✅ UnrealizedExchangeDiff
✅ User, Role, Permission
```

### Models Missing

```
❌ Customer (TK 131 subledger)
❌ Vendor (TK 331 subledger)
❌ Employee (TK 141, 334)
❌ CostCenter (641, 642 allocation)
❌ Project (revenue/expense by project)
❌ OpeningBalance (B03 opening cash)
❌ BiologicalAsset (TK 215 - NEW)
❌ Document (supporting documents)
❌ RelatedParty (B05 disclosure)
❌ Contingency (B05 note 23-24)
❌ ApprovalWorkflow (Điều 3)
❌ ApprovalRequest (Điều 3)
❌ ApprovalStep (Điều 3)
❌ Notification
❌ SystemSettings
```

---

## Part 7: Implementation Priority

### Phase 1: Core Subledgers (Week 1-2)

```
1. Customer Model
   - Fields: code, name, tax_code, address, contact
   - Relationships: journal_entries (via customer_id)
   - Reports: B01, B05, AR Aging, SL-131

2. Vendor Model
   - Fields: code, name, tax_code, address, contact
   - Relationships: journal_entries (via vendor_id)
   - Reports: B01, B05, AP Aging, SL-331

3. Employee Model
   - Fields: code, name, department, position
   - Relationships: journal_entries (via employee_id)
   - Reports: B01, B05, SL-141
```

### Phase 2: Cost Allocation (Week 3)

```
4. CostCenter Model
   - Fields: code, name, parent_id, manager
   - Relationships: journal_entries (via cost_center)
   - Reports: B02, B05

5. Project Model
   - Fields: code, name, customer_id, status
   - Relationships: journal_entries
   - Reports: B02, B05
```

### Phase 3: Opening Balances (Week 4)

```
6. OpeningBalance Model
   - Fields: account_id, amount, as_of_date
   - Relationships: account
   - Reports: B03
```

### Phase 4: Biological Assets (Week 5)

```
7. BiologicalAsset Model (NEW in TT99)
   - Fields: code, name, type, purchase_date, quantity
   - Fields: fair_value, accumulated_changes
   - Relationships: fixed_asset_category
   - Reports: B01, B03, B05
```

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-03-19 | System | Initial analysis |

---

**Document Status:** Draft  
**Next Review:** Before Phase 1 implementation
