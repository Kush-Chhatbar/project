/* Admin feedback management — GET /api/feedback/list with the API's
   supported filters (rating_range, from_date, to_date). Text search filters
   the returned data client-side; no unsupported server params are sent. */

(function () {
  'use strict';

  const user = Auth.requireRole('admin');
  if (!user) return;

  const PAGE_SIZE = 8;
  let allFeedback = [];
  let filtered = [];
  let page = 1;

  document.addEventListener('DOMContentLoaded', () => {
    UI.initNav();
    bindFilters();
    load();
  });

  function bindFilters() {
    const reload = UI.debounce(() => { page = 1; load(); });
    ['filter-rating', 'filter-from', 'filter-to'].forEach((id) =>
      document.getElementById(id).addEventListener('change', reload));
    document.getElementById('filter-search').addEventListener('input', UI.debounce(() => { page = 1; render(); }));
    document.getElementById('clear-filters').addEventListener('click', () => {
      ['filter-rating', 'filter-from', 'filter-to', 'filter-search'].forEach((id) => {
        document.getElementById(id).value = '';
      });
      page = 1;
      load();
    });
  }

  async function load() {
    const container = document.getElementById('feedback-container');
    container.innerHTML = '<div class="skeleton-block"></div><div class="skeleton-block" style="margin-top:12px"></div>';

    try {
      const result = await API.feedback.list({
        rating_range: document.getElementById('filter-rating').value || undefined,
        from_date: document.getElementById('filter-from').value || undefined,
        to_date: document.getElementById('filter-to').value || undefined
      });
      const payload = result.data || {};
      allFeedback = Array.isArray(payload) ? payload : (payload.feedbacks || []);
      render();
    } catch (err) {
      container.innerHTML = UI.errorState(err.message, { retry: true });
      container.querySelector('[data-retry]')?.addEventListener('click', load);
      UI.showToast(err.message, 'error');
    }
  }

  function applySearch() {
    const query = document.getElementById('filter-search').value.trim().toLowerCase();
    if (!query) return allFeedback;
    return allFeedback.filter((item) => {
      const guest = item.guest_details || {};
      const haystack = [
        guest.guest_name, guest.guest_email, guest.room_number, guest.room_type,
        guest.stay_number, item.guest_comment
      ].filter(Boolean).join(' ').toLowerCase();
      return haystack.includes(query);
    });
  }

  function render() {
    const container = document.getElementById('feedback-container');
    filtered = applySearch();

    if (!filtered.length) {
      container.innerHTML = UI.emptyState({
        icon: 'fa-star',
        title: 'No feedback found',
        message: allFeedback.length
          ? 'Nothing matches the current filters.'
          : 'No feedback has been submitted yet.'
      });
      return;
    }

    const total = filtered.length;
    const pages = Math.max(1, Math.ceil(total / PAGE_SIZE));
    page = Math.min(page, pages);
    const slice = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

    container.innerHTML = `
      <div class="muted" style="margin-bottom:10px; font-size:.85rem">${total} submission${total === 1 ? '' : 's'}</div>
      <div class="table-wrap">
        <table class="table table-responsive-stack">
          <thead>
            <tr><th>Rating</th><th>Guest</th><th>Stay</th><th>Room</th><th>Comment</th><th>Date</th><th></th></tr>
          </thead>
          <tbody>
            ${slice.map((item) => {
              const guest = item.guest_details || {};
              return `
              <tr>
                <td data-label="Rating">${UI.ratingStars(item.overall_rating)}</td>
                <td data-label="Guest">
                  <strong>${UI.escapeHtml(guest.guest_name || '—')}</strong><br>
                  <span class="muted" style="font-size:.78rem">${UI.escapeHtml(guest.guest_email || '')}</span>
                </td>
                <td data-label="Stay">${UI.escapeHtml(guest.stay_number || '—')}</td>
                <td data-label="Room">${UI.escapeHtml(guest.room_number || '—')}</td>
                <td data-label="Comment" style="max-width:280px">
                  <span class="clamp-2">${UI.escapeHtml(item.guest_comment || '—')}</span>
                </td>
                <td data-label="Date">${UI.formatDate(item.feedback_date)}</td>
                <td data-label="Actions"><div class="table__actions">
                  <button class="btn btn--ghost btn--sm" data-view-feedback="${item.id}">View</button>
                </div></td>
              </tr>`;
            }).join('')}
          </tbody>
        </table>
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
              <div class="detail-item"><dt>Guest</dt><dd>${UI.escapeHtml(guest.guest_name || '—')}</dd></div>
              <div class="detail-item"><dt>Email</dt><dd>${UI.escapeHtml(guest.guest_email || '—')}</dd></div>
              <div class="detail-item"><dt>Stay</dt><dd>${UI.escapeHtml(guest.stay_number || '—')}</dd></div>
              <div class="detail-item"><dt>Room</dt><dd>${UI.escapeHtml(guest.room_number || '—')} (${UI.escapeHtml(guest.room_type || '—')})</dd></div>
              <div class="detail-item"><dt>Check-in</dt><dd>${UI.formatDate(guest.check_in_date)}</dd></div>
              <div class="detail-item"><dt>Check-out</dt><dd>${UI.formatDate(guest.check_out_date)}</dd></div>
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
