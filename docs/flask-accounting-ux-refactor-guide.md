# Flask Accounting UX Refactor Guide

**Version:** 1.0  
**Based on:** prompt-foundation-ui-ux-accounting.md  
**Last Updated:** 2026-03-19

---

## 1. Design Principles Summary

| # | Principle | Key Actions |
|---|----------|-------------|
| 1 | Data Clarity First | Table hierarchy, right-align numbers, tabular fonts |
| 2 | Input Efficiency | Keyboard-first, Tab navigation, autocomplete |
| 3 | Trust & Precision | Conservative colors (blue/gray), strict validation |
| 4 | Error Prevention > Error Handling | Disable invalid actions, auto-balance |
| 5 | Consistency Over Creativity | Reuse components, standardized tables/forms |
| 6 | Printability First-Class | A4-ready layouts, VAS-compliant prints |

---

## 2. Color System

### 2.1 Semantic Colors

| Meaning | Color | Usage |
|---------|-------|-------|
| Credit / Positive | `#16a34a` (green) | Dương, Tốt |
| Debit / Negative | `#dc2626` (red) | Âm, Xấu |
| Warning | `#f59e0b` (amber) | Cảnh báo |
| Error | `#ef4444` | Lỗi |
| Success | `#22c55e` | Thành công |
| Pending | `#3b82f6` (blue) | Chờ duyệt |
| Locked | `#7c3aed` (purple) | Đã khóa |
| Zero | `#9ca3af` (gray) | Số 0 |

### 2.2 Table Colors

| Element | Color |
|---------|-------|
| Header | `#f5f7fa` |
| Row | `#ffffff` |
| Hover | `#f0f5ff` |
| Selected | `#e6f4ff` |
| Striped | `#fafafa` |
| Total row | `#fff7ed` |
| Grand total | `#ffedd5` |
| Section header | `#f1f5f9` |

---

## 3. Typography

### 3.1 Font Stack

```scss
--font-sans: 'Inter', ui-sans-serif, system-ui, sans-serif;
--font-mono: 'Roboto Mono', ui-monospace, monospace;
```

### 3.2 Type Scale

| Element | Size | Weight |
|---------|------|--------|
| H1 (Page title) | 24px | 600 |
| H2 (Section) | 20px | 600 |
| H3 (Sub) | 18px | 500 |
| Body | 14px | 400 |
| Small/Meta | 12px | 400 |
| Table | 13px | 400 |
| Number/Amount | 13px | 500 |

### 3.3 Number Formatting (VAS Style)

```
VNĐ: 1.234.567 đ
Negative: (1.234.567) ✅
Zero: -
Decimal: 2 digits
Align: RIGHT
```

---

## 4. Component Standards

### 4.1 Data Table

**Column Widths:**
| Column | Width | Alignment |
|--------|-------|-----------|
| STT | 60px | center |
| Code | 140px | left, clickable |
| Date | 120px | center |
| Name | min 200px | left |
| Account | 120px | left, monospace |
| Amount | 160px | right |

**Features:**
- Fixed header on scroll
- Hover highlight
- Row selection
- Pagination: 20/50/100/200

**Toolbar:**
- Search: left
- Actions: right

### 4.2 Forms

- Label: top position
- Required: `*` red
- Validation: inline error
- Money input: auto-format with `.` separator
- Account input: autocomplete dropdown

### 4.3 Journal Entry Table (Special)

- Editable rows
- Auto-balance check
- Highlight mismatch (red border)

### 4.4 Buttons

| Type | Color | Size |
|------|-------|------|
| Primary | Blue `#2f54eb` | 32px default |
| Secondary | Gray | 32px |
| Danger | Red | 32px |
| Large | - | 40px |
| Small | - | 24px |

### 4.5 Status Badges

| Status | Color | Background |
|--------|-------|------------|
| Nháp | gray | `#f5f5f5` |
| Chờ duyệt | blue | `#d6e4ff` |
| Đã duyệt | green | `#d1fae5` |
| Hạch toán | teal | `#ccfbf1` |
| Quá hạn | orange | `#ffedd5` |
| Hủy | red | `#fee2e2` |
| Khóa | purple | `#ede9fe` |

---

## 5. Voucher Status Flow

```
Nháp → Chờ duyệt → Đã duyệt → Hạch toán
   ↓         ↓           ↓          ↓
  Hủy    Quá hạn      Hủy       Khóa
```

---

## 6. Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+S` | Save |
| `Ctrl+N` | New voucher |
| `Ctrl+P` | Print |
| `Ctrl+K` | Global search |
| `1` | Quick: New voucher |
| `2` | Quick: Trial balance |
| `3` | Quick: Journal |
| `Tab` | Next field |
| `Shift+Tab` | Previous field |
| `Enter` | Submit/Confirm |
| `Esc` | Cancel/Close modal |

---

## 7. Auto-save

- Draft auto-save: every 30 seconds
- Visual indicator: "Đã lưu nháp lúc HH:mm"

---

## 8. Layout Dimensions

| Element | Value |
|---------|-------|
| Topbar height | 56px |
| Sidebar width (expanded) | 240px |
| Sidebar width (collapsed) | 80px |
| Content padding | 24px |
| Card padding | 16px |
| Table cell padding | 12px 16px |

---

## 9. Print Requirements (VAS Standard)

- Paper: A4
- Margin: 2cm
- Font: Times New Roman
- Size: 11pt
- Header: Company name, report title, date
- Footer: Page number

---

## 10. Screen Priority

### P1 - MVP (Implement First)

1. Dashboard
2. Chart of Accounts
3. Journal Entries (voucher form)
4. General Ledger
5. Trial Balance
6. Balance Sheet
7. Income Statement

### P2

8. Inventory
9. AR/AP Aging
10. Bank Reconciliation

### P3

11. Fixed Assets
12. Tax Reports

---

## 11. Implementation Checklist

- [x] Global Layout (header, sidebar, search)
- [ ] _variables.scss: Update color system
- [ ] _components.scss: Data table styles
- [ ] _components.scss: Form styles
- [ ] _components.scss: Button styles
- [ ] _components.scss: Status badges
- [ ] voucher_form.html: Journal entry table UX
- [ ] accounts.html: Data table UX
- [ ] ledger.html: Print-friendly
- [ ] financial reports: VAS print format
- [ ] Keyboard shortcuts JS

---

## 12. File Structure

```
assets/scss/
├── _variables.scss      # Design tokens (colors, fonts, spacing)
├── _base.scss           # Reset, HTML/body
├── _layout.scss         # Header, sidebar, navigation
├── _components.scss     # Table, form, button, badge styles (NEW)
└── app.scss             # Main entry point
```

---

## 13. References

- Design source: `prompt-foundation-ui-ux-accounting.md`
- Implemented in: `base.html`, `_layout.scss`
- Next steps: Component-level refactors
