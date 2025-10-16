const API_BASE = "";

function selectTab(targetId) {
  document.querySelectorAll(".tab").forEach((tab) => {
    const active = tab.dataset.target === targetId;
    tab.classList.toggle("active", active);
  });
  document.querySelectorAll(".panel").forEach((panel) => {
    panel.classList.toggle("active", panel.id === targetId);
  });
}

document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", () => selectTab(tab.dataset.target));
});

function formatOutput(data) {
  if (!data) {
    return "No data";
  }
  if (typeof data === "string") {
    return data;
  }
  return JSON.stringify(data, null, 2);
}

async function fetchJson(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Request failed with status ${response.status}`);
  }
  return response.json();
}

// Metrics form handler
const metricsForm = document.getElementById("metrics-form");
metricsForm?.addEventListener("submit", async (event) => {
  event.preventDefault();
  const endpoint = document.getElementById("metrics-endpoint").value;
  const instance = document.getElementById("metrics-instance").value.trim();
  const limit = document.getElementById("metrics-limit").value;
  const params = new URLSearchParams({ limit });
  if (instance) params.set("instance", instance);
  const output = document.getElementById("metrics-output");
  output.textContent = "Loading...";
  try {
    const data = await fetchJson(`/metrics/${endpoint}?${params.toString()}`);
    output.textContent = formatOutput(data);
  } catch (error) {
    output.textContent = `Error: ${error.message}`;
  }
});

// Analysis form handler
const analysisForm = document.getElementById("analysis-form");
analysisForm?.addEventListener("submit", async (event) => {
  event.preventDefault();
  const title = document.getElementById("analysis-title").value.trim();
  const metricsRaw = document.getElementById("analysis-metrics").value.trim();
  const issuesRaw = document.getElementById("analysis-issues").value.trim();
  const output = document.getElementById("analysis-output");
  output.textContent = "Loading...";
  try {
    const metrics = metricsRaw ? JSON.parse(metricsRaw) : [];
    const payload = { title, metrics };
    if (issuesRaw) {
      payload.issues = issuesRaw;
    }
    const data = await fetchJson("/analysis/insights", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    output.textContent = formatOutput(data);
  } catch (error) {
    output.textContent = `Error: ${error.message}`;
  }
});

// Live monitoring form handler
const liveForm = document.getElementById("live-form");
liveForm?.addEventListener("submit", async (event) => {
  event.preventDefault();
  const endpoint = document.getElementById("live-endpoint").value;
  const limit = document.getElementById("live-limit").value;
  const output = document.getElementById("live-output");
  output.textContent = "Loading...";
  try {
    const data = await fetchJson(`/live/${endpoint}?limit=${encodeURIComponent(limit)}`);
    output.textContent = formatOutput(data);
  } catch (error) {
    output.textContent = `Error: ${error.message}`;
  }
});

// Configuration helpers
const configForm = document.getElementById("config-form");
const statusEl = document.getElementById("config-status");

function setStatus(message, type = "info") {
  if (!statusEl) return;
  statusEl.textContent = message;
  statusEl.dataset.type = type;
}

function populateConfigForm(config) {
  if (!configForm || !config) return;
  const entries = {
    ...Object.entries(config.elastic || {}).reduce(
      (acc, [key, value]) => ({ ...acc, [`elastic.${key}`]: value }),
      {}
    ),
    ...Object.entries(config.ollama || {}).reduce(
      (acc, [key, value]) => ({ ...acc, [`ollama.${key}`]: value }),
      {}
    ),
    ...Object.entries(config.sqlserver || {}).reduce(
      (acc, [key, value]) => ({ ...acc, [`sqlserver.${key}`]: value }),
      {}
    ),
  };

  Array.from(configForm.elements).forEach((element) => {
    if (!(element instanceof HTMLInputElement)) return;
    const key = element.name;
    if (!key) return;
    if (element.type === "checkbox") {
      element.checked = Boolean(entries[key]);
    } else if (entries[key] !== undefined && entries[key] !== null) {
      element.value = entries[key];
    } else {
      element.value = "";
    }
  });
}

async function loadConfig() {
  if (!configForm) return;
  setStatus("Loading configuration...");
  try {
    const config = await fetchJson("/config");
    populateConfigForm(config);
    setStatus("Configuration loaded", "success");
  } catch (error) {
    setStatus(`Error loading config: ${error.message}`, "error");
  }
}

function collectFormValues() {
  const data = { elastic: {}, ollama: {}, sqlserver: {} };
  Array.from(configForm.elements).forEach((element) => {
    if (!(element instanceof HTMLInputElement)) return;
    const [section, field] = element.name.split(".");
    if (!section || !field) return;

    if (element.type === "checkbox") {
      data[section][field] = element.checked;
    } else if (element.value.trim() !== "") {
      data[section][field] = element.value.trim();
    }
  });

  return data;
}

configForm?.addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = collectFormValues();
  setStatus("Saving configuration...");
  try {
    const updated = await fetchJson("/config", {
      method: "PUT",
      body: JSON.stringify({
        elastic: payload.elastic,
        ollama: payload.ollama,
        sqlServer: payload.sqlserver,
      }),
    });
    populateConfigForm(updated);
    setStatus("Configuration saved", "success");
  } catch (error) {
    setStatus(`Error saving config: ${error.message}`, "error");
  }
});

const refreshButton = document.getElementById("config-refresh");
refreshButton?.addEventListener("click", loadConfig);

if (configForm) {
  loadConfig();
}
