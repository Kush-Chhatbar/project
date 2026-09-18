/* Staff & Admin login — POST /api/auth/login (app/routes/auth.py).
   The response identifies the role; we route accordingly. The backend is
   the authority on credentials and roles. */

(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', () => {
    // Already signed in? Go straight to the right dashboard.
    const token = Auth.getToken();
    const user = Auth.getUser();
    if (token && user && !Auth.isTokenExpired(token)) {
      window.location.replace(Auth.dashboardForRole(user.role));
      return;
    }

    const params = new URLSearchParams(window.location.search);
    const alertBox = document.getElementById('login-alert');
    const alertText = alertBox.querySelector('span');
    const form = document.getElementById('staff-login-form');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const submitButton = form.querySelector('button[type="submit"]');

    if (params.get('expired')) {
      alertBox.hidden = false;
      alertText.textContent = 'Your session has expired. Please sign in again.';
    }

    // Show / hide password
    const toggle = document.getElementById('toggle-password');
    toggle.addEventListener('click', () => {
      const visible = passwordInput.type === 'text';
      passwordInput.type = visible ? 'password' : 'text';
      toggle.innerHTML = visible
        ? '<i class="fa-regular fa-eye"></i>'
        : '<i class="fa-regular fa-eye-slash"></i>';
      toggle.setAttribute('aria-label', visible ? 'Show password' : 'Hide password');
    });

    const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    function validate() {
      let valid = true;
      if (!emailInput.value.trim()) {
        UI.setFieldError(emailInput, 'Email is required.');
        valid = false;
      } else if (!EMAIL_RE.test(emailInput.value.trim())) {
        UI.setFieldError(emailInput, 'Enter a valid email address.');
        valid = false;
      } else {
        UI.setFieldError(emailInput, null);
      }

      if (!passwordInput.value) {
        UI.setFieldError(passwordInput, 'Password is required.');
        valid = false;
      } else {
        UI.setFieldError(passwordInput, null);
      }
      return valid;
    }

    [emailInput, passwordInput].forEach((input) =>
      input.addEventListener('input', () => UI.setFieldError(input, null)));

    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      alertBox.hidden = true;
      if (!validate()) return;

      const restore = UI.setButtonLoading(submitButton, true);
      try {
        const result = await API.auth.staffLogin(emailInput.value.trim(), passwordInput.value);
        const data = result.data || {};
        const loggedInUser = data.user || {};
        Auth.saveSession(data.access_token, {
          id: loggedInUser.id,
          name: loggedInUser.name,
          email: loggedInUser.email,
          role: loggedInUser.role,
          department: loggedInUser.department
        });
        UI.showToast(`Welcome back, ${loggedInUser.name || 'user'}!`, 'success');
        window.location.replace(Auth.dashboardForRole(loggedInUser.role));
      } catch (err) {
        alertBox.hidden = false;
        alertText.textContent = err.message;
        UI.setButtonLoading(submitButton, false);
      }
    });
  });
})();
