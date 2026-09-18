/* ==========================================================================
   Session & role-based access control (UI level only).
   --------------------------------------------------------------------------
   The Flask backend remains the single source of truth for authentication
   and authorization — every API call sends the JWT and the backend enforces
   roles (app/utils/auth.py role_required). These checks exist purely to
   route users to the right dashboard and keep them out of pages their role
   does not use.
   ========================================================================== */

(function () {
  'use strict';

  const { STORAGE_KEYS } = window.APP_CONFIG;

  /* JWT access tokens expire after 1 hour (app/config.py
     JWT_ACCESS_TOKEN_EXPIRES). We decode the exp claim to detect expiry
     client-side before the backend rejects the request. */
  function parseJwtPayload(token) {
    try {
      const base64 = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
      return JSON.parse(decodeURIComponent(atob(base64).split('').map((c) => {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
      }).join('')));
    } catch (e) {
      return null;
    }
  }

  function getToken() {
    return localStorage.getItem(STORAGE_KEYS.token);
  }

  function getUser() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEYS.user) || 'null');
    } catch (e) {
      return null;
    }
  }

  function isTokenExpired(token) {
    if (!token) return true;
    const payload = parseJwtPayload(token);
    if (!payload || !payload.exp) return true;
    return Date.now() >= payload.exp * 1000;
  }

  function saveSession(token, user) {
    localStorage.setItem(STORAGE_KEYS.token, token);
    localStorage.setItem(STORAGE_KEYS.user, JSON.stringify(user));
  }

  function clearSession() {
    localStorage.removeItem(STORAGE_KEYS.token);
    localStorage.removeItem(STORAGE_KEYS.user);
  }

  /** Redirect target per role — mirrors the role system in the backend. */
  function dashboardForRole(role) {
    switch (role) {
      case 'guest': return '/guest/dashboard';
      case 'staff': return '/staff/dashboard';
      case 'admin': return '/admin/dashboard';
      default:      return '/login';
    }
  }

  /**
   * Protect a page. Call with the role(s) allowed on this page.
   * Unauthenticated or wrong-role visitors are redirected.
   * @param {string|string[]} allowedRoles
   */
  function requireRole(allowedRoles) {
    const roles = Array.isArray(allowedRoles) ? allowedRoles : [allowedRoles];
    const token = getToken();
    const user = getUser();

    if (!token || !user || isTokenExpired(token)) {
      clearSession();
      window.location.replace('/login?expired=1');
      return null;
    }

    if (!roles.includes(user.role)) {
      // Authenticated but wrong area: send them to their own dashboard.
      window.location.replace(dashboardForRole(user.role));
      return null;
    }

    return user;
  }

  function handleSessionExpiry() {
    if (window.location.pathname === '/login' || window.location.pathname === '/guest/login') return;
    clearSession();
    const isGuestArea = window.location.pathname.startsWith('/guest/');
    window.location.replace(
      (isGuestArea ? '/guest/login' : '/login') + '?expired=1'
    );
  }

  async function logout({ redirectTo = null } = {}) {
    const token = getToken();
    // Best effort: revoke the token server-side (PUT into the blocklist).
    if (token && !isTokenExpired(token) && window.API) {
      try { await window.API.auth.logout(); } catch (e) { /* already invalid */ }
    }
    clearSession();
    window.location.replace(redirectTo || '/login');
  }

  window.Auth = {
    parseJwtPayload,
    getToken,
    getUser,
    isTokenExpired,
    saveSession,
    clearSession,
    dashboardForRole,
    requireRole,
    handleSessionExpiry,
    logout
  };
})();
