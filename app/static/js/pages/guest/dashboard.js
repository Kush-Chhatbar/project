/* Guest dashboard.
   The backend has no aggregate "my stats" endpoint, so the small counters are
   derived client-side from the guest's real list data (all complaints ever
   returned by /api/complaints/list are the guest's own — the service scopes
   the query by the JWT identity). */

(function () {
  'use strict';

  const user = Auth.requireRole('guest');
  if (!user) return;

  document.addEventListener('DOMContentLoaded', init);

  async function init() {
    document.getElementById('welcome-heading').textContent = `Welcome, ${user.name || 'Guest'}`;
    UI.initNav();
    renderStay(user.stay);

    UI.showLoading('Loading your dashboard…');
    try {
      const [complaintsResult, feedbackResult] = await Promise.all([
        API.complaints.list(),
        API.feedback.list().catch(() => null)
      ]);

      const complaints = (complaintsResult.data && complaintsResult.data.complaints) || [];
      renderStats(complaints);
      renderRecentComplaints(complaints.slice(0, 4));

      if (feedbackResult && feedbackResult.data) {
        const feedbacks = feedbackResult.data.feedbacks || feedbackResult.data || [];
        const list = Array.isArray(feedbacks) ? feedbacks : (feedbacks.feedbacks || []);
        if (list.length) {
          UI.showToast(`You have submitted ${list.length} piece${list.length === 1 ? '' : 's'} of feedback. Thank you!`, 'info');
        }
      }
    } catch (err) {
      UI.showToast(err.message, 'error');
      document.getElementById('recent-complaints').innerHTML = UI.errorState(err.message, { retry: true });
      document.querySelector('[data-retry]')?.addEventListener('click', init);
    } finally {
      UI.hideLoading();
    }
  }

  function renderStats(complaints) {
    const counts = {
      total: complaints.length,
      open: complaints.filter((c) => ['New', 'Assigned', 'In Progress'].includes(c.status)).length,
      resolved: complaints.filter((c) => ['Resolved', 'Closed'].includes(c.status)).length
    };

    document.getElementById('guest-stats').setAttribute('aria-busy', 'false');
    document.getElementById('guest-stats').innerHTML = `
      <div class="stat-card">
        <span class="stat-card__icon stat-card__icon--navy"><i class="fa-solid fa-list-check"></i></span>
        <div><div class="stat-card__value">${counts.total}</div><div class="stat-card__label">Total complaints</div></div>
      </div>
      <div class="stat-card">
        <span class="stat-card__icon stat-card__icon--warning"><i class="fa-solid fa-hourglass-half"></i></span>
        <div><div class="stat-card__value">${counts.open}</div><div class="stat-card__label">Open complaints</div></div>
      </div>
      <div class="stat-card">
        <span class="stat-card__icon stat-card__icon--success"><i class="fa-solid fa-circle-check"></i></span>
        <div><div class="stat-card__value">${counts.resolved}</div><div class="stat-card__label">Resolved complaints</div></div>
      </div>`;
  }

  function renderStay(stay) {
    const container = document.getElementById('stay-details');
    if (!stay) {
      container.innerHTML = '<p class="muted">Stay information is not available.</p>';
      return;
    }
    container.innerHTML = `
      <div class="detail-item"><dt>Stay ID</dt><dd>${UI.escapeHtml(stay.stay_id)}</dd></div>
      <div class="detail-item"><dt>Room</dt><dd>${UI.escapeHtml(stay.room_number)} · ${UI.escapeHtml(stay.room_type)}</dd></div>
      <div class="detail-item"><dt>Check-in</dt><dd>${UI.formatDate(stay.check_in_date)}</dd></div>
      <div class="detail-item"><dt>Check-out</dt><dd>${UI.formatDate(stay.check_out_date)}</dd></div>`;
  }

  function renderRecentComplaints(complaints) {
    const container = document.getElementById('recent-complaints');
    if (!complaints.length) {
      container.innerHTML = UI.emptyState({
        icon: 'fa-comment-dots',
        title: 'No complaints yet',
        message: 'If anything is not perfect during your stay, let us know and we will make it right.'
      });
      return;
    }
    container.innerHTML = `
      <div class="table-wrap">
        <table class="table">
          <thead><tr><th>Complaint</th><th>Category</th><th>Priority</th><th>Status</th><th>Created</th></tr></thead>
          <tbody>
            ${complaints.map((c) => `
              <tr>
                <td><strong>${UI.escapeHtml(c.complaint_number)}</strong></td>
                <td>${UI.escapeHtml(c.category ? c.category.name : '—')}</td>
                <td>${UI.priorityBadge(c.priority)}</td>
                <td>${UI.statusBadge(c.status)}</td>
                <td>${UI.formatDate(c.created_at)}</td>
              </tr>`).join('')}
          </tbody>
        </table>
      </div>`;
  }
})();
