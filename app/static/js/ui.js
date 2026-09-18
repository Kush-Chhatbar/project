/* ==========================================================================
   Shared UI component helpers used by every role module.
   ========================================================================== */

(function () {
  'use strict';

  /* ---------------------------- utilities ---------------------------- */

  function escapeHtml(value) {
    if (value === null || value === undefined) return '';
    return String(value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function formatDate(value) {
    if (!value) return '—';
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return escapeHtml(value);
    return date.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
  }

  function formatDateTime(value) {
    if (!value) return '—';
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return escapeHtml(value);
    return date.toLocaleString(undefined, {
      year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
    });
  }

  function debounce(fn, wait = 350) {
    let timer = null;
    return function (...args) {
      clearTimeout(timer);
      timer = setTimeout(() => fn.apply(this, args), wait);
    };
  }

  /* ------------------------------ toasts ------------------------------ */

  const TOAST_ICONS = {
    success: 'fa-circle-check',
    error: 'fa-circle-exclamation',
    warning: 'fa-triangle-exclamation',
    info: 'fa-circle-info'
  };

  function showToast(message, type = 'info', { duration = 4200 } = {}) {
    let container = document.querySelector('.toast-container');
    if (!container) {
      container = document.createElement('div');
      container.className = 'toast-container';
      container.setAttribute('aria-live', 'polite');
      document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast toast--${type}`;
    toast.setAttribute('role', 'status');
    toast.innerHTML = `
      <i class="fa-solid ${TOAST_ICONS[type] || TOAST_ICONS.info}"></i>
      <span class="toast__message">${escapeHtml(message)}</span>
      <button type="button" class="toast__close" aria-label="Dismiss notification">
        <i class="fa-solid fa-xmark"></i>
      </button>`;
    container.appendChild(toast);

    const remove = () => {
      toast.classList.add('toast--leaving');
      setTimeout(() => toast.remove(), 220);
    };
    toast.querySelector('.toast__close').addEventListener('click', remove);
    if (duration > 0) setTimeout(remove, duration);
    return toast;
  }

  /* ------------------------- loading overlays ------------------------- */

  function showLoading(message = 'Loading…') {
    let overlay = document.querySelector('.loading-overlay');
    if (!overlay) {
      overlay = document.createElement('div');
      overlay.className = 'loading-overlay';
      overlay.innerHTML = `
        <div class="loading-overlay__box" role="status" aria-live="polite">
          <span class="spinner spinner--lg"></span>
          <span class="loading-overlay__text"></span>
        </div>`;
      document.body.appendChild(overlay);
    }
    overlay.querySelector('.loading-overlay__text').textContent = message;
    overlay.classList.add('is-visible');
  }

  function hideLoading() {
    const overlay = document.querySelector('.loading-overlay');
    if (overlay) overlay.classList.remove('is-visible');
  }

  /** Puts a button into a loading state and returns how to restore it. */
  function setButtonLoading(button, loading) {
    if (!button) return () => {};
    if (loading) {
      button.dataset.originalHtml = button.innerHTML;
      button.disabled = true;
      button.classList.add('is-loading');
      button.innerHTML = `<span class="spinner spinner--sm spinner--light"></span><span> ${escapeHtml(button.dataset.loadingText || 'Please wait…')}</span>`;
      return () => setButtonLoading(button, false);
    }
    button.disabled = false;
    button.classList.remove('is-loading');
    if (button.dataset.originalHtml) button.innerHTML = button.dataset.originalHtml;
    return () => {};
  }

  /* ------------------------------ modals ------------------------------ */

  function showModal(modal) {
    if (typeof modal === 'string') modal = document.getElementById(modal);
    if (!modal) return;
    modal.classList.add('is-open');
    modal.setAttribute('aria-hidden', 'false');
    document.body.classList.add('modal-open');
    const focusable = modal.querySelector('[data-autofocus]') ||
      modal.querySelector('button, [href], input, select, textarea');
    if (focusable) focusable.focus();
  }

  function hideModal(modal) {
    if (typeof modal === 'string') modal = document.getElementById(modal);
    if (!modal) return;
    modal.classList.remove('is-open');
    modal.setAttribute('aria-hidden', 'true');
    if (!document.querySelector('.modal.is-open')) document.body.classList.remove('modal-open');
  }

  function initModals() {
    document.addEventListener('click', (event) => {
      const openTrigger = event.target.closest('[data-open-modal]');
      if (openTrigger) {
        showModal(openTrigger.getAttribute('data-open-modal'));
      }
      const closeTrigger = event.target.closest('[data-close-modal]');
      if (closeTrigger) {
        const modal = closeTrigger.closest('.modal');
        hideModal(modal);
      }
      if (event.target.classList && event.target.classList.contains('modal')) {
        hideModal(event.target);
      }
    });
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') {
        document.querySelectorAll('.modal.is-open').forEach((modal) => hideModal(modal));
      }
    });
  }

  /** Promise-based confirmation dialog built on the modal system. */
  function confirmDialog({ title = 'Are you sure?', message = '', confirmText = 'Confirm', danger = false } = {}) {
    return new Promise((resolve) => {
      let modal = document.getElementById('confirm-dialog');
      if (!modal) {
        modal = document.createElement('div');
        modal.id = 'confirm-dialog';
        modal.className = 'modal';
        modal.setAttribute('aria-hidden', 'true');
        modal.innerHTML = `
          <div class="modal__panel modal__panel--sm" role="dialog" aria-modal="true" aria-labelledby="confirm-dialog-title">
            <div class="modal__header">
              <h3 id="confirm-dialog-title"></h3>
              <button type="button" class="modal__close" data-close-modal aria-label="Close"><i class="fa-solid fa-xmark"></i></button>
            </div>
            <div class="modal__body">
              <p id="confirm-dialog-message"></p>
            </div>
            <div class="modal__footer">
              <button type="button" class="btn btn--ghost" data-confirm-cancel>Cancel</button>
              <button type="button" class="btn btn--primary" data-confirm-ok></button>
            </div>
          </div>`;
        document.body.appendChild(modal);
      }

      modal.querySelector('#confirm-dialog-title').textContent = title;
      modal.querySelector('#confirm-dialog-message').textContent = message;
      const okButton = modal.querySelector('[data-confirm-ok]');
      okButton.textContent = confirmText;
      okButton.className = `btn ${danger ? 'btn--danger' : 'btn--primary'}`;

      const done = (result) => {
        okButton.removeEventListener('click', onOk);
        modal.removeEventListener('click', onCancelClick);
        document.removeEventListener('keydown', onEscape);
        hideModal(modal);
        resolve(result);
      };
      const onOk = () => done(true);
      const onCancelClick = (event) => {
        if (event.target.closest('[data-confirm-cancel]') || event.target === modal) done(false);
      };
      const onEscape = (event) => { if (event.key === 'Escape') done(false); };

      okButton.addEventListener('click', onOk);
      modal.addEventListener('click', onCancelClick);
      document.addEventListener('keydown', onEscape);
      showModal(modal);
    });
  }

  /* ----------------------------- badges ----------------------------- */

  const STATUS_BADGE_CLASS = {
    'New': 'badge--new',
    'Assigned': 'badge--assigned',
    'In Progress': 'badge--progress',
    'Resolved': 'badge--resolved',
    'Closed': 'badge--closed',
    'Rejected': 'badge--rejected'
  };

  const PRIORITY_BADGE_CLASS = {
    'Critical': 'badge--critical',
    'High': 'badge--high',
    'Medium': 'badge--medium',
    'Low': 'badge--low'
  };

  const statusBadge = (status) =>
    `<span class="badge ${STATUS_BADGE_CLASS[status] || 'badge--neutral'}">${escapeHtml(status || '—')}</span>`;

  const priorityBadge = (priority) =>
    `<span class="badge badge--priority ${PRIORITY_BADGE_CLASS[priority] || 'badge--neutral'}">${escapeHtml(priority || '—')}</span>`;

  const slaBadge = (slaStatus) => {
    if (!slaStatus) return '<span class="badge badge--neutral">—</span>';
    const breached = slaStatus === 'Breached';
    return `<span class="badge ${breached ? 'badge--sla-breached' : 'badge--sla-ok'}">
      <i class="fa-regular fa-clock"></i> ${escapeHtml(slaStatus)}</span>`;
  };

  const sentimentBadge = (sentiment) => {
    const cls = { Positive: 'badge--resolved', Negative: 'badge--rejected', Neutral: 'badge--neutral' }[sentiment] || 'badge--neutral';
    return `<span class="badge ${cls}">${escapeHtml(sentiment || 'Neutral')}</span>`;
  };

  /* ----------------------------- ratings ----------------------------- */

  function ratingStars(value, { showValue = true } = {}) {
    const rating = Number(value);
    if (Number.isNaN(rating) || rating <= 0) return '<span class="muted">No rating</span>';
    let stars = '';
    for (let i = 1; i <= 5; i += 1) {
      if (rating >= i) {
        stars += '<i class="fa-solid fa-star"></i>';
      } else if (rating >= i - 0.5) {
        stars += '<i class="fa-solid fa-star-half-stroke"></i>';
      } else {
        stars += '<i class="fa-regular fa-star"></i>';
      }
    }
    const valuePart = showValue ? `<span class="stars__value">${rating.toFixed(1)}</span>` : '';
    return `<span class="stars" aria-label="${rating.toFixed(1)} out of 5">${stars}${valuePart}</span>`;
  }

  /* --------------------------- pagination --------------------------- */
  /* The backend returns full lists (no server-side pagination), so we page
     through real data client-side. */

  function renderPagination(container, { page, pageSize, total, onPageChange }) {
    if (!container) return;
    const pages = Math.max(1, Math.ceil(total / pageSize));
    if (pages <= 1) {
      container.innerHTML = '';
      return;
    }

    const windowSize = 2;
    let numbers = '';
    const start = Math.max(1, page - windowSize);
    const end = Math.min(pages, page + windowSize);

    if (start > 1) {
      numbers += `<button type="button" class="pagination__page" data-page="1">1</button>`;
      if (start > 2) numbers += '<span class="pagination__ellipsis">…</span>';
    }
    for (let p = start; p <= end; p += 1) {
      numbers += `<button type="button" class="pagination__page ${p === page ? 'is-active' : ''}" data-page="${p}" ${p === page ? 'aria-current="page"' : ''}>${p}</button>`;
    }
    if (end < pages) {
      if (end < pages - 1) numbers += '<span class="pagination__ellipsis">…</span>';
      numbers += `<button type="button" class="pagination__page" data-page="${pages}">${pages}</button>`;
    }

    container.innerHTML = `
      <button type="button" class="pagination__page pagination__nav" data-page="${page - 1}" ${page <= 1 ? 'disabled' : ''} aria-label="Previous page">
        <i class="fa-solid fa-chevron-left"></i>
      </button>
      ${numbers}
      <button type="button" class="pagination__page pagination__nav" data-page="${page + 1}" ${page >= pages ? 'disabled' : ''} aria-label="Next page">
        <i class="fa-solid fa-chevron-right"></i>
      </button>`;

    container.querySelectorAll('button[data-page]').forEach((button) => {
      button.addEventListener('click', () => {
        const target = Number(button.getAttribute('data-page'));
        if (target >= 1 && target <= pages && target !== page) onPageChange(target);
      });
    });
  }

  /* --------------------------- empty states --------------------------- */

  function emptyState({ icon = 'fa-inbox', title = 'Nothing here yet', message = '' } = {}) {
    return `
      <div class="empty-state">
        <i class="fa-solid ${icon}"></i>
        <h3>${escapeHtml(title)}</h3>
        ${message ? `<p>${escapeHtml(message)}</p>` : ''}
      </div>`;
  }

  function errorState(message, { retry = null } = {}) {
    return `
      <div class="empty-state empty-state--error">
        <i class="fa-solid fa-triangle-exclamation"></i>
        <h3>Something went wrong</h3>
        <p>${escapeHtml(message)}</p>
        ${retry ? '<button type="button" class="btn btn--ghost" data-retry>Try again</button>' : ''}
      </div>`;
  }

  /* --------------------------- nav helpers --------------------------- */

  function initNav() {
    document.querySelectorAll('[data-sidebar-toggle]').forEach((toggle) => {
      toggle.addEventListener('click', () => {
        document.body.classList.toggle('sidebar-open');
      });
    });
    document.addEventListener('click', (event) => {
      if (document.body.classList.contains('sidebar-open') &&
          !event.target.closest('.sidebar') &&
          !event.target.closest('[data-sidebar-toggle]')) {
        document.body.classList.remove('sidebar-open');
      }
    });

    // Highlight the active nav link for the current path.
    const path = window.location.pathname;
    document.querySelectorAll('.sidebar__link').forEach((link) => {
      if (link.getAttribute('href') === path) link.classList.add('is-active');
    });

    document.querySelectorAll('[data-logout]').forEach((button) => {
      button.addEventListener('click', async () => {
        const confirmed = await confirmDialog({
          title: 'Sign out',
          message: 'Are you sure you want to sign out?',
          confirmText: 'Sign out',
          danger: true
        });
        if (confirmed) window.Auth.logout();
      });
    });
  }

  /* ---------------------------- form utils ---------------------------- */

  function setFieldError(input, message) {
    if (!input) return;
    const wrapper = input.closest('.form-field') || input.parentElement;
    let error = wrapper.querySelector('.form-error');
    if (message) {
      if (!error) {
        error = document.createElement('p');
        error.className = 'form-error';
        wrapper.appendChild(error);
      }
      error.textContent = message;
      input.classList.add('is-invalid');
      input.setAttribute('aria-invalid', 'true');
    } else {
      if (error) error.remove();
      input.classList.remove('is-invalid');
      input.removeAttribute('aria-invalid');
    }
  }

  function clearFormErrors(form) {
    form.querySelectorAll('.form-error').forEach((el) => el.remove());
    form.querySelectorAll('.is-invalid').forEach((el) => {
      el.classList.remove('is-invalid');
      el.removeAttribute('aria-invalid');
    });
  }

  window.UI = {
    escapeHtml, formatDate, formatDateTime, debounce,
    showToast, showLoading, hideLoading, setButtonLoading,
    showModal, hideModal, initModals, confirmDialog,
    statusBadge, priorityBadge, slaBadge, sentimentBadge, ratingStars,
    renderPagination, emptyState, errorState, initNav,
    setFieldError, clearFormErrors
  };
})();
