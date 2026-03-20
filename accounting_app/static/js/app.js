/**
 * VAS Accounting - UI Components (Toast, Loading, Confirm Delete)
 */
(function () {
  'use strict';

  /* ========================================================================
     TOAST NOTIFICATION (Top-Right, auto-hide 3s)
     ======================================================================== */

  // Create toast container on page load
  function ensureToastContainer() {
    let c = document.getElementById('toastContainer');
    if (!c) {
      c = document.createElement('div');
      c.id = 'toastContainer';
      c.style.cssText = 'position:fixed;top:72px;right:20px;z-index:9999;display:flex;flex-direction:column;gap:8px;max-width:380px;';
      document.body.appendChild(c);
    }
    return c;
  }

  /**
   * Show a toast notification.
   * @param {string} message
   * @param {'success'|'danger'|'warning'|'info'} type
   * @param {number} duration - ms (default 3000)
   */
  window.showToast = function (message, type, duration) {
    type = type || 'info';
    duration = duration || 3000;

    const iconMap = {
      success: 'fa-check-circle',
      danger: 'fa-exclamation-circle',
      warning: 'fa-exclamation-triangle',
      info: 'fa-info-circle'
    };

    const bgMap = {
      success: '#f0fdf4',
      danger: '#fef2f2',
      warning: '#fffbeb',
      info: '#eff6ff'
    };

    const borderMap = {
      success: '#22c55e',
      danger: '#ef4444',
      warning: '#f59e0b',
      info: '#2563eb'
    };

    const toast = document.createElement('div');
    toast.style.cssText =
      'display:flex;align-items:flex-start;gap:10px;padding:12px 14px;' +
      'background:' + bgMap[type] + ';' +
      'border-left:4px solid ' + borderMap[type] + ';' +
      'border-radius:8px;box-shadow:0 4px 12px rgba(0,0,0,.12);' +
      'font-size:13px;line-height:1.4;animation:toastSlideIn .2s ease;';

    toast.innerHTML =
      '<i class="fas ' + iconMap[type] + '" style="color:' + borderMap[type] + ';font-size:1rem;margin-top:2px"></i>' +
      '<div style="flex:1;color:#1e293b">' + message + '</div>' +
      '<button type="button" style="background:none;border:none;color:#94a3b8;cursor:pointer;font-size:.9rem;padding:0" ' +
      'onclick="this.parentElement.remove()">&times;</button>';

    const container = ensureToastContainer();
    container.appendChild(toast);

    // Auto-remove
    setTimeout(function () {
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(100%)';
      toast.style.transition = 'all .2s ease';
      setTimeout(function () { toast.remove(); }, 200);
    }, duration);
  };

  // Inject CSS animation
  const toastStyle = document.createElement('style');
  toastStyle.textContent = '@keyframes toastSlideIn{from{opacity:0;transform:translateX(100%)}to{opacity:1;transform:translateX(0)}}';
  document.head.appendChild(toastStyle);

  // Auto-show flash messages as toasts
  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.alert-dismissible').forEach(function (el) {
      const cls = el.classList;
      let type = 'info';
      if (cls.contains('alert-success')) type = 'success';
      else if (cls.contains('alert-danger')) type = 'danger';
      else if (cls.contains('alert-warning')) type = 'warning';

      const msg = el.querySelector('.btn-close') ? el.textContent.trim() : el.textContent.trim();
      if (msg) showToast(msg, type);
      el.style.display = 'none';
    });
  });


  /* ========================================================================
     LOADING SPINNER (Full-screen overlay)
     ======================================================================== */

  const spinnerOverlay = document.createElement('div');
  spinnerOverlay.id = 'loadingOverlay';
  spinnerOverlay.style.cssText =
    'position:fixed;inset:0;background:rgba(255,255,255,.7);backdrop-filter:blur(2px);' +
    'display:none;align-items:center;justify-content:center;z-index:9998;';
  spinnerOverlay.innerHTML =
    '<div class="spinner-border text-primary" role="status" style="width:3rem;height:3rem">' +
    '<span class="visually-hidden">Loading...</span></div>';
  document.body.appendChild(spinnerOverlay);

  window.showLoading = function () {
    spinnerOverlay.style.display = 'flex';
  };
  window.hideLoading = function () {
    spinnerOverlay.style.display = 'none';
  };

  // Auto-show loading on form submits
  document.addEventListener('submit', function (e) {
    const form = e.target;
    if (form.tagName === 'FORM' && !form.hasAttribute('data-no-loading')) {
      showLoading();
    }
  });


  /* ========================================================================
     CONFIRM DELETE (data-confirm attribute)
     ======================================================================== */

  document.addEventListener('click', function (e) {
    const btn = e.target.closest('[data-confirm]');
    if (!btn) return;

    e.preventDefault();
    const msg = btn.getAttribute('data-confirm') || 'Bạn có chắc muốn xóa?';
    const form = btn.closest('form');

    // Use BS5 modal if exists, else use confirm()
    const modalEl = document.getElementById('confirmDeleteModal');
    if (modalEl) {
      modalEl.querySelector('.modal-body p').textContent = msg;
      const confirmBtn = modalEl.querySelector('[data-confirm-yes]');
      confirmBtn.onclick = function () {
        bootstrap.Modal.getInstance(modalEl).hide();
        if (form) form.submit();
        else if (btn.href) window.location.href = btn.href;
      };
      new bootstrap.Modal(modalEl).show();
    } else {
      if (confirm(msg)) {
        if (form) form.submit();
        else if (btn.href) window.location.href = btn.href;
      }
    }
  });

})();
