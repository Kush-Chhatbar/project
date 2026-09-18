/* Staff "Assigned Complaints".
   Status updates go through PUT /api/complaints/update-status, which the
   backend restricts to admin/staff and validates against strict transitions:
     Assigned -> In Progress -> Resolved -> Closed
   Resolving requires resolution notes to already be saved (PUT
   /api/complaints/resolution-note) — the UI disables "Resolve" until notes
   exist, mirroring the backend rule. Assignment is admin-only and is NOT
   offered to staff. */

(function () {
  'use strict';

  const user = Auth.requireRole('staff');
  if (!user) return;

  const PAGE_SIZE = 8;
  let complaints = [];
  let page = 1;
  let focusId = null;

  document.addEventListener('DOMContentLoaded', () => {
    UI.initNav();
    focusId = new URLSearchParams(window.location.search).get('focus');

    bindFilters();
    load();
  });

  function bindFilters() {
    const apply = UI.debounce(() => { page = 1; load(); });
    ['filter-status', 'filter-priority', 'filter-category'].forEach((id) => {
      document.getElementById(id).addEventListener('change', apply);
    });
    document.getElementById('clear-filters').addEventListener('click', () => {
      ['filter-status', 'filter-priority', 'filter-category'].forEach((id) => {
        document.getElementById(id).value = '';
      });
      page = 1;
      load();
    });
  }

  async function load() {
    const container = document.getElementById('complaints-container');
    container.innerHTML = '<div class="skeleton-block"></div><div class="skeleton-block" style="margin-top:12px"></div>';

    try {
      // Category filter uses the API's category_name (ilike) parameter.
      if (!document.querySelector('#filter-category option')) {
        try {
          const categoriesResult = await API.categories.list();
          const categories = ((categoriesResult.data || {}).complaint_categories || []);
          document.getElementById('filter-category').innerHTML =
            '<option value="">All categories</option>' +
            categories.map((c) => `<option value="${UI.escapeHtml(c.name)}">${UI.escapeHtml(c.name)}</option>`).join('');
        } catch (e) { /* filter stays empty if categories can't load */ }
      }

      const result = await API.complaints.list({
        status: document.getElementById('filter-status').value || undefined,
        priority: document.getElementById('filter-priority').value || undefined,
        category_name: document.getElementById('filter-category').value || undefined
      });
      complaints = ((result.data || {}).complaints) || [];
      render();

      if (focusId) {
        const target = complaints.find((c) => String(c.id) === String(focusId));
        if (target) openComplaint(target.id);
        focusId = null;
      }
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
        icon: 'fa-inbox',
        title: 'No complaints match',
        message: 'Try changing the filters — or enjoy the quiet while it lasts.'
      });
      return;
    }

    const total = complaints.length;
    const pages = Math.max(1, Math.ceil(total / PAGE_SIZE));
    page = Math.min(page, pages);
    const slice = complaints.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

    container.innerHTML = `
      <div class="muted" style="margin-bottom:10px; font-size:.85rem">${total} complaint${total === 1 ? '' : 's'}</div>
      <div class="table-wrap">
        <table class="table table-responsive-stack">
          <thead>
            <tr><th>Complaint</th><th>Guest</th><th>Category</th><th>Priority</th><th>Status</th><th>SLA</th><th></th></tr>
          </thead>
          <tbody>
            ${slice.map((c) => `
              <tr>
                <td data-label="Complaint"><strong>${UI.escapeHtml(c.complaint_number)}</strong></td>
                <td data-label="Guest">${UI.escapeHtml(c.guest_details ? c.guest_details.name : '—')}</td>
                <td data-label="Category">${UI.escapeHtml(c.category ? c.category.name : '—')}</td>
                <td data-label="Priority">${UI.priorityBadge(c.priority)}</td>
                <td data-label="Status">${UI.statusBadge(c.status)}</td>
                <td data-label="SLA">${UI.slaBadge(c.sla_status)}</td>
                <td data-label="Actions"><div class="table__actions">
                  <button class="btn btn--primary btn--sm" data-open-complaint="${c.id}">Open</button>
                </div></td>
              </tr>`).join('')}
          </tbody>
        </table>
      </div>`;

    const pagination = document.createElement('div');
    pagination.className = 'pagination';
    container.appendChild(pagination);
    UI.renderPagination(pagination, { page, pageSize: PAGE_SIZE, total, onPageChange: (p) => { page = p; render(); } });

    container.querySelectorAll('[data-open-complaint]').forEach((button) => {
      button.addEventListener('click', () => openComplaint(button.getAttribute('data-open-complaint')));
    });
  }

  async function openComplaint(complaintId) {
    try {
      const result = await API.complaints.show(complaintId);
      const complaint = (result.data || {}).complaint || {};
      const guest = complaint.guest_details || {};
      const stay = complaint.stay_details || {};
      const transitions = window.APP_CONFIG.STATUS_TRANSITIONS[complaint.status] || [];

      const modal = document.createElement('div');
      modal.className = 'modal';
      modal.setAttribute('aria-hidden', 'true');
      modal.innerHTML = `
        <div class="modal__panel modal__panel--lg" role="dialog" aria-modal="true">
          <div class="modal__header">
            <h3>${UI.escapeHtml(complaint.complaint_number)} ${UI.statusBadge(complaint.status)} ${UI.priorityBadge(complaint.priority)}</h3>
            <button type="button" class="modal__close" data-close-modal aria-label="Close"><i class="fa-solid fa-xmark"></i></button>
          </div>
          <div class="modal__body">
            <dl class="detail-grid">
              <div class="detail-item"><dt>Guest</dt><dd>${UI.escapeHtml(guest.name || '—')}</dd></div>
              <div class="detail-item"><dt>Contact</dt><dd>${UI.escapeHtml(guest.email || '—')}</dd></div>
              <div class="detail-item"><dt>Room</dt><dd>${UI.escapeHtml(stay.room_number || '—')} · ${UI.escapeHtml(stay.room_type || '—')}</dd></div>
              <div class="detail-item"><dt>Category</dt><dd>${UI.escapeHtml(complaint.category ? complaint.category.name : '—')}</dd></div>
              <div class="detail-item"><dt>Department</dt><dd>${UI.escapeHtml((complaint.department && complaint.department.name) || '—')}</dd></div>
              <div class="detail-item"><dt>SLA due</dt><dd>${UI.formatDateTime(complaint.sla_due_at)} ${UI.slaBadge(complaint.sla_status)}</dd></div>
              <div class="detail-item"><dt>Created</dt><dd>${UI.formatDateTime(complaint.created_at)}</dd></div>
              <div class="detail-item"><dt>Updated</dt><dd>${UI.formatDateTime(complaint.updated_at)}</dd></div>
            </dl>

            <h3 style="margin-top:16px">Description</h3>
            <p>${UI.escapeHtml(complaint.description)}</p>

            <div class="form-field" style="margin-top:14px">
              <label for="resolution-notes">Resolution notes</label>
              <textarea class="input" id="resolution-notes" rows="3"
                placeholder="Describe what was done to resolve the complaint…">${UI.escapeHtml(complaint.resolution_notes || '')}</textarea>
              <p class="hint">Saving notes is required before the complaint can be resolved.</p>
            </div>

            <div class="form-actions" style="flex-wrap:wrap">
              <button type="button" class="btn btn--ghost" id="save-notes" data-loading-text="Saving…">
                <i class="fa-solid fa-floppy-disk"></i> Save notes
              </button>
              ${transitions.map((next) => `
                <button type="button" class="btn ${next === 'Resolved' ? 'btn--primary' : 'btn--ghost'}"
                  data-transition="${next}" data-loading-text="Updating…">
                  <i class="fa-solid fa-arrow-right"></i> Mark ${next}
                </button>`).join('')}
              ${!transitions.length ? '<span class="muted" style="align-self:center">No further actions — this complaint is closed.</span>' : ''}
            </div>
          </div>
          <div class="modal__footer">
            <button type="button" class="btn btn--ghost" data-close-modal>Close</button>
          </div>
        </div>`;
      document.body.appendChild(modal);
      UI.showModal(modal);

      const close = () => {
        UI.hideModal(modal);
        setTimeout(() => modal.remove(), 250);
      };
      modal.addEventListener('click', (event) => {
        if (event.target === modal || event.target.closest('[data-close-modal]')) close();
      });

      // Resolution notes (PUT /api/complaints/resolution-note)
      modal.querySelector('#save-notes').addEventListener('click', async (event) => {
        const notes = modal.querySelector('#resolution-notes').value.trim();
        if (!notes) {
          UI.showToast('Resolution notes cannot be empty.', 'warning');
          return;
        }
        const button = event.currentTarget;
        const restore = UI.setButtonLoading(button, true);
        try {
          const updateResult = await API.complaints.addResolution(complaint.id, notes);
          UI.showToast(updateResult.message || 'Resolution notes saved.', 'success');
          close();
          load(); // refresh list + badges
        } catch (err) {
          UI.showToast(err.message, 'error');
        } finally {
          UI.setButtonLoading(button, false);
          restore && restore();
        }
      });

      // Permitted status transitions (PUT /api/complaints/update-status)
      modal.querySelectorAll('[data-transition]').forEach((button) => {
        button.addEventListener('click', async () => {
          const nextStatus = button.getAttribute('data-transition');
          if (nextStatus === 'Resolved' && !(complaint.resolution_notes || modal.querySelector('#resolution-notes').value.trim())) {
            UI.showToast('Add resolution notes before resolving this complaint.', 'warning');
            return;
          }

          if (nextStatus === 'Resolved' && !(complaint.resolution_notes)) {
            // Save the freshly typed notes first, then resolve.
            try {
              const typedNotes = modal.querySelector('#resolution-notes').value.trim();
              await API.complaints.addResolution(complaint.id, typedNotes);
            } catch (err) {
              UI.showToast(err.message, 'error');
              return;
            }
          }

          const confirmed = await UI.confirmDialog({
            title: `Mark as ${nextStatus}`,
            message: `Move ${complaint.complaint_number} to "${nextStatus}"? This follows the required workflow.`,
            confirmText: `Mark ${nextStatus}`
          });
          if (!confirmed) return;

          const restore = UI.setButtonLoading(button, true);
          try {
            const updateResult = await API.complaints.updateStatus(complaint.id, nextStatus);
            UI.showToast(updateResult.message || `Complaint marked ${nextStatus}.`, 'success');
            close();
            load();
          } catch (err) {
            UI.showToast(err.message, 'error');
          } finally {
            UI.setButtonLoading(button, false);
            restore && restore();
          }
        });
      });
    } catch (err) {
      UI.showToast(err.message, 'error');
    }
  }
})();
