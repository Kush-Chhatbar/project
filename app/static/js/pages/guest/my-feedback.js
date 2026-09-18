/* Guest "My Feedback" — GET /api/feedback/list?rating_range&from_date&to_date
   The backend returns the guest's feedback (the list endpoint serves the
   authenticated user's data set). Response fields are rendered exactly as
   returned; no sentiment field exists per feedback item, so none is shown. */

(function () {
  'use strict';

  const user = Auth.requireRole('guest');
  if (!user) return;

  const PAGE_SIZE = 6;
  let allFeedback = [];
  let filtered = [];
  let page = 1;

  document.addEventListener('DOMContentLoaded', () => {
    UI.initNav();
    bindFilters();
    load();
  });

  function bindFilters() {
    const apply = UI.debounce(() => { page = 1; load(); });
    document.getElementById('filter-rating').addEventListener('change', apply);
    document.getElementById('filter-from').addEventListener('change', apply);
    document.getElementById('filter-to').addEventListener('change', apply);
    document.getElementById('clear-filters').addEventListener('click', () => {
      document.getElementById('filter-rating').value = '';
      document.getElementById('filter-from').value = '';
      document.getElementById('filter-to').value = '';
      page = 1;
      load();
    });
  }

  async function load() {
    const container = document.getElementById('feedback-list');
    container.innerHTML = '<div class="skeleton-block"></div><div class="skeleton-block" style="margin-top:12px"></div>';

    try {
      const filters = {
        rating_range: document.getElementById('filter-rating').value || undefined,
        from_date: document.getElementById('filter-from').value || undefined,
        to_date: document.getElementById('filter-to').value || undefined
      };
      const result = await API.feedback.list(filters);
      const payload = result.data || {};
      allFeedback = Array.isArray(payload) ? payload : (payload.feedbacks || []);
      filtered = allFeedback;
      render();
    } catch (err) {
      container.innerHTML = UI.errorState(err.message, { retry: true });
      container.querySelector('[data-retry]')?.addEventListener('click', load);
      UI.showToast(err.message, 'error');
    }
  }

  function render() {
    const container = document.getElementById('feedback-list');
    if (!filtered.length) {
      container.innerHTML = UI.emptyState({
        icon: 'fa-star',
        title: 'No feedback found',
        message: allFeedback.length
          ? 'No feedback matches your filters. Try widening the date range or rating.'
          : 'You have not submitted any feedback yet. We would love to hear about your stay!'
      });
      return;
    }

    const total = filtered.length;
    const pages = Math.max(1, Math.ceil(total / PAGE_SIZE));
    page = Math.min(page, pages);
    const slice = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

    container.innerHTML = `
      <div class="muted" style="margin-bottom:10px; font-size:.85rem">${total} submission${total === 1 ? '' : 's'}</div>
      <div class="feedback-cards">
        ${slice.map((item) => `
          <div class="card" style="margin-top:12px">
            <div class="card__header" style="margin-bottom:8px">
              <div>${UI.ratingStars(item.overall_rating)}</div>
              <span class="muted" style="font-size:.82rem">${UI.formatDateTime(item.feedback_date)}</span>
            </div>
            ${item.guest_comment
              ? `<p style="margin-bottom:10px">${UI.escapeHtml(item.guest_comment)}</p>`
              : '<p class="muted" style="margin-bottom:10px">No comment provided.</p>'}
            <div class="detail-grid" style="grid-template-columns:repeat(auto-fit,minmax(140px,1fr))">
              <div class="detail-item" style="border:none;padding:4px 0"><dt>Cleanliness</dt><dd>${UI.ratingStars(item.cleanliness_rating, { showValue: false })}</dd></div>
              <div class="detail-item" style="border:none;padding:4px 0"><dt>Staff</dt><dd>${UI.ratingStars(item.staff_rating, { showValue: false })}</dd></div>
              <div class="detail-item" style="border:none;padding:4px 0"><dt>Food</dt><dd>${UI.ratingStars(item.food_rating, { showValue: false })}</dd></div>
              <div class="detail-item" style="border:none;padding:4px 0"><dt>Service</dt><dd>${UI.ratingStars(item.service_rating, { showValue: false })}</dd></div>
            </div>
            <button class="btn btn--ghost btn--sm" data-view-feedback="${item.id}" style="margin-top:8px">
              <i class="fa-regular fa-eye"></i> View details
            </button>
          </div>`).join('')}
      </div>`;

    const pagination = document.createElement('div');
    pagination.className = 'pagination';
    container.appendChild(pagination);
    UI.renderPagination(pagination, { page, pageSize: PAGE_SIZE, total, onPageChange: (p) => { page = p; render(); } });

    container.querySelectorAll('[data-view-feedback]').forEach((button) => {
      button.addEventListener('click', () => viewDetails(button.getAttribute('data-view-feedback')));
    });
  }

  async function viewDetails(feedbackId) {
    try {
      const result = await API.feedback.show(feedbackId);
      const feedback = (result.data || {}).feedback || {};
      const guest = feedback.guest_details || {};

      const modal = document.createElement('div');
      modal.className = 'modal';
      modal.setAttribute('aria-hidden', 'true');
      modal.innerHTML = `
        <div class="modal__panel" role="dialog" aria-modal="true">
          <div class="modal__header">
            <h3>Feedback #${UI.escapeHtml(feedback.id)} ${UI.ratingStars(feedback.overall_rating)}</h3>
            <button type="button" class="modal__close" data-close-modal aria-label="Close"><i class="fa-solid fa-xmark"></i></button>
          </div>
          <div class="modal__body">
            <dl class="detail-grid">
              <div class="detail-item"><dt>Submitted</dt><dd>${UI.formatDateTime(feedback.feedback_date)}</dd></div>
              <div class="detail-item"><dt>Stay number</dt><dd>${UI.escapeHtml(guest.stay_number || '—')}</dd></div>
              <div class="detail-item"><dt>Room</dt><dd>${UI.escapeHtml(guest.room_number || '—')} (${UI.escapeHtml(guest.room_type || '—')})</dd></div>
              <div class="detail-item"><dt>Stay dates</dt><dd>${UI.formatDate(guest.check_in_date)} → ${UI.formatDate(guest.check_out_date)}</dd></div>
            </dl>
            <h3 style="margin-top:14px">Ratings</h3>
            <dl class="detail-grid">
              <div class="detail-item"><dt>Cleanliness</dt><dd>${UI.ratingStars(feedback.cleanliness_rating)}</dd></div>
              <div class="detail-item"><dt>Staff</dt><dd>${UI.ratingStars(feedback.staff_rating)}</dd></div>
              <div class="detail-item"><dt>Food</dt><dd>${UI.ratingStars(feedback.food_rating)}</dd></div>
              <div class="detail-item"><dt>Service</dt><dd>${UI.ratingStars(feedback.service_rating)}</dd></div>
            </dl>
            <h3 style="margin-top:14px">Comment</h3>
            <p>${feedback.guest_comment ? UI.escapeHtml(feedback.guest_comment) : '<span class="muted">No comment provided.</span>'}</p>
          </div>
          <div class="modal__footer">
            <button type="button" class="btn btn--primary" data-close-modal>Close</button>
          </div>
        </div>`;
      document.body.appendChild(modal);
      UI.showModal(modal);
      modal.addEventListener('click', (event) => {
        if (event.target === modal || event.target.closest('[data-close-modal]')) {
          UI.hideModal(modal);
          setTimeout(() => modal.remove(), 250);
        }
      });
    } catch (err) {
      UI.showToast(err.message, 'error');
    }
  }
})();
