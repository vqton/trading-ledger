# VAS Accounting WebApp - Business Rules Specification

**Version:** 1.0  
**Circular:** 99/2025/TT-BTC  
**Last Updated:** 2026-03-19

---

## Mục lục

1. [Document Engine Rules](#1-document-engine-rules)
2. [Financial Report Engine Rules](#2-financial-report-engine-rules)
3. [Internal Control Engine Rules](#3-internal-control-engine-rules)
4. [Currency Engine Rules](#4-currency-engine-rules)
5. [Ledger Engine Rules](#5-ledger-engine-rules)
6. [Tax Engine Rules](#6-tax-engine-rules)
7. [Audit Trail Engine Rules](#7-audit-trail-engine-rules)
8. [Global Business Rules](#8-global-business-rules)

---

## 1. Document Engine Rules

**Reference:** Phụ lục I - Biểu mẫu chứng từ kế toán (33 biểu mẫu)

### 1.1 Document Types

| Mã | Tên | Số dòng tối thiểu |
|----|-----|-------------------|
| PT | Phiếu thu | 2 |
| PC | Phiếu chi | 2 |
| PXK | Phiếu xuất kho | 2 |
| PNK | Phiếu nhập kho | 2 |
| HD | Hóa đơn | 3 |
| BB | Biên bản | 2 |
| GBN | Giấy báo Nợ | 1 |
| GBC | Giấy báo Có | 1 |

### 1.2 Document Validation Rules

```
DOC-001: Mọi chứng từ phải có số chứng từ duy nhất
DOC-002: Số chứng từ phải theo format: [Mã loại]-[YYYYMMDD]-[NNN]
DOC-003: Ngày chứng từ không được lớn hơn ngày hiện tại
DOC-004: Ngày chứng từ không được quá 30 ngày trong quá khứ
DOC-005: Mỗi chứng từ phải có ít nhất 2 dòng hạch toán
DOC-006: Tổng Nợ phải bằng Tổng Có
DOC-007: Diễn giải không được để trống
DOC-008: Số tiền phải > 0
```

### 1.3 Document Numbering Rules

```python
# Format: [PREFIX]-[YYYY]-[MM]-[NNNN]
# Examples:
# PT-2026-03-0001
# PC-2026-03-0001
# PXK-2026-03-0001

rules:
  prefix: 2-3 ký tự (theo loại chứng từ)
  year: 4 số (YYYY)
  month: 2 số (MM)
  sequence: 4 số (NNNN) - reset theo tháng
```

### 1.4 Required Fields by Document Type

```yaml
PT:
  required:
    - voucher_date
    - description
    - total_amount
    - payment_method
    - cash_account
  optional:
    - customer_id
    - reference
    - attachments

PC:
  required:
    - voucher_date
    - description
    - total_amount
    - payment_method
    - cash_account
  optional:
    - vendor_id
    - reference
    - attachments

PXK:
  required:
    - voucher_date
    - warehouse_id
    - inventory_items
    - total_amount
  optional:
    - customer_id
    - reference
    - reason

PNK:
  required:
    - voucher_date
    - warehouse_id
    - inventory_items
    - total_amount
  optional:
    - vendor_id
    - reference
    - reason
```

---

## 2. Financial Report Engine Rules

**Reference:** Phụ lục IV - Biểu mẫu báo cáo tài chính

### 2.1 Report Types

| Mã | Tên | Bắt buộc |
|----|-----|-----------|
| B01 | Báo cáo tình hình tài chính | ✅ |
| B02 | Kết quả hoạt động kinh doanh | ✅ |
| B03 | Lưu chuyển tiền tệ | ✅ |
| B05 | Thuyết minh BCTC | ✅ |

### 2.2 B01 - Báo cáo tình hình tài chính

```
B01-001: Đổi tên từ "Bảng cân đối kế toán" → "Báo cáo tình hình tài chính"
B01-002: Tài sản ngắn hạn = Tài sản có chu kỳ ≤ 12 tháng
B01-003: Tài sản dài hạn = Tài sản có chu kỳ > 12 tháng
B01-004: Nợ phải trả ngắn hạn = Nợ có thời hạn ≤ 12 tháng
B01-005: Nợ phải trả dài hạn = Nợ có thời hạn > 12 tháng
B01-006: Tổng Tài sản = Tổng Nguồn vốn (BẮT BUỘC)
B01-007: Sắp xếp theo tính thanh khoản giảm dần
```

### 2.3 B02 - Kết quả hoạt động kinh doanh

```
B02-001: Doanh thu thuần = Doanh thu - Các khoản giảm trừ
B02-002: Lợi nhuận gộp = Doanh thu thuần - Giá vốn
B02-003: Lợi nhuận thuần = Lợi nhuận gộp - Chi phí - Thuế
B02-004: Chi phí thuế TNDN (8211) tách riêng hiện hành và hoãn lại
B02-005: 82112 = Chi phí thuế TNDN bổ sung (thuế tối thiểu toàn cầu)
```

### 2.4 B03 - Lưu chuyển tiền tệ (Phương pháp gián tiếp)

```
B03-001: Sử dụng phương pháp gián tiếp (Indirect Method)
B03-002: Tiền tồn đầu kỳ + Lưu chuyển trong kỳ = Tiền tồn cuối kỳ
B03-003: Lưu chuyển từ HĐKD = Lợi nhuận + Điều chỉnh các khoản phi tiền tệ
B03-004: TK 413 (Chênh lệch tỷ giá) phản ánh vào lưu chuyển tiền tệ
```

### 2.5 Account Mapping for Reports

```yaml
# ASSETS (Tài sản)
Mã 100: Tài sản ngắn hạn
  Mã 110: Tiền và tương đương tiền
    TK 111, 112, 113
  Mã 120: Các khoản phải thu ngắn hạn
    TK 131, 136, 138
  Mã 150: Hàng tồn kho
    TK 151-158

Mã 200: Tài sản dài hạn
  Mã 210: Tài sản cố định
    TK 211, 212, 213, 214
  Mã 220: Bất động sản đầu tư
    TK 217
  Mã 240: Đầu tư tài chính dài hạn
    TK 221, 222, 228

# LIABILITIES (Nợ phải trả)
Mã 300: Nợ phải trả
  Mã 310: Nợ ngắn hạn
    TK 331, 333, 334, 335, 336, 337, 338
  Mã 330: Nợ dài hạn
    TK 341, 343, 347

# EQUITY (Vốn chủ sở hữu)
Mã 400: Vốn chủ sở hữu
  Mã 410: Vốn góp
    TK 411, 414, 418
  Mã 420: Lợi nhuận
    TK 421, 4211, 4212
```

---

## 3. Internal Control Engine Rules

**Reference:** Điều 3 - Quản trị và kiểm soát nội bộ

### 3.1 Authorization Rules

```
IC-001: Người tạo ≠ Người duyệt
IC-002: Người tạo ≠ Người ghi sổ
IC-003: Người ghi sổ ≠ Người đối chiếu
IC-004: Cấp cao nhất duyệt tối đa 1 tỷ VNĐ
IC-005: Giao dịch > 500 triệu cần 2 người ký
```

### 3.2 Segregation of Duties Matrix

| Role | Create | Approve | Record | Custody | Reconcile |
|------|--------|---------|--------|---------|-----------|
| Admin | ✅ | ✅ | ✅ | ✅ | ✅ |
| Accountant | ✅ | ❌ | ✅ | ❌ | ✅ |
| Auditor | ❌ | ❌ | ❌ | ❌ | ✅ |
| Viewer | ❌ | ❌ | ❌ | ❌ | ❌ |

### 3.3 Approval Limits

```yaml
approval_limits:
  manager:
    amount: 50_000_000  # 50 triệu
    require_approval: false
  
  director:
    amount: 500_000_000  # 500 triệu
    require_approval: true
  
  ceo:
    amount: null  # Không giới hạn
    require_approval: false
```

### 3.4 Control Activities

```
IC-010: Đối chiếu ngân hàng hàng tháng
IC-011: Đối chiếu công nợ hàng quý
IC-012: Kiểm kê tài sản cuối năm
IC-013: Backup dữ liệu hàng ngày
IC-014: Review chứng từ trước khi ghi sổ
```

---

## 4. Currency Engine Rules

**Reference:** Điều 5, 6 - Đơn vị tiền tệ kế toán

### 4.1 Currency Rules

```
CUR-001: Đơn vị tiền tệ hạch toán mặc định = VND
CUR-002: Đơn vị tiền tệ BCTC = VND
CUR-003: Tỷ giá ghi sổ = Tỷ giá thực tế tại ngày giao dịch
CUR-004: Tỷ giá cuối kỳ = Tỷ giá trung bình thị trường
```

### 4.2 Foreign Currency Transaction Rules

```python
# Khi ghi nhận tăng TSCĐ:
debit: amount_usd × exchange_rate_actual
credit: amount_usd × exchange_rate_actual

# Khi đánh giá lại cuối kỳ:
debit/credit: amount_usd × (rate_closing - rate_booking)

# Chênh lệch → TK 413
```

### 4.3 Exchange Rate Sources

```
CUR-010: Ưu tiên tỷ giá của Ngân hàng TMCP Ngoại thương (VCB)
CUR-011: Tỷ giá bình quân thị trường liên ngân hàng
CUR-012: Cập nhật tỷ giá hàng ngày
```

---

## 5. Ledger Engine Rules

**Reference:** Phụ lục III - Sổ kế toán (42 mẫu)

### 5.1 Ledger Types

| Mã | Tên | Bắt buộc |
|----|-----|-----------|
| S01 | Nhật ký chung | ✅ |
| S02 | Nhật ký đặc biệt | ❌ |
| S03-S12 | Sổ cái TK | ✅ |
| S21-S24 | Bảng tổng hợp | ✅ |
| S31-S33 | Sổ quỹ | ✅ |

### 5.2 Ledger Entry Rules

```
LED-001: Mỗi chứng từ phải có ít nhất 2 dòng
LED-002: Tổng Nợ = Tổng Có
LED-003: Số dư cuối = Số dư đầu + Phát sinh Nợ - Phát sinh Có
LED-004: Chỉ ghi nhận chứng từ đã duyệt (posted)
LED-005: Không được sửa/xóa chứng từ đã ghi sổ
```

### 5.3 Trial Balance Rules

```
TB-001: Tổng Nợ = Tổng Có (số dư)
TB-002: Tổng PS Nợ = Tổng PS Có
TB-003: Hiển thị số dư đầu, phát sinh, số dư cuối
TB-004: Sắp xếp theo mã TK
```

### 5.4 Subsidiary Ledger Rules

```
SL-001: TK 131: Theo dõi chi tiết theo khách hàng
SL-002: TK 331: Theo dõi chi tiết theo nhà cung cấp
SL-003: TK 156: Theo dõi chi tiết theo vật tư/hàng hóa
SL-004: TK 141: Theo dõi chi tiết theo nhân viên
SL-005: Số dư Sổ chi tiết = Số dư Sổ cái
```

---

## 6. Tax Engine Rules

**Reference:** TK 333 - Thuế và các khoản phải nộp Nhà nước

### 6.1 Tax Account Structure

```yaml
TK_333:
  3331:
    name: Thuế GTGT phải nội
    types:
      - 33311: Thuế GTGT đầu ra
      - 33312: Thuế GTGT hàng nhập khẩu
  
  3332: Thuế tiêu thụ đặc biệt
  3333: Thuế xuất nhập khẩu
  3334: Thuế TNDN
  3335: Thuế TNCN
  3336: Thuế tài nguyên
  3337: Thuế nhà đất, tiền thuê đất
  3338: Thuế BVMT
  33381: Thuế bảo vệ môi trường
  3339: Phí, lệ phí
```

### 6.2 VAT Rules

```
VAT-001: Thuế suất 0%, 5%, 8%, 10% (phương pháp khấu trừ)
VAT-002: Khấu trừ thuế đầu vào khi có hóa đơn hợp lệ
VAT-003: Kê khai thuế theo tháng/quý
VAT-004: Hóa đơn đầu vào phải đúng mẫu, có MST
```

### 6.3 Corporate Income Tax Rules

```
CIT-001: Thuế suất 20% (doanh nghiệp thường)
CIT-002: Thuế suất 15-17% (DN ưu đãi)
CIT-003: 82112 = Thuế TNDN bổ sung (thuế tối thiểu toàn cầu - Pillar 2)
CIT-004: Tạm tính hàng quý, quyết toán cuối năm
```

---

## 7. Audit Trail Engine Rules

### 7.1 Audit Events

```yaml
audit_events:
  CREATE:
    - user_created
    - entity_created
    - initial_values
  
  UPDATE:
    - user_modified
    - entity_modified
    - old_values
    - new_values
  
  DELETE:
    - user_deleted
    - entity_deleted
    - old_values
  
  POST:
    - user_who_posted
    - timestamp
    - ip_address
  
  UNPOST:
    - user_who_unposted
    - reason
    - timestamp
```

### 7.2 Retention Period

```
AUD-001: Lưu trữ audit log tối thiểu 10 năm
AUD-002: Backup audit log hàng tháng
AUD-003: Audit log không được sửa/xóa
AUD-004: IP address phải ghi nhận đầy đủ
```

### 7.3 Compliance Checks

```
AUD-010: Mọi giao dịch phải có audit trail
AUD-011: User login/logout phải ghi nhận
AUD-012: Thay đổi quyền user phải ghi nhận
AUD-013: Đối soát audit log hàng tháng
```

---

## 8. Global Business Rules

### 8.1 Double-Entry Accounting

```
GL-001: Mọi nghiệp vụ phải có ít nhất 2 dòng
GL-002: Tổng Nợ = Tổng Có (BẮT BUỘC)
GL-003: Mỗi dòng phải có account_id hợp lệ
GL-004: Amount phải > 0
```

### 8.2 Account Type Rules

| Type | Normal Balance | Increases With | Decreases With |
|------|---------------|---------------|---------------|
| Asset | Debit | Debit | Credit |
| Liability | Credit | Credit | Debit |
| Equity | Credit | Credit | Debit |
| Revenue | Credit | Credit | Debit |
| Expense | Debit | Debit | Credit |

### 8.3 Posting Rules

```
POST-001: Chỉ tài khoản is_postable=True mới được ghi sổ
POST-002: Chứng từ phải ở trạng thái DRAFT mới được sửa
POST-003: Chứng từ POSTED không được sửa, chỉ điều chỉnh bằng chứng từ mới
POST-004: Chứng từ LOCKED không được thay đổi
```

### 8.4 Period Rules

```
PER-001: Kỳ kế toán mặc định = Tháng
PER-002: Ngày bắt đầu = Ngày 01
PER-003: Ngày kết thúc = Ngày cuối tháng
PER-004: Số dư đầu kỳ = Số dư cuối kỳ trước
PER-005: Không cho phép sửa kỳ đã đóng
```

### 8.5 Number Formatting

```python
# Tiền VND
format_currency(value, currency="VND"):
  # 1,000,000 → "1.000.000 đ"

# Số chứng từ
format_voucher_no(prefix, date, sequence):
  # PT-2026-03-0001

# Ngày tháng
format_date(date, format="dd/MM/yyyy"):
  # 2026-03-19 → "19/03/2026"
```

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-03-19 | System | Initial specification |

---

**Document Status:** Draft  
**Next Review:** Before implementation of each engine
