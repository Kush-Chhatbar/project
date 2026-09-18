/* ==========================================================================
   API layer — single entry point for every backend call.
   Response envelope (verified in app/utils/response.py):
     { status, statusCode, message, data }
   All endpoint wrappers below map 1:1 onto the Flask routes.
   ========================================================================== */

(function () {
  'use strict';

  const { API_BASE_URL, STORAGE_KEYS } = window.APP_CONFIG;

  class ApiError extends Error {
    constructor(message, statusCode, data) {
      super(message);
      this.name = 'ApiError';
      this.statusCode = statusCode;
      this.data = data || null;
    }
  }

  /**
   * Core request helper.
   * @param {string} endpoint path beginning with "/api/..."
   * @param {object} options  fetch options (method, body, params, headers)
   */
  async function apiRequest(endpoint, options = {}) {
    const token = localStorage.getItem(STORAGE_KEYS.token);
    const method = (options.method || 'GET').toUpperCase();

    const headers = { 'Accept': 'application/json', ...(options.headers || {}) };
    if (options.body !== undefined) headers['Content-Type'] = 'application/json';
    if (token) headers['Authorization'] = `Bearer ${token}`;

    let url = `${API_BASE_URL}${endpoint}`;
    if (options.params) {
      const qs = new URLSearchParams();
      Object.entries(options.params).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') qs.append(key, value);
      });
      const query = qs.toString();
      if (query) url += `?${query}`;
    }

    let response;
    try {
      response = await fetch(url, {
        method,
        headers,
        body: options.body !== undefined ? JSON.stringify(options.body) : undefined
      });
    } catch (networkErr) {
      // fetch() rejects on DNS/socket/CORS-blocked failures
      throw new ApiError(
        'Unable to reach the server. Check your connection and try again.',
        0,
        null
      );
    }

    let payload = {};
    try { payload = await response.json(); } catch (e) { payload = {}; }

    if (response.status === 401) {
      // Token missing, expired, or revoked (blocklist) — end the session.
      if (window.Auth) window.Auth.handleSessionExpiry();
      throw new ApiError(
        (payload && payload.message) || 'Your session has expired. Please sign in again.',
        401,
        payload
      );
    }

    if (!response.ok) {
      const message =
        (payload && payload.message) ||
        DEFAULT_MESSAGES[response.status] ||
        'Something went wrong. Please try again.';
      throw new ApiError(message, response.status, payload);
    }

    return payload;
  }

  const DEFAULT_MESSAGES = {
    400: 'The request was invalid.',
    403: 'You do not have permission to perform this action.',
    404: 'The requested resource was not found.',
    422: 'The submitted data could not be processed.',
    500: 'A server error occurred. Please try again later.'
  };

  /* ------------------------------------------------------------------
     Auth
     POST /api/auth/login          staff & admin login
     POST /api/guest/login         guest login (email + stay_id + password)
     GET  /api/auth/me             current staff/admin user
     POST /api/auth/logout         revoke current token (blocklist)
  ------------------------------------------------------------------ */
  const AuthAPI = {
    staffLogin: (email, password) =>
      apiRequest('/api/auth/login', { method: 'POST', body: { email, password } }),

    guestLogin: (email, stayId, password) =>
      apiRequest('/api/guest/login', {
        method: 'POST',
        body: { email: email.trim().toLowerCase(), stay_id: String(stayId).trim(), password }
      }),

    me: () => apiRequest('/api/auth/me'),

    logout: () => apiRequest('/api/auth/logout', { method: 'POST' })
  };

  /* ------------------------------------------------------------------
     Feedback
     POST /api/feedback/add
     GET  /api/feedback/list?rating_range&from_date&to_date
     GET  /api/feedback/show?feedback_id
     GET  /api/feedback/analytics            (admin only)
     GET  /api/feedback/analytics/trend      (admin only, ?period=)
  ------------------------------------------------------------------ */
  const FeedbackAPI = {
    add: (body) => apiRequest('/api/feedback/add', { method: 'POST', body }),
    list: (filters = {}) =>
      apiRequest('/api/feedback/list', {
        params: {
          rating_range: filters.rating_range,
          from_date: filters.from_date,
          to_date: filters.to_date
        }
      }),
    show: (feedbackId) => apiRequest('/api/feedback/show', { params: { feedback_id: feedbackId } }),
    analytics: () => apiRequest('/api/feedback/analytics'),
    trend: (period = 'monthly') => apiRequest('/api/feedback/analytics/trend', { params: { period } })
  };

  /* ------------------------------------------------------------------
     Complaints
     POST /api/complaints/add
     GET  /api/complaints/list?status&priority&category_name&department&from_date&to_date
     GET  /api/complaints/show?complaint_id
     PATCH /api/complaints/update?complaint_id
     PUT  /api/complaints/assign?complaint_id      (admin)
     PUT  /api/complaints/update-status?complaint_id (admin, staff)
     PUT  /api/complaints/resolution-note?complaint_id (admin, staff)
  ------------------------------------------------------------------ */
  const ComplaintsAPI = {
    add: (body) => apiRequest('/api/complaints/add', { method: 'POST', body }),
    list: (filters = {}) =>
      apiRequest('/api/complaints/list', {
        params: {
          status: filters.status,
          priority: filters.priority,
          category_name: filters.category_name,
          department: filters.department,
          from_date: filters.from_date,
          to_date: filters.to_date
        }
      }),
    show: (complaintId) => apiRequest('/api/complaints/show', { params: { complaint_id: complaintId } }),
    update: (complaintId, body) =>
      apiRequest('/api/complaints/update', { method: 'PATCH', params: { complaint_id: complaintId }, body }),
    assign: (complaintId, body) =>
      apiRequest('/api/complaints/assign', { method: 'PUT', params: { complaint_id: complaintId }, body }),
    updateStatus: (complaintId, status) =>
      apiRequest('/api/complaints/update-status', {
        method: 'PUT',
        params: { complaint_id: complaintId },
        body: { status }
      }),
    addResolution: (complaintId, resolutionNotes) =>
      apiRequest('/api/complaints/resolution-note', {
        method: 'PUT',
        params: { complaint_id: complaintId },
        body: { resolution_notes: resolutionNotes }
      })
  };

  /* ------------------------------------------------------------------
     Reference data
     GET /api/departments/list
     GET /api/complaint-category/list
     GET /api/complaint-category/show?complaint_category_id
     GET /api/departments/analytics            (admin)
     GET /api/complaint-category/analytics     (admin)
  ------------------------------------------------------------------ */
  const DepartmentsAPI = {
    list: () => apiRequest('/api/departments/list'),
    show: (id) => apiRequest('/api/departments/show', { params: { department_id: id } }),
    analytics: () => apiRequest('/api/departments/analytics')
  };

  const CategoriesAPI = {
    list: () => apiRequest('/api/complaint-category/list'),
    show: (id) => apiRequest('/api/complaint-category/show', { params: { complaint_category_id: id } }),
    analytics: () => apiRequest('/api/complaint-category/analytics')
  };

  window.API = {
    ApiError,
    apiRequest,
    auth: AuthAPI,
    feedback: FeedbackAPI,
    complaints: ComplaintsAPI,
    departments: DepartmentsAPI,
    categories: CategoriesAPI
  };
})();
