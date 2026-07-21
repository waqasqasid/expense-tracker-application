/* Expense Tracker — Chart.js render helpers
   Called from dashboard/reports templates with server-provided JSON data. */

const ET_CHART_COLORS = [
  "#4f46e5", "#7c3aed", "#06b6d4", "#16a34a", "#d97706",
  "#dc2626", "#db2777", "#0ea5e9", "#84cc16", "#f97316",
];

function etIsDark() {
  return document.documentElement.getAttribute("data-bs-theme") === "dark";
}

function etGridColor() {
  return etIsDark() ? "rgba(255,255,255,0.08)" : "rgba(0,0,0,0.06)";
}

function etTextColor() {
  return etIsDark() ? "#9aa0b4" : "#6b7280";
}

/** Pie / doughnut chart for category-wise breakdown */
function renderCategoryPieChart(canvasId, labels, values) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return null;
  if (!labels.length) {
    ctx.parentElement.innerHTML = '<p class="text-muted text-center py-5">No expense data yet — add a transaction to see this chart.</p>';
    return null;
  }
  return new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: labels,
      datasets: [{
        data: values,
        backgroundColor: ET_CHART_COLORS,
        borderWidth: 2,
        borderColor: etIsDark() ? "#171a23" : "#ffffff",
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: "62%",
      plugins: {
        legend: { position: "bottom", labels: { color: etTextColor(), padding: 14, usePointStyle: true } },
      },
    },
  });
}

/** Bar chart comparing monthly income vs expense */
function renderMonthlyBarChart(canvasId, labels, income, expense) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return null;
  return new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        { label: "Income", data: income, backgroundColor: "#16a34a", borderRadius: 6, maxBarThickness: 26 },
        { label: "Expense", data: expense, backgroundColor: "#dc2626", borderRadius: 6, maxBarThickness: 26 },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: "bottom", labels: { color: etTextColor(), usePointStyle: true } },
      },
      scales: {
        x: { grid: { display: false }, ticks: { color: etTextColor() } },
        y: { grid: { color: etGridColor() }, ticks: { color: etTextColor() } },
      },
    },
  });
}

/** Line chart for spending trend over time */
function renderTrendLineChart(canvasId, labels, values) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return null;
  if (!labels.length) {
    ctx.parentElement.innerHTML = '<p class="text-muted text-center py-5">No spending trend data yet.</p>';
    return null;
  }
  const gradient = ctx.getContext("2d").createLinearGradient(0, 0, 0, 260);
  gradient.addColorStop(0, "rgba(79,70,229,0.35)");
  gradient.addColorStop(1, "rgba(79,70,229,0)");

  return new Chart(ctx, {
    type: "line",
    data: {
      labels: labels,
      datasets: [{
        label: "Daily Spending",
        data: values,
        borderColor: "#4f46e5",
        backgroundColor: gradient,
        fill: true,
        tension: 0.35,
        pointRadius: 3,
        pointBackgroundColor: "#4f46e5",
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { display: false }, ticks: { color: etTextColor() } },
        y: { grid: { color: etGridColor() }, ticks: { color: etTextColor() } },
      },
    },
  });
}
