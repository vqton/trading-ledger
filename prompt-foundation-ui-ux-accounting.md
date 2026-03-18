---

# 🏗️ DESIGN SYSTEM FOUNDATION — ACCOUNTING WEBAPP (VAS)

---

# SECTION 1 — DESIGN PRINCIPLES

## 1. Data Clarity First

* **Mô tả:** Dữ liệu tài chính phải rõ ràng, dễ đọc, không gây nhầm lẫn.
* **Áp dụng:** Table có phân cấp rõ, số liệu căn phải, font tabular.
* **Anti-pattern:** Màu mè, icon thừa, typography không đồng nhất.

---

## 2. Input Efficiency

* **Mô tả:** Tối ưu tốc độ nhập liệu (giống Excel/MISA).
* **Áp dụng:** Keyboard-first, tab navigation, autocomplete.
* **Anti-pattern:** Click nhiều, form dài không grouping.

---

## 3. Trust & Precision

* **Mô tả:** UI phải tạo cảm giác chính xác và đáng tin cậy.
* **Áp dụng:** màu conservative (blue/gray), validation chặt.
* **Anti-pattern:** màu flashy, animation dư thừa.

---

## 4. Error Prevention > Error Handling

* **Mô tả:** Ngăn lỗi trước khi xảy ra.
* **Áp dụng:** disable invalid actions, auto-balance.
* **Anti-pattern:** cho phép nhập sai rồi báo lỗi sau.

---

## 5. Consistency Over Creativity

* **Mô tả:** Mọi screen phải giống nhau về pattern.
* **Áp dụng:** reuse component, table/form chuẩn hóa.
* **Anti-pattern:** mỗi screen một kiểu UI.

---

## 6. Printability First-Class

* **Mô tả:** UI phải chuyển sang PDF chuẩn Bộ Tài chính.
* **Áp dụng:** layout A4-ready.
* **Anti-pattern:** UI chỉ đẹp trên web, không in được.

---

# SECTION 2 — COLOR SYSTEM

## 2.1 Brand Palette

Primary (Finance Blue):

* 50: #f0f5ff
* 100: #d6e4ff
* 200: #adc8ff
* 300: #85a5ff
* 400: #597ef7
* 500: #2f54eb
* 600: #1d39c4
* 700: #10239e
* 800: #061178
* 900: #030852

Accent:

* #13c2c2 (teal)

Neutral:

* 50: #fafafa
* 100: #f5f5f5
* 200: #e5e5e5
* 300: #d4d4d4
* 400: #a3a3a3
* 500: #737373
* 600: #525252
* 700: #404040
* 800: #262626
* 900: #171717

---

## 2.2 Semantic Colors

* Credit / Positive: #16a34a
* Debit / Negative: #dc2626
* Zero: #9ca3af
* Warning: #f59e0b
* Error: #ef4444
* Success: #22c55e
* Pending: #3b82f6
* Locked: #7c3aed

---

## 2.3 Table Colors

* Header: #f5f7fa
* Row: #ffffff
* Hover: #f0f5ff
* Selected: #e6f4ff
* Striped: #fafafa
* Total row: #fff7ed
* Grand total: #ffedd5
* Section header: #f1f5f9

---

## 2.4 Background

* Page: #f5f7fb
* Card: #ffffff
* Sidebar: #001529 (antd default)
* Modal overlay: rgba(0,0,0,0.45)

---

# SECTION 3 — TYPOGRAPHY

## 3.1 Fonts

* Heading: Inter
* Body: Inter
* Numeric: Roboto Mono

👉 Lý do:

* Inter hỗ trợ tiếng Việt tốt
* Roboto Mono giúp align số

---

## 3.2 Type Scale

| Type   | Size | Weight | Usage      |
| ------ | ---- | ------ | ---------- |
| H1     | 24px | 600    | Page title |
| H2     | 20px | 600    | Section    |
| H3     | 18px | 500    | Sub        |
| Body   | 14px | 400    | Default    |
| Small  | 12px | 400    | Meta       |
| Table  | 13px | 400    | Table      |
| Number | 13px | 500    | Amount     |

---

## 3.3 Number Rules

* VNĐ: `1.234.567 đ`
* USD: `1,234,567.89 USD`
* Negative: `(1.234.567)` ✅ VAS style
* Zero: `-`
* Decimal: 2 digits
* Align: right

---

## 3.4 Vietnamese Rules

* Line height: ≥ 1.5
* Không dùng uppercase toàn bộ
* Truncate + tooltip

---

# SECTION 4 — SPACING & LAYOUT

## 4.1 Spacing

Base: 4px

Use:

* 8px: tight spacing
* 16px: default
* 24px: section
* 32px+: page

---

## 4.2 Layout

Topbar:

* height: 56px

Sidebar:

* 240px expanded
* 80px collapsed

Content:

* padding: 24px

---

## 4.3 Layout Patterns

### Table Screen

* Toolbar + Table + Pagination

### Form

* Sections + Footer actions

### Dashboard

* Cards grid

### Report

* Filter + Table (printable)

---

# SECTION 5 — COMPONENTS

## 5.1 Data Table

Columns:

* STT: 60px center
* Code: 140px clickable
* Date: 120px center
* Name: min 200px
* Account: 120px monospace
* Amount: 160px right-align

Features:

* fixed header
* column resize
* row select
* expandable rows
* pagination: 20/50/100/200

Toolbar:

* search left
* actions right

---

## 5.2 Forms

* Label top
* Required: red *
* Validation: inline

Special:

* Money input: auto format
* Account input: autocomplete

---

## Journal Table

* editable rows
* auto balance check
* highlight mismatch

---

## 5.3 Buttons

Primary: blue
Secondary: gray
Danger: red

Sizes:

* large: 40px
* default: 32px
* small: 24px

---

## 5.4 Status

| Status    | Color  |
| --------- | ------ |
| Nháp      | gray   |
| Chờ duyệt | blue   |
| Đã duyệt  | green  |
| Hạch toán | teal   |
| Quá hạn   | orange |
| Hủy       | red    |
| Khóa      | purple |

---

## 5.5 Modal

* sm: 480px
* md: 720px
* lg: 960px

---

## 5.6 Feedback

* Success: toast 3s
* Error: persistent
* Loading: skeleton

---

# SECTION 6 — NAVIGATION

(Sử dụng đúng structure bạn đưa — giữ nguyên)

Sidebar chuẩn ERP.

---

## Kỳ kế toán

* topbar
* always visible
* format: Tháng 03/2026
* locked → banner warning

---

# SECTION 7 — PRINT

* A4
* margin: 2cm
* font: Times New Roman
* size: 11pt

---

# SECTION 8 — INTERACTION

Shortcuts:

* Ctrl+S
* Ctrl+N
* Ctrl+P

---

Auto-save:

* draft every 30s

---

# SECTION 9 — RESPONSIVE

≥1440px primary

<1024px → warning

---

# SECTION 10 — TOKENS

```json
{
  "colors": {
    "primary": "#2f54eb",
    "success": "#22c55e",
    "error": "#ef4444"
  },
  "spacing": {
    "base": 4,
    "md": 16,
    "lg": 24
  },
  "radius": {
    "sm": 4,
    "md": 8
  }
}
```

---

# SECTION 11 — SCREEN INVENTORY

## P1 (MVP)

* Dashboard
* Chart of Accounts
* Journal Entries
* General Ledger
* Trial Balance
* Balance Sheet
* Income Statement

## P2

* Inventory
* AR/AP
* Bank

## P3

* Fixed Assets
* Tax

---

# ✅ KẾT LUẬN

Design này:

✔ Chuẩn ERP
✔ Chuẩn VAS
✔ Dev React + antd dùng được ngay
✔ Tối ưu cho kế toán VN

---
