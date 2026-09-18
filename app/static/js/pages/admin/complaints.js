/* Admin complaint management.
   Verified backend behaviors used here:
     - GET  /api/complaints/list?status&priority&category_name&department&from_date&to_date
       (department filter only applies together with category_name — backend quirk;
        both are sent and the backend combines them.)
     - PUT  /api/complaints/assign?complaint_id — admin only, only for status "New"
       with no assigned staff; requires department_id + assigned_staff_id.
     - PUT  /api/complaints/update-status — transitions Assigned→In Progress→
       Resolved→Closed; resolving requires saved resolution notes.
     - PUT  /api/complaints/resolution-note — allowed while not closed.
   The backend has no staff-directory endpoint, so assignment asks for the
   staff member's numeric user ID (validated server-side: role must be "staff"). */

(function () {
  'use strict';

  const user = Auth.requireRole('admin');
  if (!user) return;

  const PAGE_SIZE = 8;
  let complaints = [];
  let page = 1;

  document.addEventListener('DOMContentLoaded', () => {
    UI.initNav();
    bindFilters();
    load();
  });

  function bindFilters() {
    const reload = UI.debounce(() => { page = 1; load(); });
    ['filter-status', 'filter-priority', 'filter-category', 'filter-department', 'filter-from', 'filter-to']
      .forEach((id) => document.getElementById(id).addEventListener('change', reload));
    document.getElementById('filter-search').addEventListener('input', UI.debounce(() => { page = 1; render(); }));
    document.getElementById('clear-filters').addEventListener('click', () => {
      ['filter-status', 'filter-priority', 'filter-category', 'filter-department', 'filter-from', 'filter-to', 'filter-search']
        .forEach((id) => { document.getElementById(id).value = ''; });
      page = 1;
      load();
    });
  }

  async function load() {
    const container = document.getElementById('complaints-container');
    container.innerHTML = '<div class="skeleton-block"></div><div class="skeleton-block" style="margin-top:12px"></div>';

    try {
      await loadReferenceData();

      const result = await API.complaints.list({
        status: document.getElementById('filter-status').value || undefined,
        priority: document.getElementById('filter-priority').value || undefined,
        category_name: document.getElementById('filter-category').value || undefined,
        department: document.getElementById('filter-department').value || undefined,
        from_date: document.getElementById('filter-from').value || undefined,
        to_date: document.getElementById('filter-to').value || undefined
      });
      complaints = ((result.data || {}).complaints) || [];
      render();
    } catch (err) {
      container.innerHTML = UI.errorState(err.message, { retry: true });
      container.querySelector('[data-retry]')?.addEventListener('click', load);
      UI.showToast(err.message, 'error');
    }
  }

  let referenceLoaded = false;
  async function loadReferenceData() {
    if (referenceLoaded) return;
    const [categoriesResult, departmentsResult] = await Promise.all([
      API.categories.list(), API.departments.list()
    ]);
    const categories = ((categoriesResult.data || {}).complaint_categories) || [];
    const departments = ((departmentsResult.data || {}).departments) || [];

    document.getElementById('filter-category').innerHTML =
      '<option value="">All categories</option>' +
      categories.map((c) => `<option value="${UI.escapeHtml(c.name)}">${UI.escapeHtml(c.name)}</option>`).join('');
    document.getElementById('filter-department').innerHTML =
      '<option value="">All departments</option>' +
      departments.map((d) => `<option value="${UI.escapeHtml(d.name)}">${UI.escapeHtml(d.name)}</option>`).join('');
    referenceLoaded = true;
  }

  function render() {
    const container = document.getElementById('complaints-container');
    const searchQuery = document.getElementById('filter-search').value.trim().toLowerCase();
    const visible = searchQuery ? complaints.filter((c) => {
      const haystack = [
        c.complaint_number, c.description,
        c.guest_details && c.guest_details.name,
        c.stay_details && c.stay_details.room_number
      ].filter(Boolean).join(' ').toLowerCase();
      return haystack.includes(searchQuery);
    }) : complaints;

    if (!visible.length) {
      container.innerHTML = UI.emptyState({
        icon: 'fa-list-check',
        title: 'No complaints found',
        message: complaints.length ? 'Nothing matches the current filters.' : 'No complaints have been submitted yet.'
      });
      return;
    }

    const total = visible.length;
    const pages = Math.max(1, Math.ceil(total / PAGE_SIZE));
    page = Math.min(page, pages);
    const slice = visible.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

    container.innerHTML = `
      <div class="muted" style="margin-bottom:10px; font-size:.85rem">${total} complaint${total === 1 ? '' : 's'}</div>
      <div class="table-wrap">
        <table class="table table-responsive-stack">
          <thead>
            <tr><th>Complaint</th><th>Guest</th><th>Category</th><th>Department</th><th>Priority</th><th>Status</th><th>SLA</th><th></th></tr>
          </thead>
          <tbody>
            ${slice.map((c) => `
              <tr>
                <td data-label="Complaint"><strong>${UI.escapeHtml(c.complaint_number)}</strong><br>
                  <span class="muted" style="font-size:.78rem">${UI.formatDate(c.created_at)}</span></td>
                <td data-label="Guest">${UI.escapeHtml(c.guest_details ? c.guest_details.name : '—')}</td>
                <td data-label="Category">${UI.escapeHtml(c.category ? c.category.name : '—')}</td>
                <td data-label="Department">${UI.escapeHtml((c.department && c.department.name) || '<span class="muted">Unassigned</span>')}</td>
                <td data-label="Priority">${UI.priorityBadge(c.priority)}</td>
                <td data-label="Status">${UI.statusBadge(c.status)}</td>
                <td data-label="SLA">${UI.slaBadge(c.sla_status)}</td>
                <td data-label="Actions"><div class="table__actions">
                  <button class="btn btn--primary btn--sm" data-open-complaint="${c.id}">
                    ${c.status === 'New' ? 'Assign' : 'Open'}
                  </button>
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
      const staff = complaint.assigned_staff || {};
      const transitions = window.APP_CONFIG.STATUS_TRANSITIONS[complaint.status] || [];
      const canAssign = complaint.status === 'New' && !complaint.assigned_staff;

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
              <div class="detail-item"><dt>Stay</dt><dd>${UI.escapeHtml(stay.stay_id || '—')} · Room ${UI.escapeHtml(stay.room_number || '—')}</dd></div>
              <div class="detail-item"><dt>Category</dt><dd>${UI.escapeHtml(complaint.category ? complaint.category.name : '—')}</dd></div>
              <div class="detail-item"><dt>Department</dt><dd>${UI.escapeHtml((complaint.department && complaint.department.name) || 'Unassigned')}</dd></div>
              <div class="detail-item"><dt>Assigned staff</dt><dd>${staff.name ? `${UI.escapeHtml(staff.name)} <span class="muted">(#${UI.escapeHtml(staff.id)})</span>` : '<span class="muted">Unassigned</span>'}</dd></div>
              <div class="detail-item"><dt>SLA due</dt><dd>${UI.formatDateTime(complaint.sla_due_at)} ${UI.slaBadge(complaint.sla_status)}</dd></div>
              <div class="detail-item"><dt>Created</dt><dd>${UI.formatDateTime(complaint.created_at)}</dd></div>
              <div class="detail-item"><dt>Updated</dt><dd>${UI.formatDateTime(complaint.updated_at)}</dd></div>
              ${complaint.resolved_at ? `<div class="detail-item"><dt>Resolved</dt><dd>${UI.formatDateTime(complaint.resolved_at)}</dd></div>` : ''}
              ${complaint.closed_at ? `<div class="detail-item"><dt>Closed</dt><dd>${UI.formatDateTime(complaint.closed_at)}</dd></div>` : ''}
            </dl>

            <h3 style="margin-top:16px">Description</h3>
            <p>${UI.escapeHtml(complaint.description)}</p>

            ${canAssign ? `
              <div class="card" style="box-shadow:none; padding:16px; margin-top:14px; border:1px solid var(--gold)">
                <h3><i class="fa-solid fa-user-plus" style="color:var(--gold-dark)"></i> Assign this complaint</h3>
                <div class="form-row">
                  <div class="form-field">
                    <label for="assign-department">Department *</label>
                    <select class="input" id="assign-department">
                      <option value="">Loading…</option>
                    </select>
                  </div>
                  <div class="form-field">
                    <label for="assign-staff">Staff member ID *</label>
                    <input class="input" id="assign-staff" type="number" min="1" placeholder="User ID (e.g. 5)">
                    <p class="hint">The backend has no staff directory API — enter the staff member's user ID. It is validated server-side.</p>
                  </div>
                </div>
                <button type="button" class="btn btn--gold" id="assign-button" data-loading-text="Assigning…">
                  <i class="fa-solid fa-paper-plane"></i> Assign complaint
                </button>
              </div>` : ''}

            ${!canAssign && !staff.name && complaint.department && complaint.department.name ? `
              <div class="alert alert--info" style="margin-top:12px">
                <i class="fa-solid fa-circle-info"></i>
                <span>Routed to <strong>${UI.escapeHtml(complaint.department.name)}</strong> — awaiting staff assignment via the assignment API.</span>
              </div>` : ''}

            <div class="form-field" style="margin-top:14px">
              <label for="resolution-notes">Resolution notes</label>
              <textarea class="input" id="resolution-notes" rows="3"
                placeholder="Describe what was done to resolve the complaint…"
                ${complaint.status === 'Closed' ? 'disabled' : ''}>${UI.escapeHtml(complaint.resolution_notes || '')}</textarea>
            </div>

            <div class="form-actions" style="flex-wrap:wrap">
              ${complaint.status !== 'Closed' ? `
                <button type="button" class="btn btn--ghost" id="save-notes" data-loading-text="Saving…">
                  <i class="fa-solid fa-floppy-disk"></i> Save notes
                </button>` : ''}
              ${transitions.map((next) => `
                <button type="button" class="btn ${next === 'Resolved' ? 'btn--primary' : 'btn--ghost'}"
                  data-transition="${next}" data-loading-text="Updating…">
                  <i class="fa-solid fa-arrow-right"></i> Mark ${next}
                </button>`).join('')}
              ${!transitions.length && complaint.status === 'Closed'
                ? '<span class="muted" style="align-self:center">This complaint is closed.</span>' : ''}
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

      // --- Assignment (admin only; PUT /api/complaints/assign) ---
      if (canAssign) {
        const departmentSelect = modal.querySelector('#assign-department');
        try {
          const departmentsResult = await API.departments.list();
          const departments = ((departmentsResult.data || {}).departments || []).filter((d) => d.is_active);
          departmentSelect.innerHTML = '<option value="">Select department…</option>' +
            departments.map((d) => `<option value="${d.id}">${UI.escapeHtml(d.name)}</option>`).join('');
        } catch (err) {
          departmentSelect.innerHTML = '<option value="">Unable to load departments</option>';
        }

        modal.querySelector('#assign-button').addEventListener('click', async (event) => {
          const departmentId = departmentSelect.value;
          const staffId = modal.querySelector('#assign-staff').value;
          let valid = true;
          UI.setFieldError(departmentSelect, null);
          UI.setFieldError(modal.querySelector('#assign-staff'), null);
          if (!departmentId) {
            UI.setFieldError(departmentSelect, 'Department is required.');
            valid = false;
          }
          if (!staffId) {
            UI.setFieldError(modal.querySelector('#assign-staff'), 'Staff member is required.');
            valid = false;
          }
          if (!valid) return;

          const confirmed = await UI.confirmDialog({
            title: 'Assign complaint',
            message: `Assign ${complaint.complaint_number} to staff #${staffId} in the selected department?`,
            confirmText: 'Assign'
          });
          if (!confirmed) return;

          const button = event.currentTarget;
          const restore = UI.setButtonLoading(button, true);
          try {
            const assignResult = await API.complaints.assign(complaint.id, {
              department_id: Number(departmentId),
              assigned_staff_id: Number(staffId)
            });
            UI.showToast(assignResult.message || 'Complaint assigned successfully.', 'success');
            close();
            load();
          } catch (err) {
            UI.showToast(err.message, 'error');
          } finally {
            UI.setButtonLoading(button, false);
            restore && restore();
          }
        });
      }

      // --- Resolution notes (PUT /api/complaints/resolution-note) ---
      const saveNotes = modal.querySelector('#save-notes');
      if (saveNotes) {
        saveNotes.addEventListener('click', async () => {
          const notes = modal.querySelector('#resolution-notes').value.trim();
          if (!notes) {
            UI.showToast('Resolution notes cannot be empty.', 'warning');
            return;
          }
          const restore = UI.setButtonLoading(saveNotes, true);
          try {
            const updateResult = await API.complaints.addResolution(complaint.id, notes);
            UI.showToast(updateResult.message || 'Resolution notes saved.', 'success');
            close();
            load();
          } catch (err) {
            UI.showToast(err.message, 'error');
          } finally {
            UI.setButtonLoading(saveNotes, false);
            restore && restore();
          }
        });
      }

      // --- Status transitions (PUT /api/complaints/update-status) ---
      modal.querySelectorAll('[data-transition]').forEach((button) => {
        button.addEventListener('click', async () => {
          const nextStatus = button.getAttribute('data-transition');
          const typedNotes = modal.querySelector('#resolution-notes').value.trim();

          if (nextStatus === 'Resolved' && !(complaint.resolution_notes || typedNotes)) {
            UI.showToast('Add resolution notes before resolving this complaint.', 'warning');
            return;
          }
          if (nextStatus === 'Resolved' && !complaint.resolution_notes) {
            try {
              await API.complaints.addResolution(complaint.id, typedNotes);
            } catch (err) {
              UI.showToast(err.message, 'error');
              return;
            }
          }

          const confirmed = await UI.confirmDialog({
            title: `Mark as ${nextStatus}`,
            message: `Move ${complaint.complaint_number} to "${nextStatus}"?`,
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
