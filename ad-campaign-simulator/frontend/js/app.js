/**
 * ============================================================
 *  app.js - Main Application Logic
 * ============================================================
 *  This is the main JavaScript file that controls the UI.
 *
 *  STRUCTURE:
 *  1. Tab Navigation
 *  2. Dashboard loading
 *  3. Campaign list rendering
 *  4. Create campaign form
 *  5. Diagnostics panel
 *  6. Analytics charts
 *  7. Utility functions
 */

// ---- GLOBAL STATE ----
let allCampaigns = [];  // Cached campaign list

// ============================================================
// 1. TAB NAVIGATION
// ============================================================

// Wait for page to fully load
document.addEventListener("DOMContentLoaded", () => {
  setupNavigation();
  loadDashboard();
  checkApiConnection();
});

function setupNavigation() {
  const links = document.querySelectorAll(".nav-link");

  links.forEach(link => {
    link.addEventListener("click", (e) => {
      e.preventDefault();

      // Remove active class from all links
      links.forEach(l => l.classList.remove("active"));
      link.classList.add("active");

      // Get which tab to show
      const tabName = link.getAttribute("data-tab");
      showTab(tabName);
    });
  });
}

function showTab(tabName) {
  // Hide all tab contents
  document.querySelectorAll(".tab-content").forEach(tab => {
    tab.classList.remove("active");
  });

  // Show the selected tab
  const tab = document.getElementById(`tab-${tabName}`);
  if (tab) tab.classList.add("active");

  // Update page title
  const titles = {
    dashboard: "Dashboard",
    campaigns: "All Campaigns",
    create: "New Campaign",
    diagnostics: "Diagnostics",
    analytics: "Analytics"
  };
  document.getElementById("page-title").textContent = titles[tabName] || tabName;

  // Load data for that tab
  if (tabName === "dashboard") loadDashboard();
  if (tabName === "campaigns") loadCampaigns();
  if (tabName === "diagnostics") loadDiagnosticsSelector();
  if (tabName === "analytics") loadAnalytics();
}


// ============================================================
// 2. DASHBOARD
// ============================================================

async function loadDashboard() {
  try {
    // Fetch campaigns and insights in parallel
    const [campaignData, insightData] = await Promise.all([
      apiGetCampaigns(),
      apiGetAllInsights()
    ]);

    allCampaigns = campaignData.campaigns;
    const insights = insightData.insights;

    // Count by status
    let healthy = 0, warning = 0, critical = 0;
    insights.forEach(i => {
      if (i.health_score >= 80) healthy++;
      else if (i.health_score >= 50) warning++;
      else critical++;
    });

    // Update stat cards
    document.getElementById("stat-total").textContent = allCampaigns.length;
    document.getElementById("stat-healthy").textContent = healthy;
    document.getElementById("stat-warning").textContent = warning;
    document.getElementById("stat-critical").textContent = critical;

    // Calculate averages for chart
    const avg = (arr, key) => arr.length > 0
      ? (arr.reduce((sum, c) => sum + (c[key] || 0), 0) / arr.length).toFixed(2)
      : 0;

    const avgCtr = avg(allCampaigns, 'ctr');
    const avgCpc = avg(allCampaigns, 'cpc');
    const avgConv = avg(allCampaigns, 'conversion_rate');

    // Render charts
    renderHealthPieChart(healthy, warning, critical);
    renderMetricsBarChart(parseFloat(avgCtr), parseFloat(avgCpc), parseFloat(avgConv));

    // Render issue alerts
    renderIssueAlerts(insights);

  } catch (err) {
    showAlert(`Failed to load dashboard: ${err.message}`, "error");
  }
}

function renderIssueAlerts(insights) {
  const container = document.getElementById("issue-alerts-list");

  // Filter to only campaigns with issues
  const alertCampaigns = insights.filter(i => i.issues_found > 0);

  if (alertCampaigns.length === 0) {
    container.innerHTML = '<p class="empty-state">✅ No active issues detected across all campaigns!</p>';
    return;
  }

  container.innerHTML = alertCampaigns.map(i => {
    const isCritical = i.health_score < 50;
    const icon = isCritical ? '🔴' : '🟡';
    return `
      <div class="alert-item ${isCritical ? 'critical' : 'warning'}">
        <div class="alert-icon">${icon}</div>
        <div class="alert-content">
          <div class="alert-campaign">${escapeHtml(i.campaign_name)}</div>
          <div class="alert-desc">${i.issues_found} issue(s) detected — Top: ${i.top_issue.replace(/_/g, ' ')} — Health: ${i.health_score}/100</div>
        </div>
        <button class="btn btn-info" onclick="viewDiagnostics(${i.campaign_id})">Diagnose →</button>
      </div>
    `;
  }).join('');
}


// ============================================================
// 3. CAMPAIGNS LIST
// ============================================================

async function loadCampaigns() {
  try {
    const data = await apiGetCampaigns();
    allCampaigns = data.campaigns;
    renderCampaignsTable(allCampaigns);
  } catch (err) {
    showAlert(`Failed to load campaigns: ${err.message}`, "error");
  }
}

function renderCampaignsTable(campaigns) {
  const tbody = document.getElementById("campaigns-tbody");

  if (!campaigns || campaigns.length === 0) {
    tbody.innerHTML = `<tr><td colspan="9" class="empty-state">
      No campaigns yet. Click "Load Demo Data" or create one!
    </td></tr>`;
    return;
  }

  tbody.innerHTML = campaigns.map(c => {
    const health = getHealthLabel(c);
    return `
      <tr>
        <td><strong>${escapeHtml(c.name)}</strong></td>
        <td>$${Number(c.budget).toLocaleString()}</td>
        <td>${Number(c.impressions).toLocaleString()}</td>
        <td>${Number(c.clicks).toLocaleString()}</td>
        <td>${formatMetric(c.ctr, '%')}</td>
        <td>${formatMetric(c.cpc, '$', true)}</td>
        <td>${formatMetric(c.conversion_rate, '%')}</td>
        <td><span class="badge badge-${health.class}">${health.label}</span></td>
        <td>
          <button class="btn btn-info" onclick="viewDiagnostics(${c.id})" title="Run Diagnostics">🔍</button>
          <button class="btn btn-outline" onclick="exportReport(${c.id})" title="Export PDF" style="margin-left:4px">📄</button>
          <button class="btn btn-danger" onclick="deleteCampaign(${c.id})" title="Delete" style="margin-left:4px">🗑</button>
        </td>
      </tr>
    `;
  }).join('');
}

async function deleteCampaign(id) {
  if (!confirm("Are you sure you want to delete this campaign?")) return;

  try {
    await apiDeleteCampaign(id);
    showAlert("Campaign deleted successfully.", "success");
    loadCampaigns();
    loadDashboard();
  } catch (err) {
    showAlert(`Delete failed: ${err.message}`, "error");
  }
}

function exportReport(id) {
  apiExportReport(id);
  showAlert("Report download starting...", "success");
}


// ============================================================
// 4. CREATE CAMPAIGN FORM
// ============================================================

// Listen for form submission
document.getElementById("create-campaign-form")?.addEventListener("submit", async (e) => {
  e.preventDefault();
  await submitCampaign();
});

// Live preview of calculated metrics as user types
["camp-impressions", "camp-clicks", "camp-conversions", "camp-budget"].forEach(id => {
  document.getElementById(id)?.addEventListener("input", updatePreview);
});

function updatePreview() {
  const impressions = parseFloat(document.getElementById("camp-impressions").value) || 0;
  const clicks = parseFloat(document.getElementById("camp-clicks").value) || 0;
  const conversions = parseFloat(document.getElementById("camp-conversions").value) || 0;
  const budget = parseFloat(document.getElementById("camp-budget").value) || 0;

  const ctr = impressions > 0 ? ((clicks / impressions) * 100).toFixed(2) : "0.00";
  const cpc = clicks > 0 ? (budget / clicks).toFixed(2) : "0.00";
  const conv = clicks > 0 ? ((conversions / clicks) * 100).toFixed(2) : "0.00";

  document.getElementById("preview-ctr").textContent = `${ctr}%`;
  document.getElementById("preview-cpc").textContent = `$${cpc}`;
  document.getElementById("preview-conv").textContent = `${conv}%`;
}

async function submitCampaign() {
  const data = {
    name: document.getElementById("camp-name").value,
    budget: parseFloat(document.getElementById("camp-budget").value),
    impressions: parseInt(document.getElementById("camp-impressions").value),
    clicks: parseInt(document.getElementById("camp-clicks").value),
    conversions: parseInt(document.getElementById("camp-conversions").value),
  };

  const msgEl = document.getElementById("form-message");

  try {
    const result = await apiCreateCampaign(data);
    msgEl.textContent = `✅ Campaign "${result.campaign.name}" created successfully!`;
    msgEl.className = "form-message success";
    clearForm();

    // Refresh data
    await loadDashboard();
  } catch (err) {
    msgEl.textContent = `❌ Error: ${err.message}`;
    msgEl.className = "form-message error";
  }
}

function clearForm() {
  document.getElementById("create-campaign-form").reset();
  updatePreview();
}


// ============================================================
// 5. DIAGNOSTICS PANEL
// ============================================================

async function loadDiagnosticsSelector() {
  const select = document.getElementById("diagnose-select");
  if (!select) return;

  try {
    const data = await apiGetCampaigns();
    allCampaigns = data.campaigns;

    select.innerHTML = '<option value="">Select a campaign...</option>' +
      allCampaigns.map(c => `<option value="${c.id}">${escapeHtml(c.name)}</option>`).join('');
  } catch (err) {
    console.error("Could not load campaigns for selector");
  }
}

async function runDiagnostics() {
  const id = document.getElementById("diagnose-select").value;
  if (!id) {
    showAlert("Please select a campaign first.", "error");
    return;
  }

  await runDiagnosticsForId(parseInt(id));
}

// Called from campaign table "Diagnose" button
function viewDiagnostics(id) {
  // Switch to diagnostics tab
  document.querySelectorAll(".nav-link").forEach(l => l.classList.remove("active"));
  document.querySelector('[data-tab="diagnostics"]').classList.add("active");
  showTab("diagnostics");

  // Load diagnostics with delay to allow tab to show
  setTimeout(() => runDiagnosticsForId(id), 100);
}

async function runDiagnosticsForId(id) {
  const container = document.getElementById("diagnostics-result");
  container.innerHTML = '<p style="padding:20px;color:#8b949e">🔄 Running diagnostics...</p>';

  try {
    // Update the select dropdown
    const select = document.getElementById("diagnose-select");
    if (select && allCampaigns.length === 0) {
      await loadDiagnosticsSelector();
    }
    if (select) select.value = id;

    const result = await apiDiagnoseCampaign(id);
    renderDiagnosticsResult(result);
  } catch (err) {
    container.innerHTML = `<p class="empty-state" style="color:#f85149">Error: ${err.message}</p>`;
  }
}

function renderDiagnosticsResult(result) {
  const container = document.getElementById("diagnostics-result");

  const score = result.health_score;
  const status = result.status;
  const issues = result.issues || [];
  const recs = result.recommendations || [];

  // Build HTML
  let html = `
    <div class="diag-header">
      <div class="diag-score-row">
        <div class="diag-score-circle ${status}">
          <span class="diag-score-num">${score}</span>
          <span class="diag-score-label">SCORE</span>
        </div>
        <div>
          <div class="diag-campaign-name">${escapeHtml(result.campaign_name)}</div>
          <div class="diag-summary">${result.summary}</div>
        </div>
      </div>

      <!-- Export button -->
      <button class="btn btn-outline" onclick="exportReport(${result.campaign_id})" style="margin-top:10px">
        📄 Export Full Report (PDF)
      </button>
    </div>
  `;

  // Issues section
  html += `<div class="diag-issues-list">`;

  if (issues.length === 0) {
    html += `<p style="padding:20px;color:#3fb950">✅ No issues detected! This campaign is performing well.</p>`;
  } else {
    html += `<p style="padding:16px 0 0;color:#8b949e;font-size:12px">${issues.length} issue(s) detected:</p>`;

    issues.forEach(issue => {
      html += `
        <div class="diag-issue ${issue.severity}">
          <div class="diag-issue-title">${issue.title}</div>
          <div class="diag-issue-desc">${issue.description}</div>

          <div class="diag-sub-title">Root Causes</div>
          <ul class="diag-list">
            ${issue.root_causes.slice(0, 4).map(c => `<li>${c}</li>`).join('')}
          </ul>
        </div>
      `;
    });
  }

  html += `</div>`;

  // Recommendations panel
  if (recs.length > 0) {
    html += `
      <div class="diag-recs-panel">
        <h4>✅ Recommended Actions (${recs.length} total)</h4>
        ${recs.slice(0, 8).map(r => `<div class="diag-rec-item">${r}</div>`).join('')}
      </div>
    `;
  }

  container.innerHTML = html;
}


// ============================================================
// 6. ANALYTICS CHARTS
// ============================================================

async function loadAnalytics() {
  try {
    if (allCampaigns.length === 0) {
      const data = await apiGetCampaigns();
      allCampaigns = data.campaigns;
    }

    if (allCampaigns.length === 0) {
      document.querySelectorAll('.chart-container h3').forEach(el => {
        el.nextElementSibling.style.display = 'none';
      });
      return;
    }

    renderCtrChart(allCampaigns);
    renderConvChart(allCampaigns);
    renderBudgetChart(allCampaigns);

  } catch (err) {
    showAlert(`Failed to load analytics: ${err.message}`, "error");
  }
}


// ============================================================
// 7. UTILITY FUNCTIONS
// ============================================================

/** Load demo/seed data */
async function seedData() {
  try {
    const result = await apiSeedData();
    showAlert(result.message, "success");
    await loadDashboard();
  } catch (err) {
    showAlert(`Seed failed: ${err.message}`, "error");
  }
}

/** Check if backend is running */
async function checkApiConnection() {
  try {
    await fetch("http://localhost:5000/");
    // Connected - status dot is green by default
  } catch (err) {
    document.getElementById("status-indicator").style.background = "#f85149";
    document.querySelector(".status-text").textContent = "API Offline";
    showAlert("⚠️ Backend not connected. Start the Python server: python app.py", "error");
  }
}

/** Show alert banner */
function showAlert(message, type = "success") {
  const banner = document.getElementById("alert-banner");
  banner.textContent = message;
  banner.className = `alert-banner ${type}`;

  // Auto-hide after 5 seconds
  setTimeout(() => {
    banner.className = "alert-banner hidden";
  }, 5000);
}

/** Get health label based on campaign metrics */
function getHealthLabel(campaign) {
  const ctr = campaign.ctr || 0;
  const conv = campaign.conversion_rate || 0;
  const cpc = campaign.cpc || 0;

  const isCritical = ctr < 0.5 || cpc > 10 || conv < 1;
  const isWarning = ctr < 1 || cpc > 5 || conv < 2;

  if (isCritical) return { label: "Critical", class: "critical" };
  if (isWarning) return { label: "Warning", class: "warning" };
  return { label: "Healthy", class: "healthy" };
}

/** Format metric values nicely */
function formatMetric(value, symbol, prefix = false) {
  if (value === null || value === undefined) return '—';
  const formatted = Number(value).toFixed(2);
  return prefix ? `${symbol}${formatted}` : `${formatted}${symbol}`;
}

/** Prevent XSS by escaping HTML characters */
function escapeHtml(str) {
  const div = document.createElement('div');
  div.appendChild(document.createTextNode(str || ''));
  return div.innerHTML;
}

/** Close modal */
function closeModal() {
  document.getElementById("modal-overlay").classList.add("hidden");
}
