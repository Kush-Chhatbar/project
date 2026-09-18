/* Guest login — POST /api/guest/login (app/routes/guests.py).
   The backend requires email + stay_id + password and issues a JWT whose
   claims carry the guest's stay (stay_id, stay_number) used by feedback and
   complaint creation. Guest login is closed outside an active stay window
   (7 days before check-in until check-out) — those backend messages are
   surfaced verbatim. */

(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', () => {
    const token = Auth.getToken();
    const user = Auth.getUser();
    if (token && user && user.role === 'guest' && !Auth.isTokenExpired(token)) {
      window.location.replace('/guest/dashboard');
      return;
    }

    const params = new URLSearchParams(window.location.search);
    const alertBox = document.getElementById('guest-login-alert');
    const alertText = alertBox.querySelector('span');
    const form = document.getElementById('guest-login-form');
    const emailInput = document.getElementById('email');
    const stayInput = document.getElementById('stay-id');
    const passwordInput = document.getElementById('password');
    const submitButton = form.querySelector('button[type="submit"]');

    if (params.get('expired')) {
      alertBox.hidden = false;
      alertText.textContent = 'Your session has expired. Please sign in again.';
    }

    const toggle = document.getElementById('toggle-password');
    toggle.addEventListener('click', () => {
      const visible = passwordInput.type === 'text';
      passwordInput.type = visible ? 'password' : 'text';
      toggle.innerHTML = visible
        ? '<i class="fa-regular fa-eye"></i>'
        : '<i class="fa-regular fa-eye-slash"></i>';
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

      if (!stayInput.value.trim()) {
        UI.setFieldError(stayInput, 'Stay ID is required.');
        valid = false;
      } else {
        UI.setFieldError(stayInput, null);
      }

      if (!passwordInput.value) {
        UI.setFieldError(passwordInput, 'Password is required.');
        valid = false;
      } else {
        UI.setFieldError(passwordInput, null);
      }
      return valid;
    }

    [emailInput, stayInput, passwordInput].forEach((input) =>
      input.addEventListener('input', () => UI.setFieldError(input, null)));

    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      alertBox.hidden = true;
      if (!validate()) return;

      const restore = UI.setButtonLoading(submitButton, true);
      try {
        const result = await API.auth.guestLogin(
          emailInput.value,
          stayInput.value.trim(),
          passwordInput.value
        );
        const data = result.data || {};
        const guest = data.guest || {};
        const stay = data.stay || {};
        Auth.saveSession(data.access_token, {
          id: guest.id,
          name: guest.name,
          email: guest.email,
          role: 'guest',
          stay: stay
        });
        UI.showToast(`Welcome, ${guest.name || 'guest'}!`, 'success');
        window.location.replace('/guest/dashboard');
      } catch (err) {
        alertBox.hidden = false;
        alertText.textContent = err.message;
        UI.setButtonLoading(submitButton, false);
      }
    });
  });
})();
