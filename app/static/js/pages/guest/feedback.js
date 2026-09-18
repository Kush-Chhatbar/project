/* Guest feedback submission — POST /api/feedback/add.
   Contract verified in app/services/feedback_service.py:
     - Required: cleanliness_rating, staff_rating, food_rating, service_rating
       (numbers, 1.0–5.0, at most one decimal place — enforced client-side).
     - The overall rating is computed server-side; it is NOT sent.
     - Guest & stay identity come from the JWT claims; not sent.
     - Optional: comment, department_feedback: [{department_id, rating, comment}].
   The backend also enforces a daily one-feedback-per-guest rule via a unique
   constraint (duplicate submissions surface the backend error message). */

(function () {
  'use strict';

  const user = Auth.requireRole('guest');
  if (!user) return;

  const RATING_FIELDS = ['cleanliness_rating', 'staff_rating', 'food_rating', 'service_rating'];
  const RATING_LABELS = {
    cleanliness_rating: 'Cleanliness rating',
    staff_rating: 'Staff rating',
    food_rating: 'Food rating',
    service_rating: 'Service rating'
  };
  const HINTS = ['', 'Poor', 'Fair', 'Good', 'Very good', 'Excellent'];

  const values = {};
  const departmentValues = {};

  document.addEventListener('DOMContentLoaded', init);

  async function init() {
    UI.initNav();

    if (user.stay) {
      const banner = document.getElementById('stay-banner');
      banner.hidden = false;
      banner.querySelector('span').textContent =
        `Stay ${user.stay.stay_id} · Room ${user.stay.room_number} (${user.stay.room_type}) — feedback is recorded against this stay.`;
    }

    RATING_FIELDS.forEach(buildStarInput);
    document.getElementById('reset-feedback').addEventListener('click', () => {
      RATING_FIELDS.forEach((field) => setRating(field, 0));
      Object.keys(departmentValues).forEach((id) => { departmentValues[id] = 0; });
      document.querySelectorAll('[data-dept-hint]').forEach((el) => { el.textContent = ''; });
      UI.clearFormErrors(document.getElementById('feedback-form'));
    });

    await loadDepartments();

    const form = document.getElementById('feedback-form');
    form.addEventListener('submit', submitFeedback);
  }

  function buildStarInput(field) {
    const container = document.querySelector(`[data-rating="${field}"]`);
    const hint = document.querySelector(`[data-hint="${field}"]`);
    for (let star = 1; star <= 5; star += 1) {
      const button = document.createElement('button');
      button.type = 'button';
      button.setAttribute('aria-label', `${star} star${star > 1 ? 's' : ''}`);
      button.innerHTML = '<i class="fa-solid fa-star"></i>';
      button.addEventListener('click', () => setRating(field, star));
      button.addEventListener('mouseenter', () => paint(container, star));
      button.addEventListener('mouseleave', () => paint(container, values[field] || 0));
      container.appendChild(button);
    }
    setRating(field, 0);

    function set(fieldValue) {
      values[field] = fieldValue;
      paint(container, fieldValue);
      hint.textContent = fieldValue ? HINTS[fieldValue] : '';
      UI.setFieldError(container, null);
    }
    container.setRating = set;
  }

  function setRating(field, value) {
    const container = document.querySelector(`[data-rating="${field}"]`);
    if (container && container.setRating) container.setRating(value);
  }

  function paint(container, active) {
    container.querySelectorAll('button').forEach((button, index) => {
      button.classList.toggle('is-active', index < active);
    });
  }

  async function loadDepartments() {
    const list = document.getElementById('department-feedback-list');
    try {
      const result = await API.departments.list();
      const departments = ((result.data || {}).departments || []).filter((d) => d.is_active);
      if (!departments.length) {
        list.innerHTML = '<p class="muted">No departments available for individual ratings.</p>';
        return;
      }
      departments.forEach((department) => {
        const row = document.createElement('div');
        row.className = 'form-field';
        row.innerHTML = `
          <label>${UI.escapeHtml(department.name)} <span class="muted">(optional)</span></label>
          <div class="star-rating star-rating--dept" data-dept="${department.id}" style="font-size:1.2rem"></div>
          <p class="star-rating__hint" data-dept-hint="${department.id}"></p>
          <input class="input" type="text" maxlength="120" placeholder="Optional comment for ${UI.escapeHtml(department.name)}"
            data-dept-comment="${department.id}" style="margin-top:6px">`;

        const starsContainer = row.querySelector('.star-rating');
        for (let star = 1; star <= 5; star += 1) {
          const button = document.createElement('button');
          button.type = 'button';
          button.setAttribute('aria-label', `${department.name}: ${star} stars`);
          button.innerHTML = '<i class="fa-solid fa-star"></i>';
          button.addEventListener('click', () => {
            departmentValues[department.id] = star;
            paint(starsContainer, star);
            row.querySelector(`[data-dept-hint="${department.id}"]`).textContent = HINTS[star] || '';
          });
          starsContainer.appendChild(button);
        }
        list.appendChild(row);
      });
    } catch (err) {
      list.innerHTML = `<p class="muted text-warning">Department ratings are unavailable right now (${UI.escapeHtml(err.message)}). You can still submit your overall feedback.</p>`;
    }
  }

  function validate() {
    let valid = true;
    RATING_FIELDS.forEach((field) => {
      const value = values[field];
      if (!value) {
        UI.setFieldError(document.querySelector(`[data-rating="${field}"]`), `${RATING_LABELS[field]} is required.`);
        valid = false;
      }
    });
    return valid;
  }

  async function submitFeedback(event) {
    event.preventDefault();
    const form = event.currentTarget;
    UI.clearFormErrors(form);
    if (!validate()) {
      UI.showToast('Please provide all four ratings before submitting.', 'warning');
      return;
    }

    const payload = {
      cleanliness_rating: values.cleanliness_rating,
      staff_rating: values.staff_rating,
      food_rating: values.food_rating,
      service_rating: values.service_rating
    };

    const comment = document.getElementById('comment').value.trim();
    if (comment) payload.comment = comment;

    const departmentFeedback = [];
    Object.entries(departmentValues).forEach(([departmentId, rating]) => {
      if (!rating) return;
      const commentInput = document.querySelector(`[data-dept-comment="${departmentId}"]`);
      const item = { department_id: Number(departmentId), rating };
      const deptComment = commentInput ? commentInput.value.trim() : '';
      if (deptComment) item.comment = deptComment;
      departmentFeedback.push(item);
    });
    if (departmentFeedback.length) payload.department_feedback = departmentFeedback;

    const submitButton = form.querySelector('button[type="submit"]');
    const restore = UI.setButtonLoading(submitButton, true);
    try {
      const result = await API.feedback.add(payload);
      const feedback = ((result.data || {}).feedback) || {};
      UI.showToast(result.message || 'Feedback submitted successfully. Thank you!', 'success');
      // Show the server-calculated overall rating.
      if (feedback.overall_rating !== undefined) {
        UI.showToast(`Your overall rating: ${feedback.overall_rating} / 5.0`, 'info');
      }
      form.reset();
      RATING_FIELDS.forEach((field) => setRating(field, 0));
      Object.keys(departmentValues).forEach((id) => { departmentValues[id] = 0; });
      document.querySelectorAll('[data-dept-hint]').forEach((el) => { el.textContent = ''; });
      document.querySelectorAll('.star-rating--dept').forEach((container) => paint(container, 0));
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (err) {
      UI.showToast(err.message, 'error');
    } finally {
      UI.setButtonLoading(submitButton, false);
      restore && restore();
    }
  }
})();
