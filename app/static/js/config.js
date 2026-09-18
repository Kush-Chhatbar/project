/* ==========================================================================
   Hotel Feedback System — Frontend configuration
   --------------------------------------------------------------------------
   Environment-appropriate API base URL:
     - Same-origin (Flask serves this UI) by default.
     - Override with window.__API_BASE_URL__ or a <meta name="api-base-url">
       tag when the UI is hosted separately from the Flask API (CORS must be
       configured on the backend in that case).
   ========================================================================== */

(function () {
  'use strict';

  function resolveBaseUrl() {
    if (window.__API_BASE_URL__) return window.__API_BASE_URL__;
    const meta = document.querySelector('meta[name="api-base-url"]');
    if (meta && meta.content) return meta.content.replace(/\/+$/, '');
    return window.location.origin;
  }

  const API_BASE_URL = resolveBaseUrl();

  const STORAGE_KEYS = {
    token: 'hfc_access_token',
    user: 'hfc_current_user'
  };

  /* Domain constants — mirrored from the Flask backend, verified in
     app/services/complaint_service.py and app/services/auth_service.py. */
  const COMPLAINT_STATUSES = ['New', 'Assigned', 'In Progress', 'Resolved', 'Closed'];

  const COMPLAINT_PRIORITIES = ['Critical', 'High', 'Medium', 'Low'];

  /* Backend-enforced status transitions (PUT /api/complaints/update-status):
     Assigned -> In Progress -> Resolved -> Closed. Resolving requires
     resolution notes to be saved first. */
  const STATUS_TRANSITIONS = {
    'Assigned': ['In Progress'],
    'In Progress': ['Resolved'],
    'Resolved': ['Closed'],
    'Closed': []
  };

  window.APP_CONFIG = {
    API_BASE_URL,
    STORAGE_KEYS,
    COMPLAINT_STATUSES,
    COMPLAINT_PRIORITIES,
    STATUS_TRANSITIONS
  };
})();
