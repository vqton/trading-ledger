/**
 * VAS Accounting - App JS
 * Sidebar toggle (localStorage), Toast, Loading, ConfirmDelete, Notifications
 */
(function () {
  'use strict';

  /* ========================================================================
     SIDEBAR: Toggle + localStorage state
     ======================================================================== */

  var SIDEBAR_KEY = 'vas_sidebar_state';  // 'expanded' | 'collapsed'
  var MOBILE_KEY  = 'vas_mobile_sidebar';  // 'open' | 'closed'

  function getSidebar()  { return document.getElementById('sidebar'); }
  function getBackdrop() { return document.getElementById('sidebarBackdrop'); }
  function isDesktop()   { return window.innerWidth > 992; }

  // Restore sidebar state from localStorage
  function restoreSidebar() {
    var sb = getSidebar();
    if (!sb) return;
    var state = localStorage.getItem(SIDEBAR_KEY);
    if (state === 'collapsed' && isDesktop()) {
      sb.classList.add('collapsed');
    } else {
      sb.classList.remove('collapsed');
    }
  }

  // Desktop: collapse/expand toggle
  var collapseBtn = document.getElementById('sidebarCollapseBtn');
  if (collapseBtn) {
    collapseBtn.addEventListener('click', function () {
      var sb = getSidebar();
      if (!sb) return;
      sb.classList.toggle('collapsed');
      localStorage.setItem(SIDEBAR_KEY, sb.classList.contains('collapsed') ? 'collapsed' : 'expanded');
    });
  }

  // Mobile: hamburger open/close
  var hamburgerBtn = document.getElementById('hamburgerBtn');
  if (hamburgerBtn) {
    hamburgerBtn.addEventListener('click', function () {
      var sb = getSidebar();
      var bd = getBackdrop();
      if (!sb) return;
      sb.classList.toggle('mobile-open');
      if (bd) bd.classList.toggle('show');
      localStorage.setItem(MOBILE_KEY, sb.classList.contains('mobile-open') ? 'open' : 'closed');
    });
  }

  // Close mobile sidebar on backdrop click
  var backdrop = getBackdrop();
  if (backdrop) {
    backdrop.addEventListener('click', function () {
      var sb = getSidebar();
      if (sb) sb.classList.remove('mobile-open');
      backdrop.classList.remove('show');
      localStorage.setItem(MOBILE_KEY, 'closed');
    });
  }

  // Close mobile sidebar on nav link click (for small screens)
  document.querySelectorAll('.sidebar .nav-link').forEach(function (link) {
    link.addEventListener('click', function () {
      if (!isDesktop()) {
        var sb = getSidebar();
        var bd = getBackdrop();
        if (sb) sb.classList.remove('mobile-open');
        if (bd) bd.classList.remove('show');
      }
    });
  });

  // Active menu highlighting: match current URL to nav links
  function highlightActiveMenu() {
    var currentPath = window.location.pathname;
    var bestMatch = null;
    var bestLen = 0;
    document.querySelectorAll('.sidebar .nav-link').forEach(function (link) {
      link.classList.remove('active');
      var href = link.getAttribute('href');
      if (href && currentPath.indexOf(href) === 0 && href.length > bestLen) {
        bestMatch = link;
        bestLen = href.length;
      }
    });
    if (bestMatch) {
      bestMatch.classList.add('active');
      // Expand parent accordion if collapsed
      var parentCollapse = bestMatch.closest('.collapse');
      if (parentCollapse && !parentCollapse.classList.contains('show')) {
        new bootstrap.Collapse(parentCollapse, { show: true });
      }
    }
  }

  // Init
  restoreSidebar();
  highlightActiveMenu();

  // Save accordion state
  document.querySelectorAll('#sidebarAccordion .collapse').forEach(function (el) {
    el.addEventListener('shown.bs.collapse', function () {
      saveAccordionState();
    });
    el.addEventListener('hidden.bs.collapse', function () {
      saveAccordionState();
    });
  });

  function saveAccordionState() {
    var state = {};
    document.querySelectorAll('#sidebarAccordion .collapse').forEach(function (el) {
      state[el.id] = el.classList.contains('show');
    });
    localStorage.setItem('vas_sidebar_accordion', JSON.stringify(state));
  }

  function restoreAccordionState() {
    try {
      var state = JSON.parse(localStorage.getItem('vas_sidebar_accordion'));
      if (!state) return;
      Object.keys(state).forEach(function (id) {
        var el = document.getElementById(id);
        if (!el) return;
        if (state[id]) {
          el.classList.add('show');
          var toggle = document.querySelector('[data-bs-target="#' + id + '"]');
          if (toggle) toggle.setAttribute('aria-expanded', 'true');
        } else {
          el.classList.remove('show');
          var toggle = document.querySelector('[data-bs-target="#' + id + '"]');
          if (toggle) toggle.setAttribute('aria-expanded', 'false');
        }
      });
    } catch (e) { /* ignore */ }
  }
  restoreAccordionState();


  /* ========================================================================
     TOAST NOTIFICATION (Top-Right, auto-hide 3s)
     ======================================================================== */

  function ensureToastContainer() {
    var c = document.getElementById('toastContainer');
    if (!c) {
      c = document.createElement('div');
      c.id = 'toastContainer';
      c.style.cssText = 'position:fixed;top:72px;right:20px;z-index:9999;display:flex;flex-direction:column;gap:8px;max-width:380px;';
      document.body.appendChild(c);
    }
    return c;
  }

  window.showToast = function (message, type, duration) {
    type = type || 'info';
    duration = duration || 3000;
    var iconMap = { success: 'fa-check-circle', danger: 'fa-exclamation-circle', warning: 'fa-exclamation-triangle', info: 'fa-info-circle' };
    var bgMap = { success: '#f0fdf4', danger: '#fef2f2', warning: '#fffbeb', info: '#eff6ff' };
    var borderMap = { success: '#22c55e', danger: '#ef4444', warning: '#f59e0b', info: '#2563eb' };

    var toast = document.createElement('div');
    toast.style.cssText = 'display:flex;align-items:flex-start;gap:10px;padding:12px 14px;background:' + bgMap[type] + ';border-left:4px solid ' + borderMap[type] + ';border-radius:8px;box-shadow:0 4px 12px rgba(0,0,0,.12);font-size:13px;line-height:1.4;animation:toastSlideIn .2s ease;';
    toast.innerHTML = '<i class="fas ' + iconMap[type] + '" style="color:' + borderMap[type] + ';font-size:1rem;margin-top:2px"></i>' +
      '<div style="flex:1;color:#1e293b">' + message + '</div>' +
      '<button type="button" style="background:none;border:none;color:#94a3b8;cursor:pointer;font-size:.9rem;padding:0" onclick="this.parentElement.remove()">&times;</button>';
    ensureToastContainer().appendChild(toast);
    setTimeout(function () {
      toast.style.opacity = '0'; toast.style.transform = 'translateX(100%)'; toast.style.transition = 'all .2s ease';
      setTimeout(function () { toast.remove(); }, 200);
    }, duration);
  };

  // Auto-convert flash alerts to toasts
  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.alert-dismissible').forEach(function (el) {
      var cls = el.classList;
      var type = 'info';
      if (cls.contains('alert-success')) type = 'success';
      else if (cls.contains('alert-danger')) type = 'danger';
      else if (cls.contains('alert-warning')) type = 'warning';
      var msg = el.textContent.trim();
      if (msg) showToast(msg, type);
      el.style.display = 'none';
    });
  });

  // Inject animation CSS
  var style = document.createElement('style');
  style.textContent = '@keyframes toastSlideIn{from{opacity:0;transform:translateX(100%)}to{opacity:1;transform:translateX(0)}}';
  document.head.appendChild(style);


  /* ========================================================================
     LOADING SPINNER
     ======================================================================== */

  var overlay = document.createElement('div');
  overlay.id = 'loadingOverlay';
  overlay.style.cssText = 'position:fixed;inset:0;background:rgba(255,255,255,.7);backdrop-filter:blur(2px);display:none;align-items:center;justify-content:center;z-index:9998;';
  overlay.innerHTML = '<div class="spinner-border text-primary" role="status" style="width:3rem;height:3rem"><span class="visually-hidden">Loading...</span></div>';
  document.body.appendChild(overlay);

  window.showLoading = function () { overlay.style.display = 'flex'; };
  window.hideLoading = function () { overlay.style.display = 'none'; };

  document.addEventListener('submit', function (e) {
    if (e.target.tagName === 'FORM' && !e.target.hasAttribute('data-no-loading')) showLoading();
  });


  /* ========================================================================
     CONFIRM DELETE
     ======================================================================== */

  document.addEventListener('click', function (e) {
    var btn = e.target.closest('[data-confirm]');
    if (!btn) return;
    e.preventDefault();
    var msg = btn.getAttribute('data-confirm') || 'Bạn có chắc muốn xóa?';
    var form = btn.closest('form');
    var modalEl = document.getElementById('confirmDeleteModal');
    if (modalEl) {
      modalEl.querySelector('.modal-body p').textContent = msg;
      var confirmBtn = modalEl.querySelector('[data-confirm-yes]');
      confirmBtn.onclick = function () {
        bootstrap.Modal.getInstance(modalEl).hide();
        if (form) form.submit();
        else if (btn.href) window.location.href = btn.href;
      };
      new bootstrap.Modal(modalEl).show();
    } else {
      if (confirm(msg)) { if (form) form.submit(); else if (btn.href) window.location.href = btn.href; }
    }
  });


  /* ========================================================================
     NOTIFICATIONS (poll unread count)
     ======================================================================== */

  function pollNotifications() {
    var badge = document.getElementById('notifBadge');
    if (!badge) return;
    fetch('/notifications/api/unread-count')
      .then(function (r) { return r.json(); })
      .then(function (data) {
        if (data.status === 'success' && data.count > 0) {
          badge.textContent = data.count > 99 ? '99+' : data.count;
          badge.style.display = 'flex';
        } else {
          badge.style.display = 'none';
        }
      })
      .catch(function () {});
  }

  // Poll every 30s
  pollNotifications();
  setInterval(pollNotifications, 30000);


  /* ========================================================================
     FORM ENHANCEMENTS
     ======================================================================== */

  // 1. Auto-scroll to first error on page load
  document.addEventListener('DOMContentLoaded', function () {
    var firstError = document.querySelector('.has-error, .is-invalid');
    if (firstError) {
      firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
      // Focus the input inside
      var input = firstError.querySelector('.form-control, .form-select');
      if (input) setTimeout(function () { input.focus(); }, 300);
    }
  });

  // 2. Dynamic show/hide fields based on checkbox/select
  //    Usage: <input data-toggle-target="myField">  +  <div data-show-if="myField" data-show-value="y">
  function initDynamicFields() {
    // Checkbox toggle
    document.querySelectorAll('[data-toggle-target]').forEach(function (el) {
      var target = el.getAttribute('data-toggle-target');
      function update() {
        var checked = el.checked;
        document.querySelectorAll('[data-show-if="' + target + '"]').forEach(function (dep) {
          var showVal = dep.getAttribute('data-show-value') || 'y';
          var shouldShow = checked ? (showVal === 'y') : (showVal !== 'y');
          dep.style.display = shouldShow ? '' : 'none';
          if (shouldShow) dep.classList.remove('hidden-field');
          else dep.classList.add('hidden-field');
        });
      }
      el.addEventListener('change', update);
      update(); // init on load
    });

    // Select toggle
    document.querySelectorAll('select').forEach(function (sel) {
      sel.addEventListener('change', function () {
        var val = this.value;
        var id = this.id;
        document.querySelectorAll('[data-show-if="' + id + '"]').forEach(function (dep) {
          var showVal = dep.getAttribute('data-show-value') || '';
          dep.style.display = (val === showVal) ? '' : 'none';
        });
      });
    });
  }
  initDynamicFields();

  // 3. Native date picker enhancement (click to open)
  document.querySelectorAll('input[data-datepicker], input[type="date"]').forEach(function (el) {
    el.addEventListener('click', function () {
      if (this.showPicker) this.showPicker();
    });
  });

  // 4. Form dirty state warning
  var formDirty = false;
  document.querySelectorAll('form').forEach(function (form) {
    if (form.hasAttribute('data-no-dirty')) return;
    form.querySelectorAll('input, select, textarea').forEach(function (input) {
      input.addEventListener('change', function () { formDirty = true; });
      input.addEventListener('input', function () { formDirty = true; });
    });
    form.addEventListener('submit', function () { formDirty = false; });
  });
  window.addEventListener('beforeunload', function (e) {
    if (formDirty) { e.preventDefault(); e.returnValue = ''; }
  });

})();
