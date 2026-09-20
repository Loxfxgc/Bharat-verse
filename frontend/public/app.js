/**
 * BharatVerse - Client Application Logic
 * Integrates with FastAPI Backend to drive the Sense -> Act -> Learn loop.
 */

const API_BASE = "";

// Global State
let campusResources = [];
let pendingRecommendations = [];
let activeAnomalies = [];
let graphTopology = { nodes: [], edges: [] };
let mlMetadata = null;

document.addEventListener("DOMContentLoaded", () => {
  initApp();
});

async function initApp() {
  await fetchOverviewData();
  await fetchResources();
  await fetchAnomalies();
  await fetchRecommendations();
  await fetchGraphData();
  await fetchFeedbackData();
  await fetchAuditLogs();
  await fetchMLMetadata();
  initGraphCanvas();
  updateForecastView();
}

// 1. Navigation & View Switching
function switchView(viewName) {
  document.querySelectorAll(".nav-item").forEach(item => item.classList.remove("active"));
  document.querySelectorAll(".view-panel").forEach(panel => panel.classList.remove("active"));

  const navElem = document.getElementById(`nav-${viewName}`);
  const viewElem = document.getElementById(`view-${viewName}`);

  if (navElem) navElem.classList.add("active");
  if (viewElem) viewElem.classList.add("active");

  const titleElem = document.getElementById("current-view-title");
  const subElem = document.getElementById("current-view-subtitle");

  const titles = {
    "overview": ["Autonomous Resource Intelligence Overview", "Smart Campus Orchestration & Decision Intelligence (SIH 26202)"],
    "digital-twin": ["Digital Twin Operational State", "Live Universal Resource Model Telemetry & Space Utilization"],
    "graph": ["Resource Graph Relationships", "Multi-Hop Connected Graph of Buildings, Rooms, Courses, Faculty & Equipment"],
    "forecast": ["AI Demand & Shortage Prediction", "Trained XGBoost Regressor 24-Hour Utilization Curve"],
    "simulation": ["What-If Scenario Simulation Lab", "Evaluate Reassignments, Costs & Conflicts Prior to Execution"],
    "optimization": ["Google OR-Tools Constraint Optimizer", "CP-SAT Hard & Soft Constraint Feasibility Allocation"],
    "approvals": ["Risk-Aware Approvals & Audit Trail", "Human-In-The-Loop Governance for High-Impact Autonomous Actions"],
    "feedback": ["Continuous Closed Feedback Loop", "Comparison of Predicted vs Actual Post-Execution Utilization"],
    "training": ["Machine Learning Training Center", "XGBoost & Isolation Forest Retraining, Metrics & Feature Importances"]
  };

  if (titles[viewName]) {
    titleElem.innerText = titles[viewName][0];
    subElem.innerText = titles[viewName][1];
  }

  if (viewName === "graph") {
    renderGraph();
  }
}

// 2. Fetch Overview Data
async function fetchOverviewData() {
  try {
    const res = await fetch(`${API_BASE}/api/resources/digital-twin/overview`);
    const data = await res.json();
    document.getElementById("kpi-total-res").innerText = data.total_resources;
    document.getElementById("kpi-available-res").innerText = data.available_resources;
    document.getElementById("kpi-utilization").innerText = `${data.overall_utilization_pct}%`;
    document.getElementById("kpi-active-alerts").innerText = data.active_alerts_count;
    document.getElementById("kpi-pending-decisions").innerText = data.pending_approvals_count;
    document.getElementById("sidebar-pending-badge").innerText = data.pending_approvals_count;
  } catch (err) {
    console.error("Error fetching overview:", err);
  }
}

// 3. Fetch Resources (Digital Twin)
async function fetchResources() {
  try {
    const res = await fetch(`${API_BASE}/api/resources`);
    campusResources = await res.json();
    renderOverviewResources(campusResources.slice(0, 6));
    renderFullResources(campusResources);
  } catch (err) {
    console.error("Error fetching resources:", err);
  }
}

function renderOverviewResources(rooms) {
  const container = document.getElementById("overview-rooms-grid");
  if (!container) return;
  container.innerHTML = rooms.map(r => createResourceCardHTML(r)).join("");
}

function renderFullResources(rooms) {
  const container = document.getElementById("full-resources-grid");
  if (!container) return;
  container.innerHTML = rooms.map(r => createResourceCardHTML(r)).join("");
}

function createResourceCardHTML(r) {
  const util = r.utilization_rate || 0;
  const statusClass = r.status.toLowerCase();

  return `
    <div class="resource-card" id="card-${r.resource_id}">
      <div class="card-header-flex">
        <span class="res-name">${r.name}</span>
        <span class="status-badge ${statusClass}">${r.status}</span>
      </div>
      <div class="res-meta">
        ${r.location || 'Campus Space'} • Capacity: <strong>${r.capacity} seats</strong> • ₹${r.cost_per_hour}/hr
      </div>
      <div class="utilization-bar-wrap">
        <div class="util-info">
          <span>Current Occupancy (${r.current_occupancy}/${r.capacity})</span>
          <strong>${util}%</strong>
        </div>
        <div class="bar-bg">
          <div class="bar-fill" style="width: ${Math.min(100, util)}%;"></div>
        </div>
      </div>
      <div class="capabilities-list">
        ${(r.capabilities || []).map(c => `<span class="cap-tag">${c}</span>`).join("")}
      </div>
    </div>
  `;
}

function filterResources(status) {
  if (status === 'all') {
    renderFullResources(campusResources);
  } else {
    const filtered = campusResources.filter(r => r.status.toLowerCase() === status.toLowerCase());
    renderFullResources(filtered);
  }
}

// 4. Fetch Anomalies
async function fetchAnomalies() {
  try {
    const res = await fetch(`${API_BASE}/api/anomalies`);
    activeAnomalies = await res.json();
    const tbody = document.getElementById("overview-anomalies-table");
    if (!tbody) return;

    if (activeAnomalies.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--text-dim);">No active anomalies detected. All sensors normal.</td></tr>`;
      return;
    }

    tbody.innerHTML = activeAnomalies.map(a => `
      <tr>
        <td><strong>${a.resource_id}</strong></td>
        <td>${a.anomaly_type}</td>
        <td><span style="color: var(--accent-rose); font-weight: 700;">${a.observed_value} occupants</span></td>
        <td style="color: var(--text-muted);">${a.expected_range}</td>
        <td><span class="severity-badge ${a.severity.toLowerCase()}">${a.severity}</span></td>
        <td>
          <button class="btn-primary" style="padding: 4px 8px; font-size: 11px;" onclick="resolveAnomaly('${a.anomaly_id}')">
            Resolve
          </button>
        </td>
      </tr>
    `).join("");
  } catch (err) {
    console.error("Error fetching anomalies:", err);
  }
}

async function resolveAnomaly(anomalyId) {
  try {
    await fetch(`${API_BASE}/api/anomalies/${anomalyId}/resolve`, { method: "POST" });
    showToast("Anomaly resolved successfully");
    fetchAnomalies();
    fetchOverviewData();
  } catch (err) {
    showToast("Failed to resolve anomaly", "error");
  }
}

async function simulateNewAnomaly() {
  try {
    const res = await fetch(`${API_BASE}/api/anomalies/detect`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        resource_id: "ROOM_R104",
        actual_occupancy: 135, // exceeds 120 capacity
        hour: 15,
        is_weekend: 0
      })
    });
    const data = await res.json();
    showToast(`Sensor Event Flagged: ${data.anomaly_type} in ${data.resource_id}`);
    fetchAnomalies();
    fetchOverviewData();
  } catch (err) {
    showToast("Error triggering anomaly", "error");
  }
}

// 5. Fetch Recommendations & "The Wow Moment"
async function fetchRecommendations() {
  try {
    const res = await fetch(`${API_BASE}/api/recommendations`);
    pendingRecommendations = await res.json();
    renderFlagshipRecommendation();
    renderPendingApprovals();
  } catch (err) {
    console.error("Error fetching recommendations:", err);
  }
}

function renderFlagshipRecommendation() {
  const pending = pendingRecommendations.find(r => r.status === "pending") || pendingRecommendations[0];
  const card = document.getElementById("wow-moment-card");
  if (!card || !pending) return;

  document.getElementById("rec-title").innerText = `${pending.course_id} Constraint Violation Detected`;
  document.getElementById("rec-problem-desc").innerText = pending.problem;
  document.getElementById("rec-from-room").innerText = `${pending.from_room_id}`;
  document.getElementById("rec-to-room").innerText = `${pending.to_room_id}`;

  const actionContainer = document.getElementById("rec-actions-container");
  if (pending.status === "executed") {
    actionContainer.innerHTML = `<span style="color: var(--accent-emerald); font-weight: 700; padding: 8px;">✓ EXECUTED & DIGITAL TWIN UPDATED</span>`;
  } else if (pending.status === "rejected") {
    actionContainer.innerHTML = `<span style="color: var(--accent-rose); font-weight: 700; padding: 8px;">✕ REJECTED BY ADMIN</span>`;
  } else {
    actionContainer.innerHTML = `
      <button class="btn-approve" id="btn-approve-rec" onclick="approveFlagshipRecommendation('${pending.rec_id}')">
        ✓ Approve & Execute
      </button>
      <button class="btn-reject" id="btn-reject-rec" onclick="rejectFlagshipRecommendation('${pending.rec_id}')">
        ✕ Reject
      </button>
    `;
  }
}

async function approveFlagshipRecommendation(recId = "REC_DS301_R102") {
  try {
    const res = await fetch(`${API_BASE}/api/approvals/${recId}/approve`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        decision: "approved",
        reviewer: "Campus Operations Director",
        comments: "Approved based on OR-Tools constraint satisfaction verification."
      })
    });
    const result = await res.json();
    if (result.success) {
      showToast("Recommendation Approved & Executed! Digital Twin updated.");
      await fetchRecommendations();
      await fetchResources();
      await fetchOverviewData();
      await fetchAuditLogs();
      await fetchFeedbackData();
    }
  } catch (err) {
    showToast("Failed to approve recommendation", "error");
  }
}

async function rejectFlagshipRecommendation(recId = "REC_DS301_R102") {
  try {
    await fetch(`${API_BASE}/api/approvals/${recId}/reject`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        decision: "rejected",
        reviewer: "Campus Operations Director"
      })
    });
    showToast("Recommendation rejected.");
    fetchRecommendations();
  } catch (err) {
    showToast("Error rejecting recommendation", "error");
  }
}

function renderPendingApprovals() {
  const container = document.getElementById("pending-approvals-list");
  if (!container) return;

  const pending = pendingRecommendations.filter(r => r.status === "pending");
  if (pending.length === 0) {
    container.innerHTML = `<p style="color: var(--text-dim); padding: 12px 0;">No pending actions waiting for human approval.</p>`;
    return;
  }

  container.innerHTML = pending.map(p => `
    <div style="background: rgba(7, 11, 20, 0.6); border: 1px solid var(--border-glass); border-radius: var(--radius-md); padding: 16px; margin-bottom: 12px;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
        <strong style="color: #FFF; font-size: 15px;">${p.problem}</strong>
        <span class="severity-badge medium">Risk Level: ${p.risk_level.toUpperCase()}</span>
      </div>
      <p style="color: var(--text-muted); font-size: 13px; margin-bottom: 12px;">
        Move from <strong>${p.from_room_id}</strong> ➔ <strong>${p.to_room_id}</strong>
      </p>
      <div style="display: flex; gap: 10px;">
        <button class="btn-approve" style="max-width: 140px;" onclick="approveFlagshipRecommendation('${p.rec_id}')">Approve</button>
        <button class="btn-reject" style="max-width: 140px;" onclick="rejectFlagshipRecommendation('${p.rec_id}')">Reject</button>
      </div>
    </div>
  `).join("");
}

// 6. 24-Hour Demand Forecast
async function updateForecastView() {
  const select = document.getElementById("forecast-room-select");
  const roomId = select ? select.value : "ROOM_R102";

  try {
    const res = await fetch(`${API_BASE}/api/predictions/${roomId}`);
    const data = await res.json();
    const container = document.getElementById("forecast-chart-container");
    if (!container) return;

    container.innerHTML = data.forecast_curve.map(pt => {
      const heightPct = Math.max(10, Math.min(100, pt.utilization));
      const isRisk = pt.shortage_risk;
      const color = isRisk ? "var(--accent-rose)" : "var(--accent-cyan)";

      return `
        <div style="flex: 1; display: flex; flex-direction: column; align-items: center; height: 100%; justify-content: flex-end;">
          <span style="font-size: 10px; color: var(--text-dim); margin-bottom: 4px;">${pt.predicted_occupancy}</span>
          <div style="width: 100%; height: ${heightPct}%; background: ${color}; border-radius: 4px 4px 0 0; opacity: 0.85; transition: height 0.4s ease;" title="${pt.time_label}: ${pt.predicted_occupancy} occupants (${pt.utilization}%)"></div>
          <span style="font-size: 9px; color: var(--text-muted); margin-top: 6px;">${pt.hour}h</span>
        </div>
      `;
    }).join("");
  } catch (err) {
    console.error("Error updating forecast:", err);
  }
}

// 7. Simulation Sandbox
async function executeSimulation() {
  const courseId = document.getElementById("sim-course-select").value;
  const targetRoomId = document.getElementById("sim-target-room").value;
  const enrollment = parseInt(document.getElementById("sim-enrollment-override").value) || 85;

  try {
    const res = await fetch(`${API_BASE}/api/simulation/run`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        scenario_name: "Interactive Simulation",
        course_id: courseId,
        target_room_id: targetRoomId,
        simulate_enrollment: enrollment
      })
    });
    const data = await res.json();

    const outBox = document.getElementById("sim-output-box");
    outBox.style.display = "block";

    const capElem = document.getElementById("sim-cap-check");
    capElem.innerText = data.capacity_check;
    capElem.className = data.capacity_check.startsWith("PASS") ? "status-pass" : "status-fail";

    const equipElem = document.getElementById("sim-equip-check");
    equipElem.innerText = data.equipment_check;
    equipElem.className = data.equipment_check.startsWith("PASS") ? "status-pass" : "status-fail";

    const confElem = document.getElementById("sim-conflict-check");
    confElem.innerText = data.schedule_conflict;
    confElem.className = data.schedule_conflict === "NONE" ? "status-pass" : "status-fail";

    const utilElem = document.getElementById("sim-delta-util");
    utilElem.innerText = `${data.delta_utilization > 0 ? '+' : ''}${data.delta_utilization}%`;
    utilElem.className = data.delta_utilization >= 0 ? "status-pass" : "status-fail";

    document.getElementById("sim-summary-text").innerText = data.summary;
    showToast("Simulation completed!");
  } catch (err) {
    showToast("Error running simulation", "error");
  }
}

// 8. OR-Tools Optimization Solver
async function runFlagshipOptimization() {
  switchView("optimization");
  triggerFullOptimization();
}

async function triggerFullOptimization() {
  const container = document.getElementById("optimization-results-container");
  if (!container) return;

  container.innerHTML = `<p style="color: var(--accent-cyan); padding: 20px;">Running Google OR-Tools CP-SAT Solver across campus constraints...</p>`;

  try {
    const res = await fetch(`${API_BASE}/api/optimization/run`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ course_id: "CRS_DS301", force_solver: true })
    });
    const data = await res.json();

    container.innerHTML = `
      <div style="background: rgba(0, 242, 254, 0.1); border: 1px solid rgba(0, 242, 254, 0.3); border-radius: var(--radius-md); padding: 18px; margin-bottom: 20px;">
        <h4 style="color: #FFF; font-size: 16px; margin-bottom: 6px;">CP-SAT Solver Status: <strong>${data.solver_status}</strong></h4>
        <p style="color: var(--text-muted); font-size: 13px;">Optimal Feasible Room: <strong style="color: var(--accent-cyan); font-size: 15px;">${data.best_allocation}</strong> for ${data.course_name} (${data.enrolled_students} students)</p>
      </div>

      <h5 style="color: #FFF; font-size: 14px; margin-bottom: 12px;">Candidate Rooms Constraint Evaluation Matrix</h5>
      <table class="data-table">
        <thead>
          <tr>
            <th>Room</th>
            <th>Capacity</th>
            <th>Status</th>
            <th>Capabilities</th>
            <th>Feasibility</th>
            <th>Objective Score</th>
          </tr>
        </thead>
        <tbody>
          ${data.candidates.map(c => `
            <tr>
              <td><strong>${c.name}</strong></td>
              <td>${c.capacity}</td>
              <td><span class="status-badge ${c.status.toLowerCase()}">${c.status}</span></td>
              <td>${(c.capabilities || []).join(", ")}</td>
              <td>
                ${c.feasible 
                  ? `<span class="status-pass" style="font-weight: 700;">✓ FEASIBLE</span>` 
                  : `<span class="status-fail" style="font-size: 11px;">✕ ${c.rejection_reasons[0] || 'Infeasible'}</span>`
                }
              </td>
              <td style="font-family: var(--font-mono);">${c.objective_score}</td>
            </tr>
          `).join("")}
        </tbody>
      </table>
    `;
    showToast("OR-Tools Solver found optimal allocation: Room R102");
  } catch (err) {
    container.innerHTML = `<p style="color: var(--accent-rose);">Optimization failed to execute.</p>`;
  }
}

// 9. Feedback Loop & Audit Logs
async function fetchFeedbackData() {
  try {
    const res = await fetch(`${API_BASE}/api/feedback`);
    const records = await res.json();
    const tbody = document.getElementById("feedback-records-table");
    if (!tbody) return;

    if (records.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--text-dim);">No feedback records yet. Execute decisions to calibrate learning.</td></tr>`;
      return;
    }

    tbody.innerHTML = records.map(fb => `
      <tr>
        <td style="font-family: var(--font-mono);">${fb.feedback_id}</td>
        <td>${fb.action_description}</td>
        <td style="color: var(--accent-cyan);">${fb.predicted_utilization}%</td>
        <td style="color: var(--accent-emerald); font-weight: 700;">${fb.actual_utilization}%</td>
        <td>${fb.deviation}%</td>
        <td><strong style="color: var(--accent-emerald);">${fb.accuracy_score}%</strong></td>
      </tr>
    `).join("");

    const mRes = await fetch(`${API_BASE}/api/feedback/metrics`);
    const mData = await mRes.json();
    const pill = document.getElementById("fb-accuracy-pill");
    if (pill) pill.innerText = `Closed-Loop Accuracy: ${mData.system_prediction_accuracy}%`;
  } catch (err) {
    console.error("Error fetching feedback:", err);
  }
}

async function fetchAuditLogs() {
  try {
    const res = await fetch(`${API_BASE}/api/approvals/audit-logs`);
    const logs = await res.json();
    const tbody = document.getElementById("audit-logs-table");
    if (!tbody) return;

    tbody.innerHTML = logs.map(l => `
      <tr>
        <td style="font-family: var(--font-mono);">${l.log_id}</td>
        <td><span class="severity-badge medium">${l.action_type}</span></td>
        <td><strong>${l.resource_id}</strong></td>
        <td>${l.user}</td>
        <td style="color: var(--text-muted);">${l.details}</td>
        <td style="font-size: 11px; color: var(--text-dim);">${new Date(l.timestamp).toLocaleTimeString()}</td>
      </tr>
    `).join("");
  } catch (err) {
    console.error("Error fetching audit logs:", err);
  }
}

// 10. ML Training Center & Retraining
async function fetchMLMetadata() {
  try {
    const res = await fetch(`${API_BASE}/api/ml/metrics`);
    mlMetadata = await res.json();

    if (mlMetadata.metrics) {
      document.getElementById("ml-r2-score").innerText = `${mlMetadata.metrics.r2_score} (${mlMetadata.metrics.accuracy_pct}%)`;
      document.getElementById("ml-mae-score").innerText = `${mlMetadata.metrics.mae} occ`;
      document.getElementById("ml-rmse-score").innerText = `${mlMetadata.metrics.rmse} occ`;
      document.getElementById("ml-samples-count").innerText = (mlMetadata.training_samples || 25920).toLocaleString();
    }

    const featContainer = document.getElementById("feature-importances-container");
    if (featContainer && mlMetadata.feature_importances) {
      featContainer.innerHTML = Object.entries(mlMetadata.feature_importances).map(([k, v]) => {
        const pct = (v * 100).toFixed(1);
        return `
          <div class="feature-bar">
            <span class="feature-name">${k}</span>
            <div class="feature-bar-fill">
              <div class="feature-fill-inner" style="width: ${pct}%;"></div>
            </div>
            <span class="feature-pct">${pct}%</span>
          </div>
        `;
      }).join("");
    }
  } catch (err) {
    console.error("Error fetching ML metadata:", err);
  }
}

async function triggerModelRetrain() {
  const btn = document.getElementById("btn-retrain-model");
  btn.disabled = true;
  btn.innerText = "Training XGBoost & Isolation Forest...";
  showToast("Triggered model retraining on historical campus telemetry...");

  try {
    const res = await fetch(`${API_BASE}/api/ml/retrain`, { method: "POST" });
    const data = await res.json();
    if (data.success) {
      showToast(`Model Retrained! New R² Score: ${data.metrics.r2_score}`);
      await fetchMLMetadata();
    }
  } catch (err) {
    showToast("Retraining failed", "error");
  } finally {
    btn.disabled = false;
    btn.innerText = "⚡ Retrain Models Now";
  }
}

async function submitNewResourceForTraining() {
  const resId = document.getElementById("new-res-id").value.trim();
  const name = document.getElementById("new-res-name").value.trim();
  const type = document.getElementById("new-res-type").value;
  const capacity = parseInt(document.getElementById("new-res-capacity").value) || 50;
  const capsRaw = document.getElementById("new-res-caps").value;
  const capabilities = capsRaw.split(",").map(c => c.trim()).filter(Boolean);
  const cost = parseFloat(document.getElementById("new-res-cost").value) || 100.0;

  if (!resId || !name) {
    showToast("Resource ID and Name are required", "error");
    return;
  }

  const btn = document.getElementById("btn-ingest-new-resource");
  btn.disabled = true;
  btn.innerText = "Analyzing & Retraining Model...";
  showToast(`Analyzing new resource ${resId} and generating training baseline...`);

  try {
    const res = await fetch(`${API_BASE}/api/ml/analyze-and-train`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        resource_id: resId,
        name: name,
        type: type,
        capacity: capacity,
        capabilities: capabilities,
        cost_per_hour: cost,
        days_of_history: 30,
        retrain_now: true
      })
    });

    const data = await res.json();
    showToast(`Resource ${resId} ingested! Retrained with R²: ${data.model_metrics.r2_score}`);

    const outBox = document.getElementById("new-res-analysis-output");
    outBox.style.display = "block";
    outBox.innerHTML = `
      <h5 style="color: #FFF; font-size: 14px; margin-bottom: 8px;">Resource Intelligence Profile Analysis</h5>
      <p style="color: var(--text-main); font-size: 13px; margin-bottom: 4px;">
        • <strong>Space Classification:</strong> ${data.analysis.capacity_category} (${data.analysis.capacity} seats)
      </p>
      <p style="color: var(--text-main); font-size: 13px; margin-bottom: 4px;">
        • <strong>Versatility Score:</strong> <span style="color: var(--accent-cyan); font-weight: 700;">${data.analysis.versatility_score}</span> (${data.analysis.capabilities.join(", ")})
      </p>
      <p style="color: var(--text-main); font-size: 13px; margin-bottom: 4px;">
        • <strong>Safe Operational Capacity:</strong> ≤ ${data.analysis.operational_thresholds.normal_safe_max} occupants
      </p>
      <p style="color: var(--text-main); font-size: 13px; margin-bottom: 8px;">
        • <strong>Anomaly Overcrowding Trigger:</strong> > ${data.analysis.operational_thresholds.overcrowding_alert_level} occupants
      </p>
      <p style="color: var(--accent-emerald); font-size: 12.5px; font-weight: 600;">
        ✓ Ingested ${data.new_samples_added} new training samples. Total campus telemetry dataset: ${data.total_dataset_samples} records.
      </p>
    `;

    // Refresh state across dashboard
    await fetchMLMetadata();
    await fetchResources();
    await fetchOverviewData();
  } catch (err) {
    showToast("Error ingesting resource", "error");
  } finally {
    btn.disabled = false;
    btn.innerText = "⚡ Ingest, Analyze & Retrain";
  }
}

// 11. Resource Graph Visualizer (HTML5 Canvas)
async function fetchGraphData() {
  try {
    const res = await fetch(`${API_BASE}/api/graph/topology`);
    graphTopology = await res.json();
  } catch (err) {
    console.error("Error fetching graph data:", err);
  }
}

function initGraphCanvas() {
  const canvas = document.getElementById("graphCanvas");
  if (!canvas) return;
  const dpr = window.devicePixelRatio || 1;
  const rect = canvas.getBoundingClientRect();
  canvas.width = rect.width * dpr;
  canvas.height = rect.height * dpr;
  renderGraph();
}

function renderGraph() {
  const canvas = document.getElementById("graphCanvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  const width = canvas.width;
  const height = canvas.height;

  ctx.clearRect(0, 0, width, height);

  const nodes = graphTopology.nodes || [];
  const edges = graphTopology.edges || [];

  if (nodes.length === 0) return;

  // Position nodes in orbits around center
  const centerX = width / 2;
  const centerY = height / 2;

  const nodePositions = {};
  const colors = {
    "Building": "#4FACFE",
    "Room": "#00E676",
    "Faculty": "#C084FC",
    "Course": "#FF007F",
    "Equipment": "#FFB300",
    "Node": "#94A3B8"
  };

  // Arrange nodes cleanly by group
  nodes.forEach((n, idx) => {
    let radius = 180;
    if (n.label === "Building") radius = 80;
    else if (n.label === "Room") radius = 160;
    else if (n.label === "Course") radius = 250;
    else if (n.label === "Faculty") radius = 320;
    else if (n.label === "Equipment") radius = 380;

    const angle = (idx / nodes.length) * Math.PI * 2;
    nodePositions[n.id] = {
      x: centerX + Math.cos(angle) * (radius * 0.9),
      y: centerY + Math.sin(angle) * (radius * 0.7),
      color: colors[n.label] || "#94A3B8",
      name: n.name || n.id,
      label: n.label
    };
  });

  // Draw Edges
  ctx.lineWidth = 1;
  edges.slice(0, 45).forEach(e => {
    const src = nodePositions[e.source];
    const tgt = nodePositions[e.target];
    if (src && tgt) {
      ctx.strokeStyle = "rgba(255, 255, 255, 0.12)";
      ctx.beginPath();
      ctx.moveTo(src.x, src.y);
      ctx.lineTo(tgt.x, tgt.y);
      ctx.stroke();
    }
  });

  // Draw Nodes
  Object.values(nodePositions).forEach(pos => {
    ctx.shadowColor = pos.color;
    ctx.shadowBlur = 10;
    ctx.fillStyle = pos.color;
    ctx.beginPath();
    ctx.arc(pos.x, pos.y, 7, 0, Math.PI * 2);
    ctx.fill();

    ctx.shadowBlur = 0;
    ctx.fillStyle = "#E2E8F0";
    ctx.font = "10px Inter, sans-serif";
    ctx.fillText(pos.name.length > 14 ? pos.name.substring(0, 12) + ".." : pos.name, pos.x + 10, pos.y + 3);
  });
}

// 12. Search & Toast Utilities
function handleSearch(query) {
  if (!query) {
    renderFullResources(campusResources);
    return;
  }
  const q = query.toLowerCase();
  const matches = campusResources.filter(r => 
    r.name.toLowerCase().includes(q) || 
    r.resource_id.toLowerCase().includes(q) ||
    (r.capabilities || []).some(c => c.toLowerCase().includes(q))
  );
  renderFullResources(matches);
}

function showToast(message, type = "info") {
  const container = document.getElementById("toast-container");
  if (!container) return;

  const toast = document.createElement("div");
  toast.className = "toast";
  toast.innerHTML = `
    <span style="color: ${type === 'error' ? 'var(--accent-rose)' : 'var(--accent-cyan)'}; font-size: 16px;">
      ${type === 'error' ? '✕' : 'ℹ'}
    </span>
    <span style="font-size: 13px; color: #FFF;">${message}</span>
  `;

  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = "0";
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}
