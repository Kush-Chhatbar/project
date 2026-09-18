/* Guest complaint submission — POST /api/complaints/add.
   Contract verified in app/services/complaint_service.py:
     - Requires: category_id (active category), description.
     - priority optional, defaults to "Medium"; allowed: Critical|High|Medium|Low.
     - Guest & stay identity come from the JWT claims (not sent).
     - Complaint number and SLA due date are generated server-side.
   The list endpoint (/api/complaints/list) is scoped to the logged-in guest,
   which is how "My Complaints" works without a guest-specific endpoint. */

(function () {
  'use strict';

  const user = Auth.requireRole('guest');
  if (!user) return;

  let submitting = false; // duplicate-submission guard

  document.addEventListener('DOMContentLoaded', init);

  async function init() {
    UI.initNav();

    if (user.stay) {
      const banner = document.getElementById('stay-banner');
      banner.hidden = false;
      banner.querySelector('span').textContent =
        `Stay ${user.stay.stay_id} · Room ${user.stay.room_number} — your complaint will reference this stay.`;
    }

    await loadCategories();

    const form = document.getElementById('complaint-form');
    const categorySelect = document.getElementById('category');
    const description = document.getElementById('description');

    categorySelect.addEventListener('change', () => UI.setFieldError(categorySelect, null));
    description.addEventListener('input', () => UI.setFieldError(description, null));

    form.addEventListener('submit', submitComplaint);
  }

  async function loadCategories() {
    const select = document.getElementById('category');
    try {
      const result = await API.categories.list();
      const categories = ((result.data || {}).complaint_categories || []).filter((c) => c.is_active);
      if (!categories.length) {
        select.innerHTML = '<option value="">No categories available</option>';
        UI.showToast('No complaint categories are available. Please contact the front desk.', 'warning');
        return;
      }
      select.innerHTML = '<option value="">Select a category…</option>' + categories.map((category) =>
        `<option value="${category.id}">${UI.escapeHtml(category.name)}</option>`).join('');
    } catch (err) {
      select.innerHTML = '<option value="">Unable to load categories</option>';
      UI.showToast(err.message, 'error');
    }
  }

  function validate() {
    let valid = true;
    const categorySelect = document.getElementById('category');
    const description = document.getElementById('description');

    if (!categorySelect.value) {
      UI.setFieldError(categorySelect, 'Please choose a complaint category.');
      valid = false;
    }
    if (!description.value.trim()) {
      UI.setFieldError(description, 'Please describe the issue.');
      valid = false;
    } else if (description.value.trim().length < 10) {
      UI.setFieldError(description, 'Description must be at least 10 characters.');
      valid = false;
    }
    return valid;
  }

  async function submitComplaint(event) {
    event.preventDefault();
    if (submitting) return; // prevent double POST while request in flight
    const form = event.currentTarget;
    UI.clearFormErrors(form);
    if (!validate()) return;

    submitting = true;
    const submitButton = form.querySelector('button[type="submit"]');
    const restore = UI.setButtonLoading(submitButton, true);

    try {
      const payload = {
        category_id: Number(document.getElementById('category').value),
        priority: document.getElementById('priority').value,
        description: document.getElementById('description').value.trim()
      };
      const result = await API.complaints.add(payload);
      const complaint = ((result.data || {}).complaint) || {};
      UI.showToast(
        `Complaint ${complaint.complaint_number || ''} submitted successfully. Our team has been notified.`,
        'success'
      );
      form.reset();
    } catch (err) {
      UI.showToast(err.message, 'error');
    } finally {
      submitting = false;
      UI.setButtonLoading(submitButton, false);
      restore && restore();
    }
  }
})();
