/* Guest "My Complaints" — GET /api/complaints/list?status=...
   The endpoint returns only complaints belonging to the authenticated guest.
   Guests see status and (per the service) the assigned department name and
   resolution notes — but never assignment controls, which are admin-only
   (PUT /api/complaints/assign is @role_required("admin")). */

(function () {
  'use strict';

  const user = Auth.requireRole('guest');
  if (!user) return;

  const PAGE_SIZE = 6;
  let complaints = [];
  let page = 1;

  document.addEventListener('DOMContentLoaded', () => {
    UI.initNav();
    document.getElementById('filter-status').addEventListener('change', () => { page = 1; load(); });
    document.getElementById('clear-filters').addEventListener('click', () => {
      document.getElementById('filter-status').value = '';
      page = 1;
      load();
    });
    load();
  });

  async function load() {
    const container = document.getElementById('complaints-container');
    container.innerHTML = '<div class="skeleton-block"></div><div class="skeleton-block" style="margin-top:12px"></div>';

    try {
      const status = document.getElementById('filter-status').value;
      const result = await API.complaints.list({ status: status || undefined });
      complaints = ((result.data || {}).complaints) || [];
      render();
    } catch (err) {
      container.innerHTML = UI.errorState(err.message, { retry: true });
      container.querySelector('[data-retry]')?.addEventListener('click', load);
      UI.showToast(err.message, 'error');
    }
  }

  function render() {
    const container = document.getElementById('complaints-container');
    if (!complaints.length) {
      container.innerHTML = UI.emptyState({
        icon: 'fa-list-check',
        title: 'No complaints found',
        message: 'Nothing here — enjoy your stay! If anything comes up, raise a complaint and we will handle it.'
      });
      return;
    }

    const total = complaints.length;
    const pages = Math.max(1, Math.ceil(total / PAGE_SIZE));
    page = Math.min(page, pages);
    const slice = complaints.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

    container.innerHTML = `
      <div class="muted" style="margin-bottom:10px; font-size:.85rem">${total} complaint${total === 1 ? '' : 's'}</div>
      ${slice.map((complaint) => `
        <div class="card" style="margin-top:12px">
          <div class="card__header" style="margin-bottom:10px">
            <div style="display:flex; align-items:center; gap:10px; flex-wrap:wrap">
              <strong>${UI.escapeHtml(complaint.complaint_number)}</strong>
              ${UI.statusBadge(complaint.status)}
              ${UI.priorityBadge(complaint.priority)}
            </div>
            <span class="muted" style="font-size:.82rem">Created ${UI.formatDateTime(complaint.created_at)}</span>
          </div>
          <p style="margin-bottom:10px">${UI.escapeHtml(complaint.description)}</p>
          <div class="detail-grid" style="grid-template-columns:repeat(auto-fit,minmax(150px,1fr))">
            <div class="detail-item" style="border:none;padding:2px 0"><dt>Category</dt><dd>${UI.escapeHtml(complaint.category ? complaint.category.name : '—')}</dd></div>
            <div class="detail-item" style="border:none;padding:2px 0"><dt>Department</dt><dd>${UI.escapeHtml((complaint.department && complaint.department.name) || 'Not assigned yet')}</dd></div>
            <div class="detail-item" style="border:none;padding:2px 0"><dt>SLA</dt><dd>${UI.slaBadge(complaint.sla_status)}</dd></div>
            <div class="detail-item" style="border:none;padding:2px 0"><dt>Last update</dt><dd>${UI.formatDateTime(complaint.updated_at)}</dd></div>
          </div>
          ${complaint.resolution_notes ? `
            <div class="alert alert--info" style="margin-top:10px; margin-bottom:0">
              <i class="fa-solid fa-wrench"></i>
              <span><strong>Resolution:</strong> ${UI.escapeHtml(complaint.resolution_notes)}</span>
            </div>` : ''}
          <div style="margin-top:10px">
            <button class="btn btn--ghost btn--sm" data-view-complaint="${complaint.id}">
              <i class="fa-regular fa-eye"></i> View details
            </button>
          </div>
        </div>`).join('')}`;

    const pagination = document.createElement('div');
    pagination.className = 'pagination';
    container.appendChild(pagination);
    UI.renderPagination(pagination, { page, pageSize: PAGE_SIZE, total, onPageChange: (p) => { page = p; render(); } });

    container.querySelectorAll('[data-view-complaint]').forEach((button) => {
      button.addEventListener('click', () => viewComplaint(button.getAttribute('data-view-complaint')));
    });
  }

  async function viewComplaint(complaintId) {
    try {
      const result = await API.complaints.show(complaintId);
      const complaint = (result.data || {}).complaint || {};
      const stay = complaint.stay_details || {};

      const modal = document.createElement('div');
      modal.className = 'modal';
      modal.setAttribute('aria-hidden', 'true');
      modal.innerHTML = `
        <div class="modal__panel" role="dialog" aria-modal="true">
          <div class="modal__header">
            <h3>${UI.escapeHtml(complaint.complaint_number)} ${UI.statusBadge(complaint.status)}</h3>
            <button type="button" class="modal__close" data-close-modal aria-label="Close"><i class="fa-solid fa-xmark"></i></button>
          </div>
          <div class="modal__body">
            <dl class="detail-grid">
              <div class="detail-item"><dt>Category</dt><dd>${UI.escapeHtml(complaint.category ? complaint.category.name : '—')}</dd></div>
              <div class="detail-item"><dt>Priority</dt><dd>${UI.priorityBadge(complaint.priority)}</dd></div>
              <div class="detail-item"><dt>Department</dt><dd>${UI.escapeHtml((complaint.department && complaint.department.name) || 'Not assigned')}</dd></div>
              <div class="detail-item"><dt>SLA due</dt><dd>${UI.formatDateTime(complaint.sla_due_at)}</dd></div>
              <div class="detail-item"><dt>Created</dt><dd>${UI.formatDateTime(complaint.created_at)}</dd></div>
              <div class="detail-item"><dt>Updated</dt><dd>${UI.formatDateTime(complaint.updated_at)}</dd></div>
              <div class="detail-item"><dt>Stay</dt><dd>${UI.escapeHtml(stay.stay_id || '—')} · Room ${UI.escapeHtml(stay.room_number || '—')}</dd></div>
            </dl>
            <h3 style="margin-top:14px">Description</h3>
            <p>${UI.escapeHtml(complaint.description)}</p>
            <h3 style="margin-top:14px">Resolution</h3>
            <p>${complaint.resolution_notes ? UI.escapeHtml(complaint.resolution_notes) : '<span class="muted">Not resolved yet.</span>'}</p>
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
