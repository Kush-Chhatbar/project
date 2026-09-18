/* ==========================================================================
   Shared layout chrome: topbar + sidebar + footer, personalized per role.
   Loaded on every authenticated page via data-layout="guest|staff|admin".
   ========================================================================== */

(function () {
  'use strict';

  const MENUS = {
    guest: [
      { href: '/guest/dashboard', icon: 'fa-house', label: 'Dashboard' },
      { href: '/guest/feedback', icon: 'fa-star', label: 'Submit Feedback' },
      { href: '/guest/my-feedback', icon: 'fa-comment-dots', label: 'My Feedback' },
      { href: '/guest/complaints', icon: 'fa-circle-exclamation', label: 'Submit Complaint' },
      { href: '/guest/my-complaints', icon: 'fa-list-check', label: 'My Complaints' },
      { href: '/profile', icon: 'fa-user', label: 'Profile' }
    ],
    staff: [
      { href: '/staff/dashboard', icon: 'fa-gauge-high', label: 'Dashboard' },
      { href: '/staff/complaints', icon: 'fa-list-check', label: 'Assigned Complaints' },
      { href: '/profile', icon: 'fa-user', label: 'Profile' }
    ],
    admin: [
      { href: '/admin/dashboard', icon: 'fa-chart-pie', label: 'Dashboard' },
      { href: '/admin/feedbacks', icon: 'fa-star', label: 'Feedback' },
      { href: '/admin/complaints', icon: 'fa-list-check', label: 'Complaints' },
      { href: '/profile', icon: 'fa-user', label: 'Profile' }
    ]
  };

  const ROLE_LABELS = { guest: 'Guest', staff: 'Staff', admin: 'Administrator' };

  function initials(name) {
    return (name || '?')
      .split(/\s+/)
      .map((part) => part.charAt(0).toUpperCase())
      .slice(0, 2)
      .join('');
  }

  function renderLayout(role) {
    const layout = document.querySelector('[data-layout]');
    if (!layout) return;
    const user = window.Auth.getUser() || {};
    const menu = MENUS[role] || [];
    const currentPath = window.location.pathname;

    // Capture the page's declared content BEFORE replacing the layout,
    // so it can be re-inserted into the rendered shell.
    const originalContent = Array.from(layout.childNodes);

    const navLinks = menu.map((item) => `
      <a href="${item.href}" class="sidebar__link ${currentPath === item.href ? 'is-active' : ''}">
        <i class="fa-solid ${item.icon}"></i><span>${item.label}</span>
      </a>`).join('');

    const brandHref = window.Auth.dashboardForRole(role);

    layout.innerHTML = `
      <div class="app-shell">
        <aside class="sidebar" id="sidebar">
          <div class="sidebar__brand">
            <a href="${brandHref}" class="brand">
              <span class="brand__mark"><i class="fa-solid fa-hotel"></i></span>
              <span class="brand__text">Grandeur&nbsp;Suites</span>
            </a>
          </div>
          <nav class="sidebar__nav" aria-label="Main navigation">${navLinks}</nav>
          <div class="sidebar__footer">
            <div class="sidebar__user">
              <span class="avatar">${UI.escapeHtml(initials(user.name))}</span>
              <span class="sidebar__user-meta">
                <span class="sidebar__user-name">${UI.escapeHtml(user.name || '')}</span>
                <span class="sidebar__user-role">${UI.escapeHtml(ROLE_LABELS[role] || user.role || '')}</span>
              </span>
            </div>
            <button type="button" class="btn btn--ghost btn--sm btn--block" data-logout>
              <i class="fa-solid fa-right-from-bracket"></i> Sign out
            </button>
          </div>
        </aside>

        <div class="app-main">
          <header class="topbar">
            <button type="button" class="topbar__burger" data-sidebar-toggle aria-label="Toggle navigation">
              <i class="fa-solid fa-bars"></i>
            </button>
            <span class="topbar__title">${UI.escapeHtml(ROLE_LABELS[role] || '')} Portal</span>
            <span class="topbar__spacer"></span>
            <span class="topbar__user">
              <span class="avatar avatar--sm">${UI.escapeHtml(initials(user.name))}</span>
              <span class="topbar__user-name">${UI.escapeHtml(user.name || '')}</span>
            </span>
          </header>
          <main class="page">
            <div data-page-content></div>
          </main>
          <footer class="footer">
            <span>© ${new Date().getFullYear()} Grandeur Suites · Guest Feedback &amp; Complaint Analytics</span>
          </footer>
        </div>
      </div>`;

    // Move the page's original content into the shell so plain HTML pages
    // only declare their content once.
    const target = layout.querySelector('[data-page-content]');
    originalContent.forEach((node) => target.appendChild(node));
  }

  document.addEventListener('DOMContentLoaded', () => {
    const layout = document.querySelector('[data-layout]');
    if (!layout) return;
    const role = layout.getAttribute('data-layout');
    renderLayout(role);
    UI.initModals();
    UI.initNav();
  });
})();
