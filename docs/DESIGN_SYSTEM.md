# VAS Accounting Design System v1

## Typography

| Role | Font | Weight | Size |
|------|------|--------|------|
| Body text | Inter | 400 | 14px |
| Labels / headings | Inter | 600 | 13–18px |
| Money / numbers | JetBrains Mono | 400/500 | 13px |
| Account codes | JetBrains Mono | 400 | 13px |
| Table headers | Inter | 600 | 11px uppercase |

Base font size is **14px** (not 16px) for compact data density.

## Color Palette

### Bootstrap Semantic Mapping

| Token | Hex | Usage |
|-------|-----|-------|
| `--bs-primary` | `#2563eb` | Buttons, links, active states |
| `--success-500` | `#22c55e` | Paid, positive amounts, approved |
| `--danger-500` | `#ef4444` | Overdue, negative amounts, errors |
| `--warning-500` | `#f59e0b` | Pending, warnings, draft review |
| `--info-500` | `#3b82f6` | Pending status, info alerts |
| `--bg-page` | `#f8fafc` | Page background (NOT pure white) |
| `--bg-card` | `#ffffff` | Cards, tables, forms |
| `--neutral-800` | `#1e293b` | Primary text |
| `--neutral-500` | `#64748b` | Muted text, placeholders |

### Accounting Semantic Colors

| Token | Hex | Meaning |
|-------|-----|---------|
| `--positive` | `#16a34a` | Credit balances, net profit |
| `--negative` | `#dc2626` | Debit deficit, net loss |
| `--zero` | `#94a3b8` | Zero balance |
| `--pending` | `#3b82f6` | Awaiting action |
| `--locked` | `#7c3aed` | Locked periods |

## Spacing & Density

- **Compact mode** default: tables use 6px/12px padding
- Form inputs: **38px height** (clickable, not fat)
- Card padding: 12–16px
- Section gaps: 16–24px

## Icon Standards (Font Awesome 6)

| Action | Icon | Hover Color |
|--------|------|-------------|
| View | `fa-eye` | primary |
| Edit | `fa-pen-to-square` | primary |
| Delete | `fa-trash` | danger |
| Print | `fa-print` | primary |
| Export Excel | `fa-file-excel` | success |
| Export PDF | `fa-file-pdf` | danger |
| Add / Create | `fa-plus` | — |
| Search | `fa-search` | — |
| Filter | `fa-filter` | — |
| Download | `fa-download` | primary |
| Upload | `fa-upload` | primary |
| Approve | `fa-check` | success |
| Reject | `fa-xmark` | danger |
| Login | `fa-sign-in-alt` | — |
| Logout | `fa-sign-out-alt` | — |
| Settings | `fa-cog` | — |
| Dashboard | `fa-home` | — |

**Usage:** Always pair icon with action text or use `title=""` for accessibility.

```html
<!-- Button with icon + text (preferred) -->
<a href="..." class="btn btn-sm btn-outline-primary">
  <i class="fas fa-eye"></i> Xem
</a>

<!-- Icon-only button (toolbar) -->
<a href="..." class="btn btn-sm btn-outline-secondary" title="Sửa">
  <i class="fas fa-pen-to-square"></i>
</a>
```

## CSS Utility Classes

### Money & Numbers
```css
.text-money    /* mono + right-align + tabular-nums (for amounts) */
.text-amount   /* mono + right-align (for any number column) */
.text-account-code  /* mono + muted color (for TK codes) */
.text-positive /* green + bold */
.text-negative /* red + bold */
.text-zero     /* gray */
```

### Tables
```html
<table class="table table-compact table-hover">
```
`.table-compact` gives: 6px/12px padding, uppercase sticky headers, stripe + hover rows.

### Row Types
```html
<tr class="row-total">      <!-- yellow bg, bold -->
<tr class="row-section">    <!-- section header row -->
```

### Status Badges
```html
<span class="badge badge-draft">Nháp</span>
<span class="badge badge-pending">Chờ duyệt</span>
<span class="badge badge-approved">Đã duyệt</span>
<span class="badge badge-posted">Đã ghi sổ</span>
<span class="badge badge-paid">Đã thanh toán</span>
<span class="badge badge-overdue">Quá hạn</span>
<span class="badge badge-cancelled">Đã hủy</span>
<span class="badge badge-locked">Đã khóa</span>
```

### KPI Cards
```html
<div class="kpi-row">
  <div class="kpi-card">
    <div class="kpi-icon kpi-icon-primary"><i class="fas fa-wallet"></i></div>
    <div class="kpi-label">Tiền mặt</div>
    <div class="kpi-value">1,500,000</div>
  </div>
</div>
```

## Button Sizes

| Class | Height | Usage |
|-------|--------|-------|
| `.btn-sm` | 28px | Table actions, toolbar |
| Default | 34px | Form submit, primary actions |
| `.btn-lg` | 42px | Hero CTAs (rare) |

## Template Structure

```html
{% extends "base.html" %}
{% block title %}Page Title{% endblock %}
{% block page_title %}Page Title{% endblock %}
{% block main_content %}
  <!-- content here -->
{% endblock %}
```

## Responsive

- Sidebar collapses on <992px
- Tables scroll horizontally on small screens
- Print: sidebar/topbar hidden, A4 @page margins

## CDN Links (base.html)

```html
<!-- Fonts -->
https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600

<!-- Bootstrap 5.3 -->
https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css
https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js

<!-- Font Awesome 6 -->
https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css
```
