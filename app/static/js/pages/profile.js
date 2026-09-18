/* Profile page — GET /api/auth/me for staff & admin.
   Guests: the backend has no guest profile endpoint (/api/guest only exposes
   login), so the guest's details saved at login are displayed. */

(function () {
  'use strict';

  const user = Auth.requireRole(['guest', 'staff', 'admin']);
  if (!user) return;

  document.addEventListener('DOMContentLoaded', () => {
    UI.initNav();
    if (user.role === 'guest') {
      renderGuest(user);
    } else {
      loadStaffProfile();
    }
  });

  function roleLabel(role) {
    return { guest: 'Guest', staff: 'Staff Member', admin: 'Administrator' }[role] || role;
  }

  function item(label, value) {
    return `<div class="detail-item"><dt>${UI.escapeHtml(label)}</dt><dd>${value}</dd></div>`;
  }

  async function loadStaffProfile() {
    const container = document.getElementById('profile-content');
    try {
      const result = await API.auth.me();
      const fresh = ((result.data || {}).user) || {};
      // Keep the stored session in sync with the backend's response.
      Auth.saveSession(Auth.getToken(), { ...user, ...fresh });

      container.innerHTML = `
        <div style="display:flex; align-items:center; gap:14px; margin-bottom:18px">
          <span class="avatar" style="width:56px; height:56px; flex-basis:56px; font-size:1.1rem">
            ${UI.escapeHtml((fresh.name || '?').split(/\s+/).map((p) => p[0]).slice(0, 2).join(''))}
          </span>
          <div>
            <h2 style="margin:0">${UI.escapeHtml(fresh.name)}</h2>
            <span class="badge badge--new">${UI.escapeHtml(roleLabel(fresh.role))}</span>
          </div>
        </div>
        <dl class="detail-grid" style="grid-template-columns:1fr 1fr">
          ${item('User ID', UI.escapeHtml(fresh.id))}
          ${item('Email', UI.escapeHtml(fresh.email))}
          ${item('Role', UI.escapeHtml(roleLabel(fresh.role)))}
          ${item('Department ID', fresh.department != null ? UI.escapeHtml(fresh.department) : '<span class="muted">Not assigned</span>')}
        </dl>`;
    } catch (err) {
      container.innerHTML = UI.errorState(err.message, { retry: true });
      container.querySelector('[data-retry]')?.addEventListener('click', loadStaffProfile);
      UI.showToast(err.message, 'error');
    }
  }

  function renderGuest(sessionUser) {
    const container = document.getElementById('profile-content');
    const stay = sessionUser.stay || {};
    container.innerHTML = `
      <div style="display:flex; align-items:center; gap:14px; margin-bottom:18px">
        <span class="avatar" style="width:56px; height:56px; flex-basis:56px; font-size:1.1rem">
          ${UI.escapeHtml((sessionUser.name || '?').split(/\s+/).map((p) => p[0]).slice(0, 2).join(''))}
        </span>
        <div>
          <h2 style="margin:0">${UI.escapeHtml(sessionUser.name)}</h2>
          <span class="badge badge--assigned">Guest</span>
        </div>
      </div>
      <dl class="detail-grid" style="grid-template-columns:1fr 1fr">
        ${item('Guest ID', UI.escapeHtml(sessionUser.id))}
        ${item('Email', UI.escapeHtml(sessionUser.email))}
        ${item('Stay ID', UI.escapeHtml(stay.stay_id || '—'))}
        ${item('Room', stay.room_number ? `${UI.escapeHtml(stay.room_number)} (${UI.escapeHtml(stay.room_type || '')})` : '—')}
        ${item('Check-in', UI.formatDate(stay.check_in_date))}
        ${item('Check-out', UI.formatDate(stay.check_out_date))}
      </dl>`;
  }
})();
