/* Staff dashboard.
   There is no dedicated staff statistics endpoint in the backend, so the
   counters are computed from GET /api/complaints/list — which the
   ComplaintService scopes to the authenticated staff member's assignments.
   Nothing is fabricated; empty data renders genuine empty states. */

(function () {
  'use strict';

  const user = Auth.requireRole('staff');
  if (!user) return;

  document.addEventListener('DOMContentLoaded', init);

  async function init() {
    document.getElementById('welcome-heading').textContent = `Welcome, ${user.name || 'Staff'}`;
    UI.initNav();

    UI.showLoading('Loading your assignments…');
    try {
      const result = await API.complaints.list();
      const complaints = ((result.data || {}).complaints) || [];
      renderStats(complaints);
      renderAttention(complaints);
    } catch (err) {
      UI.showToast(err.message, 'error');
      document.getElementById('attention-list').innerHTML = UI.errorState(err.message, { retry: true });
      document.querySelector('[data-retry]')?.addEventListener('click', init);
    } finally {
      UI.hideLoading();
    }
  }

  function renderStats(complaints) {
    const assigned = complaints.filter((c) => c.status === 'Assigned').length;
    const inProgress = complaints.filter((c) => c.status === 'In Progress').length;
    const resolved = complaints.filter((c) => c.status === 'Resolved' || c.status === 'Closed').length;
    const breached = complaints.filter((c) => c.sla_status === 'Breached' &&
      !['Resolved', 'Closed'].includes(c.status)).length;

    document.getElementById('staff-stats').setAttribute('aria-busy', 'false');
    document.getElementById('staff-stats').innerHTML = `
      <div class="stat-card">
        <span class="stat-card__icon stat-card__icon--navy"><i class="fa-solid fa-inbox"></i></span>
        <div><div class="stat-card__value">${complaints.length}</div><div class="stat-card__label">Assigned to me</div></div>
      </div>
      <div class="stat-card">
        <span class="stat-card__icon stat-card__icon--info"><i class="fa-solid fa-flag"></i></span>
        <div><div class="stat-card__value">${assigned}</div><div class="stat-card__label">Newly assigned</div></div>
      </div>
      <div class="stat-card">
        <span class="stat-card__icon stat-card__icon--warning"><i class="fa-solid fa-person-digging"></i></span>
        <div><div class="stat-card__value">${inProgress}</div><div class="stat-card__label">In progress</div></div>
      </div>
      <div class="stat-card">
        <span class="stat-card__icon stat-card__icon--success"><i class="fa-solid fa-circle-check"></i></span>
        <div><div class="stat-card__value">${resolved}</div><div class="stat-card__label">Resolved / closed</div></div>
      </div>
      ${breached ? `
      <div class="stat-card">
        <span class="stat-card__icon stat-card__icon--danger"><i class="fa-solid fa-triangle-exclamation"></i></span>
        <div><div class="stat-card__value">${breached}</div><div class="stat-card__label">SLA breached</div></div>
      </div>` : ''}`;
  }

  function renderAttention(complaints) {
    const container = document.getElementById('attention-list');
    const open = complaints
      .filter((c) => ['Assigned', 'In Progress'].includes(c.status))
      .sort((a, b) => new Date(a.sla_due_at || 0) - new Date(b.sla_due_at || 0))
      .slice(0, 5);

    if (!open.length) {
      container.innerHTML = UI.emptyState({
        icon: 'fa-mug-hot',
        title: 'All clear!',
        message: complaints.length
          ? 'You have no open complaints right now. Nicely done.'
          : 'No complaints have been assigned to you yet.'
      });
      return;
    }

    container.innerHTML = `
      <div class="table-wrap">
        <table class="table">
          <thead><tr><th>Complaint</th><th>Category</th><th>Priority</th><th>Status</th><th>SLA due</th><th></th></tr></thead>
          <tbody>
            ${open.map((c) => `
              <tr>
                <td><strong>${UI.escapeHtml(c.complaint_number)}</strong></td>
                <td>${UI.escapeHtml(c.category ? c.category.name : '—')}</td>
                <td>${UI.priorityBadge(c.priority)}</td>
                <td>${UI.statusBadge(c.status)}</td>
                <td>${UI.slaBadge(c.sla_status)} <span class="muted" style="font-size:.8rem">${UI.formatDateTime(c.sla_due_at)}</span></td>
                <td class="table__actions">
                  <a class="btn btn--ghost btn--sm" href="/staff/complaints?focus=${c.id}">Open</a>
                </td>
              </tr>`).join('')}
          </tbody>
        </table>
      </div>`;
  }
})();
