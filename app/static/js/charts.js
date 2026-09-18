/* ==========================================================================
   Lightweight, dependency-free SVG charts for the admin analytics.
   Data comes exclusively from the real analytics endpoints.
   ========================================================================== */

(function () {
  'use strict';

  const NS = 'http://www.w3.org/2000/svg';

  function el(tag, attrs = {}) {
    const node = document.createElementNS(NS, tag);
    Object.entries(attrs).forEach(([key, value]) => node.setAttribute(key, value));
    return node;
  }

  function clear(node) {
    while (node.firstChild) node.removeChild(node.firstChild);
  }

  /**
   * Vertical bar chart for discrete distributions.
   * @param {HTMLElement} container
   * @param {{label: string, value: number}[]} points
   */
  function barChart(container, points, { color = '#3B82A0' } = {}) {
    clear(container);
    const width = Math.max(container.clientWidth || 480, 280);
    const height = 220;
    const padding = { top: 16, right: 12, bottom: 34, left: 34 };

    const svg = el('svg', { viewBox: `0 0 ${width} ${height}`, class: 'chart', role: 'img' });
    const innerW = width - padding.left - padding.right;
    const innerH = height - padding.top - padding.bottom;

    const max = Math.max(1, ...points.map((p) => p.value));
    const step = points.length ? innerW / points.length : innerW;
    const barWidth = Math.min(56, step * 0.6);

    // Y gridlines + labels
    for (let i = 0; i <= 4; i += 1) {
      const y = padding.top + (innerH * i) / 4;
      svg.appendChild(el('line', {
        x1: padding.left, x2: width - padding.right, y1: y, y2: y,
        stroke: '#E5E7EB', 'stroke-width': 1
      }));
      const label = el('text', {
        x: padding.left - 8, y: y + 4, 'text-anchor': 'end',
        'font-size': 10, fill: '#6B7280'
      });
      label.textContent = Math.round((max * (4 - i)) / 4);
      svg.appendChild(label);
    }

    points.forEach((point, index) => {
      const barHeight = (point.value / max) * innerH;
      const x = padding.left + step * index + (step - barWidth) / 2;
      const y = padding.top + innerH - barHeight;

      const bar = el('rect', {
        x, y, width: barWidth, height: Math.max(barHeight, 1),
        rx: 6, fill: color, class: 'chart__bar'
      });
      bar.appendChild(el('title', {})).textContent = `${point.label}: ${point.value}`;
      svg.appendChild(bar);

      const valueLabel = el('text', {
        x: x + barWidth / 2, y: y - 6, 'text-anchor': 'middle',
        'font-size': 10, fill: '#1F2937', 'font-weight': 600
      });
      valueLabel.textContent = point.value;
      svg.appendChild(valueLabel);

      const axisLabel = el('text', {
        x: x + barWidth / 2, y: height - 12, 'text-anchor': 'middle',
        'font-size': 10, fill: '#6B7280'
      });
      axisLabel.textContent = point.label;
      svg.appendChild(axisLabel);
    });

    container.appendChild(svg);
  }

  /**
   * Line chart for rating trends.
   * @param {HTMLElement} container
   * @param {{label: string, value: number}[]} points
   */
  function lineChart(container, points, { color = '#1E3A5F' } = {}) {
    clear(container);
    const width = Math.max(container.clientWidth || 640, 320);
    const height = 240;
    const padding = { top: 18, right: 16, bottom: 34, left: 38 };

    const svg = el('svg', { viewBox: `0 0 ${width} ${height}`, class: 'chart', role: 'img' });
    const innerW = width - padding.left - padding.right;
    const innerH = height - padding.top - padding.bottom;

    const values = points.map((p) => p.value);
    const min = Math.max(0, Math.min(...values, 5) - 0.5);
    const max = Math.min(5, Math.max(...values, 1) + 0.25);
    const span = Math.max(max - min, 0.5);

    // Horizontal gridlines 1..5
    for (let rating = 1; rating <= 5; rating += 1) {
      if (rating < min || rating > max) continue;
      const y = padding.top + innerH - ((rating - min) / span) * innerH;
      svg.appendChild(el('line', {
        x1: padding.left, x2: width - padding.right, y1: y, y2: y,
        stroke: '#E5E7EB', 'stroke-width': 1
      }));
      const label = el('text', {
        x: padding.left - 8, y: y + 4, 'text-anchor': 'end', 'font-size': 10, fill: '#6B7280'
      });
      label.textContent = rating;
      svg.appendChild(label);
    }

    if (points.length === 0) return;

    const xFor = (index) => (points.length === 1
      ? padding.left + innerW / 2
      : padding.left + (innerW * index) / (points.length - 1));
    const yFor = (value) => padding.top + innerH - ((value - min) / span) * innerH;

    const pathD = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${xFor(i).toFixed(1)} ${yFor(p.value).toFixed(1)}`).join(' ');
    svg.appendChild(el('path', { d: pathD, fill: 'none', stroke: color, 'stroke-width': 2.5, 'stroke-linecap': 'round' }));

    // Area fill under the line
    const areaD = `${pathD} L ${xFor(points.length - 1).toFixed(1)} ${padding.top + innerH} L ${xFor(0).toFixed(1)} ${padding.top + innerH} Z`;
    svg.appendChild(el('path', { d: areaD, fill: color, opacity: 0.08 }));

    const step = Math.ceil(points.length / 8);
    points.forEach((point, index) => {
      const cx = xFor(index);
      const cy = yFor(point.value);
      const dot = el('circle', { cx, cy, r: 4, fill: '#FFFFFF', stroke: color, 'stroke-width': 2 });
      dot.appendChild(el('title', {})).textContent = `${point.label}: ${point.value}`;
      svg.appendChild(dot);

      if (index % step === 0 || index === points.length - 1) {
        const label = el('text', {
          x: cx, y: height - 12, 'text-anchor': 'middle', 'font-size': 10, fill: '#6B7280'
        });
        label.textContent = point.label;
        svg.appendChild(label);
      }
    });

    container.appendChild(svg);
  }

  window.Charts = { barChart, lineChart };
})();
