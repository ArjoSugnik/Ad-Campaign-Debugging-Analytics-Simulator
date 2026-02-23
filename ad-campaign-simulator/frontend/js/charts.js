/**
 * ============================================================
 *  charts.js - Dashboard Charts & Visualizations
 * ============================================================
 *  Uses Chart.js (loaded from CDN) to create beautiful charts.
 *
 *  Chart instances are stored globally so they can be
 *  destroyed and re-created when data updates.
 */

// Store chart instances so we can destroy them before re-creating
let healthPieChart = null;
let metricsBarChart = null;
let ctrChart = null;
let convChart = null;
let budgetChart = null;

// Consistent colors for our dark theme
const CHART_COLORS = {
  healthy: '#3fb950',
  warning: '#d29922',
  critical: '#f85149',
  blue: '#58a6ff',
  purple: '#bc8cff',
  teal: '#39d353',
  grid: 'rgba(255,255,255,0.06)',
  text: '#8b949e',
};

// Helper: destroy chart if it exists
function destroyChart(chart) {
  if (chart) {
    chart.destroy();
  }
  return null;
}


/**
 * Renders the Health Distribution Pie Chart on the Dashboard
 * Shows breakdown of Healthy / Warning / Critical campaigns
 */
function renderHealthPieChart(healthyCount, warningCount, criticalCount) {
  healthPieChart = destroyChart(healthPieChart);

  const ctx = document.getElementById('healthPieChart')?.getContext('2d');
  if (!ctx) return;

  healthPieChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Healthy', 'Warning', 'Critical'],
      datasets: [{
        data: [healthyCount, warningCount, criticalCount],
        backgroundColor: [
          CHART_COLORS.healthy,
          CHART_COLORS.warning,
          CHART_COLORS.critical,
        ],
        borderColor: '#161b22',
        borderWidth: 3,
        hoverBorderWidth: 0,
      }]
    },
    options: {
      responsive: true,
      cutout: '65%',
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            color: CHART_COLORS.text,
            padding: 16,
            font: { size: 12 }
          }
        },
        tooltip: {
          callbacks: {
            label: (ctx) => ` ${ctx.label}: ${ctx.parsed} campaign(s)`
          }
        }
      }
    }
  });
}


/**
 * Renders the Metrics Benchmark Bar Chart on Dashboard
 * Compares average CTR, CPC, Conversion Rate vs benchmarks
 */
function renderMetricsBarChart(avgCtr, avgCpc, avgConvRate) {
  metricsBarChart = destroyChart(metricsBarChart);

  const ctx = document.getElementById('metricsBarChart')?.getContext('2d');
  if (!ctx) return;

  metricsBarChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['CTR (%)', 'Conv. Rate (%)'],
      datasets: [
        {
          label: 'Your Average',
          data: [avgCtr, avgConvRate],
          backgroundColor: CHART_COLORS.blue,
          borderRadius: 6,
        },
        {
          label: 'Industry Benchmark',
          data: [2.0, 3.0],  // Industry standard benchmarks
          backgroundColor: CHART_COLORS.purple,
          borderRadius: 6,
        }
      ]
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          labels: { color: CHART_COLORS.text, font: { size: 11 } }
        },
        tooltip: {
          callbacks: {
            label: (ctx) => ` ${ctx.dataset.label}: ${ctx.parsed.y}%`
          }
        }
      },
      scales: {
        x: {
          grid: { color: CHART_COLORS.grid },
          ticks: { color: CHART_COLORS.text }
        },
        y: {
          grid: { color: CHART_COLORS.grid },
          ticks: { color: CHART_COLORS.text },
          beginAtZero: true,
        }
      }
    }
  });
}


/**
 * Renders CTR by Campaign horizontal bar chart (Analytics tab)
 */
function renderCtrChart(campaigns) {
  ctrChart = destroyChart(ctrChart);

  const ctx = document.getElementById('ctrChart')?.getContext('2d');
  if (!ctx) return;

  const labels = campaigns.map(c => truncate(c.name, 20));
  const values = campaigns.map(c => c.ctr || 0);
  const colors = values.map(v => v >= 2 ? CHART_COLORS.healthy : v >= 1 ? CHART_COLORS.warning : CHART_COLORS.critical);

  ctrChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'CTR (%)',
        data: values,
        backgroundColor: colors,
        borderRadius: 4,
      }]
    },
    options: {
      indexAxis: 'y',  // Horizontal bars
      responsive: true,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => ` CTR: ${ctx.parsed.x}%`
          }
        }
      },
      scales: {
        x: {
          grid: { color: CHART_COLORS.grid },
          ticks: { color: CHART_COLORS.text },
          beginAtZero: true,
        },
        y: {
          grid: { color: CHART_COLORS.grid },
          ticks: { color: CHART_COLORS.text, font: { size: 11 } }
        }
      }
    }
  });
}


/**
 * Renders Conversion Rate by Campaign chart (Analytics tab)
 */
function renderConvChart(campaigns) {
  convChart = destroyChart(convChart);

  const ctx = document.getElementById('convChart')?.getContext('2d');
  if (!ctx) return;

  const labels = campaigns.map(c => truncate(c.name, 20));
  const values = campaigns.map(c => c.conversion_rate || 0);
  const colors = values.map(v => v >= 3 ? CHART_COLORS.healthy : v >= 1.5 ? CHART_COLORS.warning : CHART_COLORS.critical);

  convChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Conversion Rate (%)',
        data: values,
        backgroundColor: colors,
        borderRadius: 4,
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => ` Conv. Rate: ${ctx.parsed.x}%`
          }
        }
      },
      scales: {
        x: {
          grid: { color: CHART_COLORS.grid },
          ticks: { color: CHART_COLORS.text },
          beginAtZero: true,
        },
        y: {
          grid: { color: CHART_COLORS.grid },
          ticks: { color: CHART_COLORS.text, font: { size: 11 } }
        }
      }
    }
  });
}


/**
 * Renders Budget vs Clicks scatter/bubble chart (Analytics tab)
 */
function renderBudgetChart(campaigns) {
  budgetChart = destroyChart(budgetChart);

  const ctx = document.getElementById('budgetChart')?.getContext('2d');
  if (!ctx) return;

  const labels = campaigns.map(c => truncate(c.name, 20));

  budgetChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [
        {
          label: 'Budget ($)',
          data: campaigns.map(c => c.budget || 0),
          backgroundColor: CHART_COLORS.blue + '88',
          borderColor: CHART_COLORS.blue,
          borderWidth: 1,
          borderRadius: 4,
          yAxisID: 'y',
        },
        {
          label: 'Clicks',
          data: campaigns.map(c => c.clicks || 0),
          type: 'line',
          borderColor: CHART_COLORS.teal,
          backgroundColor: CHART_COLORS.teal + '22',
          borderWidth: 2,
          pointBackgroundColor: CHART_COLORS.teal,
          pointRadius: 5,
          fill: false,
          yAxisID: 'y1',
        }
      ]
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          labels: { color: CHART_COLORS.text, font: { size: 11 } }
        }
      },
      scales: {
        x: {
          grid: { color: CHART_COLORS.grid },
          ticks: { color: CHART_COLORS.text, font: { size: 10 } }
        },
        y: {
          type: 'linear',
          position: 'left',
          grid: { color: CHART_COLORS.grid },
          ticks: {
            color: CHART_COLORS.blue,
            callback: v => `$${v.toLocaleString()}`
          }
        },
        y1: {
          type: 'linear',
          position: 'right',
          grid: { drawOnChartArea: false },
          ticks: {
            color: CHART_COLORS.teal,
            callback: v => v.toLocaleString()
          }
        }
      }
    }
  });
}


// Utility: truncate long strings for chart labels
function truncate(str, max) {
  return str.length > max ? str.substring(0, max) + '...' : str;
}
