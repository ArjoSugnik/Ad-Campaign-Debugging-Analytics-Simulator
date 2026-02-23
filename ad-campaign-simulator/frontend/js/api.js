/**
 * ============================================================
 *  api.js - API Communication Module
 * ============================================================
 *  This file handles ALL communication with the Python backend.
 *
 *  Think of it as the "phone" between the frontend (HTML/CSS)
 *  and the backend (Python/Flask).
 *
 *  We use the modern fetch() API to make HTTP requests.
 *  All functions are async/await (they wait for the server to respond).
 */

const API_BASE = "http://localhost:5000/api";

/**
 * Helper function: Makes an API call and handles errors
 * @param {string} endpoint - e.g., "/campaigns"
 * @param {object} options  - fetch options (method, body, etc.)
 */
async function apiCall(endpoint, options = {}) {
  try {
    const response = await fetch(API_BASE + endpoint, {
      headers: { "Content-Type": "application/json" },
      ...options
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || `HTTP error ${response.status}`);
    }

    return data;

  } catch (err) {
    console.error(`API Error [${endpoint}]:`, err.message);
    throw err;
  }
}

// ---- CAMPAIGN ENDPOINTS ----

/** GET all campaigns */
async function apiGetCampaigns() {
  return apiCall("/campaigns");
}

/** POST create a new campaign */
async function apiCreateCampaign(data) {
  return apiCall("/campaigns", {
    method: "POST",
    body: JSON.stringify(data)
  });
}

/** GET single campaign by ID */
async function apiGetCampaign(id) {
  return apiCall(`/campaigns/${id}`);
}

/** DELETE a campaign */
async function apiDeleteCampaign(id) {
  return apiCall(`/campaigns/${id}`, { method: "DELETE" });
}

// ---- DIAGNOSTICS ENDPOINTS ----

/** GET diagnostic results for a campaign */
async function apiDiagnoseCampaign(id) {
  return apiCall(`/diagnose/${id}`);
}

/** GET insights for ALL campaigns */
async function apiGetAllInsights() {
  return apiCall("/insights");
}

// ---- MISC ENDPOINTS ----

/** POST seed example data */
async function apiSeedData() {
  return apiCall("/seed", { method: "POST" });
}

/** GET export campaign as PDF */
function apiExportReport(id) {
  // This opens a download link directly in the browser
  window.location.href = `${API_BASE}/report/${id}`;
}
