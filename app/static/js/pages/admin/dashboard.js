/* Admin dashboard.
   Data sources (all verified in the backend):
     - GET /api/feedback/analytics        → totals, averages, sentiment, distribution
     - GET /api/feedback/analytics/trend  → average rating per period + direction
     - GET /api/complaint-category/analytics → complaints per category
     - GET /api/complaints/list           → status counts (open/resolved/breached)
   Cards and charts render only what these endpoints actually return. */

(function () {
  'use strict';

  const user = Auth.requireRole('admin');
  if (!user) return;

  document.addEventListener('DOMContentLoaded', init);

  async function init() {
    UI.initNav();
    document.getElementById('trend-period').addEventListener('change', loadTrend);
    await Promise.all([loadFeedbackAnalytics(), loadComplaintMetrics(), loadCategoryAnalytics()]);
    loadTrend();
  }

  async function loadFeedbackAnalytics() {
    try {
      const result = await API.feedback.analytics();
      const data = result.data || {};
      renderDistribution(data.rating_distribution || {});
      return data;
    } catch (err) {
      document.getElementById('distribution-chart').innerHTML = UI.errorState(err.message);
      return null;
    }
  }

  async function loadComplaintMetrics() {
    try {
      const [complaintsResult, categoriesResult] = await Promise.all([
        API.complaints.list(),
        API.feedback.analytics()
      ]);
      const complaints = ((complaintsResult.data || {}).complaints) || [];
      const feedbackData = (categoriesResult.data || {});

      const open = complaints.filter((c) => ['New', 'Assigned', 'In Progress'].includes(c.status)).length;
      const resolved = complaints.filter((c) => ['Resolved', 'Closed'].includes(c.status)).length;
      const breached = complaints.filter((c) => c.sla_status === 'Breached' && !['Resolved', 'Closed'].includes(c.status)).length;

      document.getElementById('admin-metrics').setAttribute('aria-busy', 'false');
      document.getElementById('admin-metrics').innerHTML = `
        <div class="stat-card">
          <span class="stat-card__icon stat-card__icon--navy"><i class="fa-solid fa-star"></i></span>
          <div><div class="stat-card__value">${feedbackData.total_feedback ?? 0}</div><div class="stat-card__label">Total feedback</div></div>
        </div>
        <div class="stat-card">
          <span class="stat-card__icon stat-card__icon--gold"><i class="fa-solid fa-award"></i></span>
          <div><div class="stat-card__value">${feedbackData.average_overall_rating ?? 0}</div><div class="stat-card__label">Average rating</div></div>
        </div>
        <div class="stat-card">
          <span class="stat-card__icon stat-card__icon--info"><i class="fa-solid fa-list-check"></i></span>
          <div><div class="stat-card__value">${complaints.length}</div><div class="stat-card__label">Total complaints</div></div>
        </div>
        <div class="stat-card">
          <span class="stat-card__icon stat-card__icon--warning"><i class="fa-solid fa-hourglass-half"></i></span>
          <div><div class="stat-card__value">${open}</div><div class="stat-card__label">Open complaints</div></div>
        </div>
        <div class="stat-card">
          <span class="stat-card__icon stat-card__icon--success"><i class="fa-solid fa-circle-check"></i></span>
          <div><div class="stat-card__value">${resolved}</div><div class="stat-card__label">Resolved complaints</div></div>
        </div>
        <div class="stat-card">
          <span class="stat-card__icon stat-card__icon--danger"><i class="fa-solid fa-triangle-exclamation"></i></span>
          <div><div class="stat-card__value">${breached}</div><div class="stat-card__label">SLA breaches</div></div>
        </div>`;
    } catch (err) {
      UI.showToast(err.message, 'error');
    }
  }

  async function loadCategoryAnalytics() {
    const container = document.getElementById('category-analytics');
    try {
      const result = await API.categories.analytics();
      const data = result.data || {};
      const categories = data.categories || [];

      if (!categories.length) {
        container.innerHTML = UI.emptyState({ icon: 'fa-chart-simple', title: 'No complaint data yet' });
        return;
      }

      const top = categories.slice(0, 6);
      Charts.barChart(container, top.map((c) => ({ label: c.category, value: c.complaints })), { color: '#3B82A0' });

      if (data.most_common_categories && data.most_common_categories.length) {
        container.insertAdjacentHTML('beforeend',
          `<p class="muted" style="font-size:.85rem; margin:8px 0 0">
            Most common: <strong>${data.most_common_categories.map(UI.escapeHtml).join(', ')}</strong>
            (of ${data.total_complaints} total complaints)</p>`);
      }
    } catch (err) {
      container.innerHTML = UI.errorState(err.message, { retry: true });
      container.querySelector('[data-retry]')?.addEventListener('click', loadCategoryAnalytics);
    }
  }

  async function loadTrend() {
    const container = document.getElementById('trend-chart');
    const period = document.getElementById('trend-period').value;
    try {
      container.innerHTML = '<div class="skeleton-block" style="height:200px"></div>';
      const result = await API.feedback.trend(period);
      const data = result.data || {};
      const trend = data.trend || [];

      if (!trend.length) {
        container.innerHTML = UI.emptyState({ icon: 'fa-chart-line', title: 'No trend data yet', message: 'Trends appear once guests submit feedback.' });
        document.getElementById('trend-summary').textContent = '';
        return;
      }

      Charts.lineChart(container, trend.map((point) => ({ label: point.period, value: point.average_rating })));

      const direction = data.trend_direction || 'Stable';
      const icon = direction === 'Improving' ? 'fa-arrow-trend-up text-success'
        : direction === 'Declining' ? 'fa-arrow-trend-down text-danger' : 'fa-arrows-left-right';
      document.getElementById('trend-summary').innerHTML =
        `<i class="fa-solid ${icon}"></i> Trend: <strong>${UI.escapeHtml(direction)}</strong>
         (${data.change >= 0 ? '+' : ''}${UI.escapeHtml(data.change)} rating change over the period)`;
    } catch (err) {
      container.innerHTML = UI.errorState(err.message, { retry: true });
      container.querySelector('[data-retry]')?.addEventListener('click', loadTrend);
    }
  }

  function renderDistribution(distribution) {
    const container = document.getElementById('distribution-chart');
    const order = ['5 Star', '4 Star', '3 Star', '2 Star', '1 Star'];
    const points = order.map((label) => ({ label: label.replace(' Star', '★'), value: distribution[label] || 0 }));
    if (!points.some((p) => p.value > 0)) {
      container.innerHTML = UI.emptyState({ icon: 'fa-star', title: 'No ratings yet', message: 'Distribution appears once feedback arrives.' });
      return;
    }
    Charts.barChart(container, points, { color: '#D4A373' });
  }
})();
